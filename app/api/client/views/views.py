
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


def generate_client_pdf_core(request, client_id, duration=None):
        start_date = datetime.now().date()
        
        if duration == 'week':
            start_date -= timedelta(days=7)
            pdf_filename = f"week_{client_id}.pdf"
        elif duration == 'month':
            start_date -= timedelta(days=30)
            pdf_filename = f"month_{client_id}.pdf"
        elif duration == 'year':
            start_date -= timedelta(days=365)
            pdf_filename = f"year_{client_id}.pdf"
        else:
            start_date = "2000-01-01"
            pdf_filename = f"{client_id}.pdf"
        
        print(start_date)
        template = "client_report.html"
        media_root = Base.MEDIA_ROOT
        client_directory = os.path.join(media_root, "clients")
        os.makedirs(client_directory, exist_ok=True)
        client = Client.objects.get(id=int(client_id))

        purpose = "credit"  # Purpose set to 'Credit by WashMix'
        
        invoice_list = client.invoice_list.filter(
        purpose=purpose,
        created__gte=start_date
        ).annotate(
            balance=Subquery(
                client.transaction_list.filter(invoice=OuterRef('pk'))
                .values('invoice')
                .annotate(total=Sum('amount'))
                .values('total')[:1]
            )
        )
        context = {"client": client, "invoice_list": invoice_list, "is_pdf": True}
        client_orders = Order.objects.filter(client=client, created__gte=start_date)
        context["client_orders"] = client_orders

        printable_page = render_to_string(template, context)

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_html:
            temp_html.write(printable_page.encode("utf-8"))

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            HTML(string=printable_page).write_pdf(temp_pdf)

        client_id = client.id
        pdf_path = os.path.join(client_directory, pdf_filename)

        shutil.move(temp_pdf.name, pdf_path)
        os.remove(temp_html.name)

        success_message = "PDF generated successfully"
        response_data = {
            'pdf_path': pdf_path,
            'message': success_message
        }
        return JsonResponse(response_data)
    
@csrf_exempt
def generate_client_pdf(request):
        if request.method == "POST":
            client_id = request.POST.get("client_id")
            duration = request.POST.get("duration")
            if client_id:
                return HttpResponse(generate_client_pdf_core(request, client_id, duration))
            else:
                raise HTTPException("Invalid payload")


@csrf_exempt
def get_client_pdf(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        if client_id:
            pdf_path = get_pdf_path(Base.MEDIA_ROOT, client_id)
            
            if os.path.exists(pdf_path) and os.path.isfile(pdf_path) and not os.path.isdir(pdf_path):
                full_pdf_url = request.build_absolute_uri(get_pdf_path(Base.MEDIA_URL, client_id))
            
                response_data = {
                    'pdf_path': full_pdf_url,
                    'message': "PDF fetched successfully"
                }
                return JsonResponse(response_data)
            else:
                response_data = {
                    'error': "PDF does not exist"
                }
                return JsonResponse(response_data, status=404)
        else:
            response_data = {
                'error': "Invalid payload"
            }
            return JsonResponse(response_data, status=400)
    else:
        response_data = {
            'error': "Invalid request method"
        }
        return JsonResponse(response_data, status=405)
    
def get_pdf_path(media_path, client_id):
    media_root = media_path
    client_directory = os.path.join(media_root, "clients")
    pdf_filename = f"{client_id}.pdf"
    pdf_path = os.path.join(client_directory, pdf_filename)
    return pdf_path
