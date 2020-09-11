from django.conf import settings

from djoser import email
from templated_mail.mail import BaseEmailMessage

from core.tasks import raw_send_email


class SendGridEmail(BaseEmailMessage):
    event = "-"
    protocol = "https"

    def send(self, to: list, *args, **kwargs) -> int:
        self.render()

        email_info = self._get_email_info()

        raw_send_email.send(to=to, html_content=self.html, **email_info)

        return len(to)

    def get_context_data(self, **kwargs) -> dict:
        # force HTTPS protocol in email template
        context = super().get_context_data(**kwargs)

        context.update(
            {"protocol": self.protocol,}
        )

        return context

    def _get_email_info(self) -> dict:
        event_info = settings.EMAIL_EVENT_INFO[self.event]
        subject = event_info["subject"]
        from_email = event_info.get("from_email", settings.SENDGRID_FROM_EMAIL)

        return {
            "subject": subject,
            "from_email": from_email,
        }


class PasswordResetEmail(SendGridEmail, email.PasswordResetEmail):
    event = settings.FORGOT_PASSWORD
