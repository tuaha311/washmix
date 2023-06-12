from django.shortcuts import render, render_to_response
from .models import SMSTemplate
from django.http import HttpResponse
from users.models import Client as clients
import json
import logging
from notifications.tasks import send_sms as Send_SMS
from django.db.models import Q
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext


logger = logging.getLogger(__name__)


def outbound_sms(request):
    if request.method == 'GET':
        zip_code_param = request.GET.get('zip_code')
        city_param = request.GET.get('city')
        address_param = request.GET.get('address')
        phone_param = request.GET.get('phone')
        
        selected = ""
        if zip_code_param:
            defaults = clients.objects.filter(billing_address__zip_code = zip_code_param)
            for default in defaults:
                selected = selected + str(default.id) + ","
                
        elif city_param:
            defaults = clients.objects.filter(Q(billing_address__address_line_1__contains=city_param))
            for default in defaults:
                selected = selected + str(default.id) + ","
        elif address_param:
            defaults = clients.objects.filter(billing_address__address_line_1=address_param)
            for default in defaults:
                selected = selected + str(default.id) + ","
        elif phone_param:
            default = clients.objects.get(main_phone__number=phone_param)
            selected = selected + str(default.id)
        else:
            selected = None
    customers = clients.objects.all()
    billing_address = []
    for customer in customers:
        billing_address.append(customer.billing_address)
    zips = []
    for zip in billing_address:
        if zip['zip_code'] not in zips:
            zips.append(zip['zip_code'])
    addressess = []
    for address in billing_address:
        if address['address_line_1'] not in addressess:
            addressess.append(address['address_line_1'])
    cities = []
    for city in addressess:
        address_components = city.split(',')
        city = address_components[-1].strip()
        if city not in cities:
            cities.append(city)
    
    templates = SMSTemplate.objects.all()
    context = {'customers': customers, 'templates': templates, 'selected': selected, 'zips': zips, 'cities': cities}
    return render(request, 'outbound_sms.html', context)


def send_sms(request):
    if request.method == 'POST':
        customer_ids_string = request.POST.getlist('customers')
        template_id = request.POST.get('template')

        customer_ids = json.loads(customer_ids_string[0])

        customer_ids = [int(id) for id in customer_ids]
        # return HttpResponse() 
        try:
            template = SMSTemplate.objects.get(pk=template_id)
        except SMSTemplate.DoesNotExist:
            return HttpResponse('Selected template does not exist.')

        customers = clients.objects.filter(pk__in=customer_ids)

        for customer in customers:
            # Prepare recipient list and context
            recipient_list = [customer.main_phone.number]
            event = settings.PROMOTION
            template = SMSTemplate.objects.get(pk=template_id)
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

            logger.info(f"Sending SMS to client {customer.email}")

        return HttpResponse('SMS send request submitted successfully.')
    else:
        return HttpResponse('Invalid request method.')
