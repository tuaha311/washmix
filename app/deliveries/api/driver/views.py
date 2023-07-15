from datetime import datetime
import json
from django.conf import settings
from django.utils.timezone import localtime, now

from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import default_driver_permissions
from deliveries.api.driver.serializers import DeliverySerializer
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.utils import update_deliveries_to_no_show
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from weasyprint import HTML

from deliveries.models.delivery import Delivery
import tempfile
import os
import shutil
from users.models.employee import Employee
from django.db.models import Q, Min, Max, TimeField
from django.db.models.functions import Cast, ExtractHour, ExtractMinute
from datetime import time

class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = default_driver_permissions
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = (
        "kind",
        "status",
    )

    def get_queryset(self):
        now = localtime()
        employee = self.request.user.employee

        one_week_ago = now - settings.FULL_WEEK_DURATION_TIMEDELTA
        delivery_list = employee.delivery_list.filter(date__gte=one_week_ago)

        return delivery_list

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            status = request.data["status"]
        except:
            status = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.kind == DeliveryKind.PICKUP and status == DeliveryStatus.NO_SHOW:
            print("Marking the Delivery to No Show and Charging client.")
            update_deliveries_to_no_show(instance)

        if request.method == 'PATCH':
            if status == 'in_progress':
                instance.start = now().time()
                instance.save()

            if status == 'completed':
                instance.end = now().time()
                instance.save()

        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

@csrf_exempt
def driver_daily_report(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        date_str = data.get('date')
        employee = data.get('user')
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
        deliveries = Delivery.objects.filter(changed__date=date_obj, employee_id=employee).filter(Q(status="no_show") | Q(status="completed")).exclude(kind="dropoff", status="no_show").order_by('start')
        driver = Employee.objects.get(id=employee)
        # Get the minimum and maximum times from the start and end fields
        start_time = deliveries.aggregate(start_time=Min('start'))['start_time']
        end_time = deliveries.aggregate(end_time=Max('end'))['end_time']

        start_time = start_time
        end_time = end_time

        # Calculate the timedelta between start_time and end_time
        delta = datetime.combine(datetime.min.date(), end_time) - datetime.combine(datetime.min.date(), start_time)

        # Extract hours and minutes from the timedelta
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60

        time_delta = {'hours': hours, 'minutes': minutes}
        report_html = generate_report_html(deliveries, date_obj, driver, time_delta)
        pdf_file = generate_pdf(report_html)


        temp_path = tempfile.mktemp(suffix='.pdf')
        with open(temp_path, 'wb') as f:
            f.write(pdf_file)

        destination_dir = os.path.join('media', 'driver')
        os.makedirs(destination_dir, exist_ok=True)
        pdf_name = f"{date_obj}_driver_{employee}.pdf"
        destination_path = os.path.join(destination_dir, pdf_name)
        shutil.move(temp_path, destination_path)
        response = HttpResponse("Driver daily report generated and saved successfully.")

        path = ("/" + os.path.join("media", "driver") + "/" + pdf_name)
        return JsonResponse({"path":path})

    return HttpResponse("Only POST requests are allowed.")

def generate_report_html(deliveries, date_str, driver, time_delta):
    # Generate HTML content for the report using a template
    context = {'deliveries': deliveries, "driver": driver, "date": date_str, "is_pdf": True, "time_delta": time_delta}
    report_html = render_to_string('driver_daily_report.html', context)
    return report_html

def generate_pdf(html_content):
    # Generate PDF from the provided HTML content using WeasyPrint
    pdf_file = HTML(string=html_content).write_pdf()
    return pdf_file
