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
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if request.method == 'PATCH':
            status = request.data.get('status')
            if status == 'in_progress':
                instance.start = now().time()
                instance.save()
                
            if status == 'completed':
                instance.end = now().time()
                instance.save()
        

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

@csrf_exempt
def driver_daily_report(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        date_str = data.get('date')
        employee = data.get('user')
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
        deliveries = Delivery.objects.filter(changed__date=date_obj, employee_id=employee).order_by('start')
        driver = Employee.objects.get(id=employee)

        report_html = generate_report_html(deliveries, date_obj, driver)
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

def generate_report_html(deliveries, date_str, driver):
    # Generate HTML content for the report using a template
    context = {'deliveries': deliveries, "driver": driver, "date": date_str, "is_pdf": True}
    report_html = render_to_string('driver_daily_report.html', context)
    return report_html

def generate_pdf(html_content):
    # Generate PDF from the provided HTML content using WeasyPrint
    pdf_file = HTML(string=html_content).write_pdf()
    return pdf_file
