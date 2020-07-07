import http
import logging
import os
from datetime import datetime

from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from djoser.email import PasswordResetEmail
from rest_framework.utils import json
from templated_mail.mail import BaseEmailMessage

from ..custom_permission.custom_token_authentication import account_activation_token

logging.basicConfig(level=logging.ERROR, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WMPasswordResetEmail(PasswordResetEmail):
    def get_context_data(self):
        context = super(WMPasswordResetEmail, self).get_context_data()
        context.update({'protocol': 'https'})
        return context


class WMOrderPlacementEmail(BaseEmailMessage):

    def __init__(self, request=None, context=None, template_name=None,
                 **kwargs):
        super(WMOrderPlacementEmail, self).__init__(request=request, context=context, template_name=template_name)
        self.user = kwargs.get('user')
        self.order = kwargs.get('order')
        self.order_items = kwargs.get('order_items')

    def get_context_data(self, **kwargs):
        context = super(WMOrderPlacementEmail, self).get_context_data()
        address1 = self.order.pickup_address
        address2 = self.order.dropoff_address
        pickup_address = '{address_line1}, {city},  {state}, {zip_code}'.format(address_line1=address1.address_line_1,
                                                                                city=address1.city,
                                                                                state=address1.state,
                                                                                zip_code=address1.zip_code)
        dropoff_address = '{address_line1}, {city},  {state}, {zip_code}'.format(address_line1=address2.address_line_1,
                                                                                 city=address2.city,
                                                                                 state=address2.state,
                                                                                 zip_code=address2.zip_code)

        context.update({'user': self.user})
        context.update({'order': self.order})
        context.update({'order_details': self.order_items})
        context.update({'pickup_address': pickup_address})
        context.update({'dropoff_address': dropoff_address})

        return context


def wm_user_confirmation_email(**kwargs):
    """Perform any additional content formatting steps here"""

    user = kwargs.get('user')

    def email_formatter():
        # user.is_active = False
        # user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = account_activation_token.make_token(user)

        message = {
            'to': [{'email': user.email or user.username}],
            'template_id': 'd-3dca30fda91a41fd9d283b4841982d14',
            'email_data': {
                'uid': uid,
                'token': token,
                'url': settings.USER_ACTIVATION_URL.format(**{'uid': uid, 'token': token}),
                'protocol': 'https',
                'site_name': 'washmix',
                'domain': 'example.com',
                'email': user.email or user.email
            }
        }
        return message
    return email_formatter


class WMEmailController(BaseEmailMessage):
    def __init__(self, **kwargs):
        self.email_formatter = kwargs.pop('email_formatter')
        self.request = kwargs.get('request')
        super(WMEmailController, self).__init__(**kwargs)

    def get_context_data(self):
        context = super(WMEmailController, self).get_context_data()
        context.update(self.email_formatter())
        context.update({'protocol': 'https'})
        return context


def wm_order_placement_email(**kwargs):
    user = kwargs.get('user')
    address = kwargs.get('pickup_address')
    pick_from = kwargs.get('pick_from')
    pick_to = kwargs.get('pick_to')

    def order_placement_formatter():
        return {'to': [{'email': user.email, 'name': user.username}],
                'template_id': 'd-c7f0068261504cdfbd89220b0c16ac65',
                'email_data': {
                    'from_date': pick_from.strftime('%A %m/%d'),
                    'from_hour': pick_from.strftime('%l %p'),
                    'to_hour': pick_to.strftime('%l %p'),
                    'pickup_address': address.address_line_1,
                    'email': user.email
                }}
    return order_placement_formatter


def wm_package_purchase_email(**kwargs):
    """
    Email formatter to be used when user purchase a package.
    Expects a card, user and a package_name.
    :param kwargs:
    :return:
    """
    users = kwargs.get('users')
    charge = kwargs.get('charge')
    package_name = kwargs.get('package_name')

    source = charge.source
    purchase_date = datetime.now().strftime('%d/%m/%y')

    def email_formatter():
        to = []
        for user in users:
            to.append({'email': user.email, 'name': user.username})

        return {'to': to,
                'template_id': 'd-180c40861e2049ff983ffaecca4eda49',
                'email_data': {
                    'amount_paid': float(charge.amount / 100),
                    'date': purchase_date,
                    'package_name': package_name,
                    'receipt_number': charge.receipt_number,
                    'payment_method': '%s - %s' % (source.brand, source.last4),
                    'email': user.email

                }}

    return email_formatter


class WMEmailControllerSendGrid(object):
    def __init__(self, **kwargs):
        self.email_formatter = kwargs.get('email_formatter')
        self.header = {
            'authorization': '%s %s' % ('Bearer', os.environ.get('SENDGRID_API_KEY_2')),
            'content-type': "application/json"
        }
        self.payload = self.get_context_data()

    def get_context_data(self):
        email_data = self.email_formatter()

        return {
            "personalizations": [
                {
                    'to': email_data['to'],
                    'dynamic_template_data': email_data['email_data']
                }
            ],
            "from": {
                "email": "washmix@example.com",
                "name": "Washmix"
            },
            "reply_to": {
                "email": "washmix@example.com",
                "name": "Washmix"
            },
            "template_id": email_data['template_id']
        }

    def send_sendgrid_email(self):
        try:
            payload = json.dumps(self.payload)
            conn = http.client.HTTPSConnection("api.sendgrid.com")

            conn.request("POST", "/v3/mail/send", payload, self.header)
            res = conn.getresponse()
            data = res.read()

            print(data.decode("utf-8"))
        except Exception as error:
            logger.warn(
                'Fail to send email with template id {0}, Error Report: {1}'.format(self.payload['template_id'], error)
            )
