import json
import logging

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render

from notifications.tasks import send_sms as Send_SMS
from users.models import Client as clients

from .models import SMSTemplate

logger = logging.getLogger(__name__)


def get_selected_customers(request):
    zip_code_param = request.GET.get("zip_code")
    city_param = request.GET.get("city")
    address_param = request.GET.get("address")
    phone_param = request.GET.get("phone")

    selected = ""
    if zip_code_param:
        defaults = clients.objects.filter(billing_address__zip_code=zip_code_param)
        for default in defaults:
            selected += str(default.id) + ","

    elif city_param:
        defaults = clients.objects.filter(Q(billing_address__address_line_1__contains=city_param))
        for default in defaults:
            selected += str(default.id) + ","
    elif address_param:
        defaults = clients.objects.filter(billing_address__address_line_1=address_param)
        for default in defaults:
            selected += str(default.id) + ","
    elif phone_param:
        default = clients.objects.get(main_phone__number=phone_param)
        selected += str(default.id)
    else:
        selected = None

    return selected


def outbound_sms(request):
    if request.method == "GET":
        selected = get_selected_customers(request)

        customers = clients.objects.all()
        billing_address = [customer.billing_address for customer in customers]

        zips = [address["zip_code"] for address in billing_address if "zip_code" in address and address["zip_code"]]
        addresses = [address["address_line_1"] for address in billing_address if "address_line_1" in address and address["address_line_1"]]
        addresses = list(set(addresses))
        cities = [
            address.split(",")[-1].strip()
            for address in addresses
            if address.split(",")[-1].strip()
        ]

        templates = SMSTemplate.objects.all()
        context = {
            "customers": customers,
            "templates": templates,
            "selected": selected,
            "zips": zips,
            "cities": cities,
        }
        return render(request, "outbound_sms.html", context)


def send_sms(request):
    if request.method == "POST":
        customer_ids_string = request.POST.getlist("customers")
        template_id = request.POST.get("template")

        if not customer_ids_string or not template_id:
            return HttpResponse("Invalid customer IDs or template ID.")

        try:
            template = SMSTemplate.objects.get(pk=template_id)
        except SMSTemplate.DoesNotExist:
            return HttpResponse("Selected template does not exist.")

        customer_ids = json.loads(customer_ids_string[0])

        try:
            customer_ids = [int(id) for id in customer_ids]
        except ValueError:
            return HttpResponse("Invalid customer IDs.")

        customers = clients.objects.filter(pk__in=customer_ids)

        for i in range(0, len(customers), 50):
            batch_customers = customers[i:i+50]
            # Prepare recipient list and context
            recipient_list = [customer.main_phone.number for customer in batch_customers if customer.main_phone and customer.main_phone.number]
            event = settings.PROMOTION
            context = {
                "template": template.content,
            }
            # Send SMS using the task function
            Send_SMS.send_with_options(
                kwargs={
                    "event": event,
                    "recipient_list": recipient_list,
                    "extra_context": context,
                },
                delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
            )

        messages.success(request, "SMS send request submitted successfully.")
        return redirect("/admin/sms/outbound-sms")
    else:
        messages.error(request, "Invalid request method.")
        return redirect("/admin/sms/outbound-sms")
