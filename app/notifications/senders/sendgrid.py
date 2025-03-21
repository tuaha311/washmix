import logging

from django.conf import settings
from django.template.loader import render_to_string

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import HtmlContent, Mail, ReplyTo, To

from notifications.senders.base import Sender

logger = logging.getLogger(__name__)


class SendGridSender(Sender):
    def __init__(self):
        self._client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY).client

    def send(self, recipient_list: list, event: str, context: dict = None, *args, **kwargs) -> None:
        event_info = settings.EMAIL_EVENT_INFO[event]

        subject = event_info["subject"]
        template_name = event_info["template_name"]
        reply_to = event_info.get("reply_to", settings.SENDGRID_NO_REPLY)
        from_email = event_info.get("from_email", settings.SENDGRID_FROM_EMAIL)

        html_content = render_to_string(template_name, context=context)

        self.raw_send(
            from_sender=from_email,
            subject=subject,
            recipient_list=recipient_list,
            body=html_content,
            reply_to=reply_to,
        )

    def raw_send(
        self,
        from_sender: str,
        recipient_list: list,
        subject: str,
        body: str,
        reply_to: str = None,
        *args,
        **kwargs,
    ) -> None:
        recipient_list = [To(item) for item in recipient_list]

        mail = Mail(
            from_email=from_sender,
            to_emails=recipient_list,
            subject=subject,
            html_content=HtmlContent(body),
        )

        if reply_to:
            mail.reply_to = ReplyTo(email=reply_to)

        request_body = mail.get()

        response = self._client.mail.send.post(request_body=request_body)

        logger.info(f"SendGrid response - {response}")
