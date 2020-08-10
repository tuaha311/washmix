from django.conf import settings

from djoser import email
from templated_mail.mail import BaseEmailMessage

from notifications.senders.sendgrid import SendGridSender


class SendGridEmail(BaseEmailMessage):
    event = "-"
    protocol = "https"

    # TODO move logic to dramatiq
    def send(self, to, *args, **kwargs):
        self.render()

        sender = SendGridSender()

        email_info = self._get_email_info()
        sender.raw_send(
            recipient_list=to, html_content=self.html, **email_info,
        )

        return len(to)

    def get_context_data(self, **kwargs):
        # force HTTPS protocol in email template
        context = super().get_context_data(**kwargs)

        context.update(
            {"protocol": self.protocol,}
        )

        return context

    def _get_email_info(self):
        event_info = settings.EMAIL_EVENT_INFO[self.event]
        subject = event_info["subject"]
        from_email = event_info.get("from_email", settings.SENDGRID_FROM_EMAIL)

        return {
            "subject": subject,
            "from_email": from_email,
        }


class PasswordResetEmail(SendGridEmail, email.PasswordResetEmail):
    event = settings.FORGOT_PASSWORD
