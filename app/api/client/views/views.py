from http.client import HTTPException
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
import os
import tempfile
import shutil
import settings.base as Base
from django.db.models import Sum, OuterRef, Subquery
from weasyprint import HTML
from orders.models import Order
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import Client
from datetime import datetime, timedelta
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages


def generate_client_pdf_core(request, client_id, duration=None, start_date=None, end_date=None):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)

    start_date, pdf_filename = calculate_start_date_and_filename(client_id, duration, start_date)

    invoice_list, client_orders = get_filtered_data(client, start_date, end_date)

    context = {
        "client": client,
        "invoice_list": invoice_list,
        "is_pdf": True,
        "client_orders": client_orders,
    }

    printable_page = render_to_string("client_report.html", context)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_html:
        temp_html.write(printable_page.encode("utf-8"))

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        HTML(string=printable_page).write_pdf(temp_pdf)
    print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    print(client_id, "client_id")
    print(duration, "duration")
    print(start_date, "start_date")
    print(end_date, "end_date")
    print(pdf_filename, "pdf_filename")
    media_root = Base.MEDIA_ROOT
    client_directory = os.path.join(media_root, "clients")
    os.makedirs(client_directory, exist_ok=True)
    pdf_directory = os.path.join(Base.MEDIA_URL, "clients")
    pdf_path = os.path.join(client_directory, pdf_filename)

    shutil.move(temp_pdf.name, pdf_path)
    os.remove(temp_html.name)
    pdf_path = os.path.join(pdf_directory, pdf_filename)
    success_message = "PDF generated successfully"
    response_data = {"pdf_path": pdf_path, "message": success_message}
    return JsonResponse(response_data)


def calculate_start_date_and_filename(client_id, duration, start_date):
    if not start_date:
        start_date = datetime.now().date()
    else:
        pdf_filename = f"custom_{client_id}.pdf"
        return start_date, pdf_filename

    if duration == "week":
        start_date -= timedelta(days=7)
        pdf_filename = f"week_{client_id}.pdf"
    elif duration == "month":
        start_date -= timedelta(days=30)
        pdf_filename = f"month_{client_id}.pdf"
    elif duration == "year":
        start_date -= timedelta(days=365)
        pdf_filename = f"year_{client_id}.pdf"
    else:
        start_date = "2000-01-01"
        pdf_filename = f"{client_id}.pdf"

    return start_date, pdf_filename


def get_filtered_data(client, start_date, end_date=None):
    purpose = "credit"  # Purpose set to 'Credit by WashMix'

    if end_date:
        print("-------------------HERRE------------------")
        print("-------------------start_date------------------", start_date)
        print("-------------------end_date------------------", end_date)
        invoice_list = client.invoice_list.filter(
            purpose=purpose,
            created__gte=start_date,
            created__lte=end_date,
        ).annotate(
            balance=Subquery(
                client.transaction_list.filter(invoice=OuterRef("pk"))
                .values("invoice")
                .annotate(total=Sum("amount"))
                .values("total")[:1]
            )
        )
        client_orders = Order.objects.filter(
            client=client, created__gte=start_date, created__lte=end_date
        )
    else:
        print("-------------------STILLLL THERRE------------------")
        
        invoice_list = client.invoice_list.filter(
            purpose=purpose,
            created__gte=start_date,
        ).annotate(
            balance=Subquery(
                client.transaction_list.filter(invoice=OuterRef("pk"))
                .values("invoice")
                .annotate(total=Sum("amount"))
                .values("total")[:1]
            )
        )
        client_orders = Order.objects.filter(client=client, created__gte=start_date)

    return invoice_list, client_orders


@csrf_exempt
def generate_client_pdf(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        duration = request.POST.get("duration")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        if client_id:
            return HttpResponse(
                generate_client_pdf_core(
                    request,
                    client_id=client_id,
                    duration=duration,
                    start_date=start_date,
                    end_date=end_date,
                ), messages.success(request, "Client's PDF generated successfully.")
            )
        else:
            messages.error(request, "Client's PDF could not be generated.")
            raise HTTPException("Invalid payload")
        
    if request.method == "GET":
        client_id = request.GET.get("client_id")
        week_pdf_name = f"week_{client_id}.pdf"
        week_pdf_path = os.path.join(settings.MEDIA_URL, "clients", week_pdf_name)
        full_path = os.path.join(settings.MEDIA_ROOT, "clients", week_pdf_name)
        if os.path.exists(full_path):
            week_pdf_path = week_pdf_path
        else:
            week_pdf_path = "-"

        month_pdf_name = f"month_{client_id}.pdf"
        month_pdf_path = os.path.join(settings.MEDIA_URL, "clients", month_pdf_name)
        full_path = os.path.join(settings.MEDIA_ROOT, "clients", month_pdf_name)
        if os.path.exists(full_path):
            month_pdf_path = month_pdf_path
        else:
            month_pdf_path = "-"

        year_pdf_name = f"year_{client_id}.pdf"
        year_pdf_path = os.path.join(settings.MEDIA_URL, "clients", year_pdf_name)
        full_path = os.path.join(settings.MEDIA_ROOT, "clients", year_pdf_name)
        if os.path.exists(full_path):
            year_pdf_path = year_pdf_path
        else:
            year_pdf_path = "-"
            
        all_times_pdf_name = f"{client_id}.pdf"
        all_times_pdf_path = os.path.join(settings.MEDIA_URL, "clients", all_times_pdf_name)
        full_path = os.path.join(settings.MEDIA_ROOT, "clients", all_times_pdf_name)
        if os.path.exists(full_path):
            all_times_pdf_path = all_times_pdf_path
        else:
            all_times_pdf_path = "-"

        context = {
            "client_id": client_id,
            "week_pdf_path": week_pdf_path,
            "month_pdf_path": month_pdf_path,
            "year_pdf_path": year_pdf_path,
            "all_times_pdf_path": all_times_pdf_path,
        }
        return render(request, "generate_client_pdf.html", context)


@csrf_exempt
def get_client_pdf(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        if client_id:
            pdf_path = get_pdf_path(Base.MEDIA_ROOT, client_id)

            if (
                os.path.exists(pdf_path)
                and os.path.isfile(pdf_path)
                and not os.path.isdir(pdf_path)
            ):
                full_pdf_url = request.build_absolute_uri(get_pdf_path(Base.MEDIA_URL, client_id))

                response_data = {"pdf_path": full_pdf_url, "message": "PDF fetched successfully"}
                return JsonResponse(response_data)
            else:
                response_data = {"error": "PDF does not exist"}
                return JsonResponse(response_data, status=404)
        else:
            response_data = {"error": "Invalid payload"}
            return JsonResponse(response_data, status=400)
    else:
        response_data = {"error": "Invalid request method"}
        return JsonResponse(response_data, status=405)


def get_pdf_path(media_path, client_id):
    media_root = media_path
    client_directory = os.path.join(media_root, "clients")
    pdf_filename = f"{client_id}.pdf"
    pdf_path = os.path.join(client_directory, pdf_filename)
    return pdf_path
