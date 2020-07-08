import http
import logging
import os

from djoser.email import PasswordResetEmail
from rest_framework.utils import json
from templated_mail.mail import BaseEmailMessage

logging.basicConfig(level=logging.ERROR, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class WMPasswordResetEmail(PasswordResetEmail):
    def get_context_data(self):
        context = super(WMPasswordResetEmail, self).get_context_data()
        context.update({"protocol": "https"})
        return context


class WMOrderPlacementEmail(BaseEmailMessage):
    def __init__(self, request=None, context=None, template_name=None, **kwargs):
        super(WMOrderPlacementEmail, self).__init__(
            request=request, context=context, template_name=template_name
        )
        self.user = kwargs.get("user")
        self.order = kwargs.get("order")
        self.order_items = kwargs.get("order_items")

    def get_context_data(self, **kwargs):
        context = super(WMOrderPlacementEmail, self).get_context_data()
        address1 = self.order.pickup_address
        address2 = self.order.dropoff_address
        pickup_address = "{address_line1}, {city},  {state}, {zip_code}".format(
            address_line1=address1.address_line_1,
            city=address1.city,
            state=address1.state,
            zip_code=address1.zip_code,
        )
        dropoff_address = "{address_line1}, {city},  {state}, {zip_code}".format(
            address_line1=address2.address_line_1,
            city=address2.city,
            state=address2.state,
            zip_code=address2.zip_code,
        )

        context.update({"user": self.user})
        context.update({"order": self.order})
        context.update({"order_details": self.order_items})
        context.update({"pickup_address": pickup_address})
        context.update({"dropoff_address": dropoff_address})

        return context


class EmailController(BaseEmailMessage):
    def __init__(self, **kwargs):
        self.email_formatter = kwargs.pop("email_formatter")
        self.request = kwargs.get("request")
        super(EmailController, self).__init__(**kwargs)

    def get_context_data(self):
        context = super(EmailController, self).get_context_data()
        context.update(self.email_formatter())
        context.update({"protocol": "https"})
        return context


class WMEmailControllerSendGrid(object):
    def __init__(self, **kwargs):
        self.email_formatter = kwargs.get("email_formatter")
        self.header = {
            "authorization": "%s %s" % ("Bearer", os.environ.get("SENDGRID_API_KEY_2")),
            "content-type": "application/json",
        }
        self.payload = self.get_context_data()

    def get_context_data(self):
        email_data = self.email_formatter()

        return {
            "personalizations": [
                {"to": email_data["to"], "dynamic_template_data": email_data["email_data"],}
            ],
            "from": {"email": "washmix@example.com", "name": "Washmix"},
            "reply_to": {"email": "washmix@example.com", "name": "Washmix"},
            "template_id": email_data["template_id"],
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
                "Fail to send email with template id {0}, Error Report: {1}".format(
                    self.payload["template_id"], error
                )
            )
