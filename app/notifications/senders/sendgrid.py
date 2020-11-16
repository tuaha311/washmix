from django.conf import settings
from django.template.loader import render_to_string

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import HtmlContent, Mail, To

from notifications.senders.base import Sender


class SendGridSender(Sender):
    def __init__(self):
        self._client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY).client

    def raw_send(
        self, from_email: str, recipient_list: list, subject: str, html_content: str
    ) -> None:
        recipient_list = [To(item) for item in recipient_list]

        mail = Mail(
            from_email=from_email,
            to_emails=recipient_list,
            subject=subject,
            html_content=HtmlContent(html_content),
        )
        request_body = mail.get()

        self._client.mail.send.post(request_body=request_body)

    def send(self, recipient_list: list, event: str, context: dict = None) -> None:
        event_info = settings.EMAIL_EVENT_INFO[event]

        subject = event_info["subject"]
        template_name = event_info["template_name"]
        from_email = event_info.get("from_email", settings.SENDGRID_FROM_EMAIL)

        html_content = render_to_string(template_name, context=context)

        self.raw_send(
            from_email=from_email,
            subject=subject,
            recipient_list=recipient_list,
            html_content=html_content,
        )
