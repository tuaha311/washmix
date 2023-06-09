from django.shortcuts import render
from .models import Customer, SMSTemplate
from django.http import HttpResponse
from twilio.rest import Client
from users.models import Client as clients
from django.http import JsonResponse

def outbound_sms(request):
    if request.method == 'GET':
        zip_code_param = request.GET.get('zip_code')
        selected = ""
        if zip_code_param:
            defaults = clients.objects.filter(billing_address__zip_code = zip_code_param)
            for default in defaults:
                selected = selected + str(default.id) + ","
        else:
            selected = None
    print(selected)
    customers = clients.objects.all()
    templates = SMSTemplate.objects.all()
    context = {'customers': customers, 'templates': templates, 'selected': selected}
    return render(request, 'outbound_sms.html', context)


def send_sms(request):
    if request.method == 'POST':
        customer_ids = request.POST.getlist('customers')
        template_id = request.POST.get('template')
        template = SMSTemplate.objects.get(pk=template_id)
        customers = Customer.objects.filter(pk__in=customer_ids)

        # Send SMS using Twilio
        account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
        auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
        client = Client(account_sid, auth_token)

        for customer in customers:
            message = client.messages.create(
                body=template.content.replace('NAME', customer.name),
                from_='+14159939274',  # Your Twilio phone number
                to=customer.phone_number
            )
            print(f"SMS sent to {customer.name} - SID: {message.sid}")

        return HttpResponse('SMS sent successfully.')
    else:
        return HttpResponse('Invalid request method.')