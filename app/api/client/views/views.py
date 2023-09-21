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
from billing.choices import *
from django.db.models import Q



def generate_client_pdf_core(request, client_id, duration=None, start_date=None, end_date=None):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)

    start_date, pdf_filename = calculate_start_date_and_filename(client_id, duration, start_date)

    invoice_list, client_orders = get_filtered_data(client, start_date, end_date)
    chunk_size = 25
    order_chunks = [client_orders[i:i+chunk_size] for i in range(0, len(client_orders), chunk_size)]
    invoice_chunks = [invoice_list[i:i+chunk_size] for i in range(0, len(invoice_list), chunk_size)]
    context = {
        "client": client,
        "invoice_chunks": invoice_chunks,
        "is_pdf": True,
        "order_chunks": order_chunks
    }

    printable_page = render_to_string("client_report.html", context)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_html:
        temp_html.write(printable_page.encode("utf-8"))

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        HTML(string=printable_page).write_pdf(temp_pdf)
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
        datenow = datetime.now()
        start_date = datetime(datenow.year, datenow.month, 1)
        pdf_filename = f"month_{client_id}.pdf"
    elif duration == "year":
        datenow = datetime.now()
        start_date = datetime(datenow.year, 1, 1)
        pdf_filename = f"year_{client_id}.pdf"
    else:
        start_date = "2000-01-01"
        pdf_filename = f"{client_id}.pdf"

    return start_date, pdf_filename


def get_filtered_data(client, start_date, end_date=None):
    purpose = InvoicePurpose.CREDIT  # Purpose set to 'Credit by WashMix'
    if end_date:
        invoice_list = client.invoice_list.filter(
            purpose=purpose,
            created__date__range =[start_date, end_date]
        ).annotate(
            balance=Subquery(
                client.transaction_list.filter(invoice=OuterRef("pk"))
                .values("invoice")
                .annotate(total=Sum("amount"))
                .values("total")[:1]
            )
        )
        client_orders = Order.objects.filter(
            client=client, created__date__range =[start_date, end_date]
        )
    else:
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
        week_pdf_path = get_existing_pdf_path(client_id, "week")
        month_pdf_path = get_existing_pdf_path(client_id, "month")
        year_pdf_path = get_existing_pdf_path(client_id, "year")
        custom_pdf_path = get_existing_pdf_path(client_id, "custom")
        all_times_pdf_path = get_existing_pdf_path(client_id)

        context = {
            "client_id": client_id,
            "week_pdf_path": week_pdf_path,
            "month_pdf_path": month_pdf_path,
            "year_pdf_path": year_pdf_path,
            "all_times_pdf_path": all_times_pdf_path,
            "custom_pdf_path": custom_pdf_path
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
                generate_pdf = generate_client_pdf_core(request, client_id)
                full_pdf_url = request.build_absolute_uri(get_pdf_path(Base.MEDIA_URL, client_id))
                response_data = {"pdf_path": full_pdf_url, "message": "PDF fetched successfully"}
                return JsonResponse(response_data, status=201)
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

def get_existing_pdf_path(client_id, duration=None):
    if duration:
        pdf_name = f"{duration}_{client_id}.pdf"
    else:
        pdf_name = f"{client_id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_URL, "clients", pdf_name)
    full_path = os.path.join(settings.MEDIA_ROOT, "clients", pdf_name)
    if os.path.exists(full_path):
        return pdf_path
    else:
        return "-"
