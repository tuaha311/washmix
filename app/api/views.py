import re

from django.conf import settings
from django.urls import re_path
from django.utils.timezone import localtime
from django.views.generic import TemplateView
from django.views.static import serve

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import HealthSerializer
from core.tasks import worker_health
from notifications.utils import get_extra_context


class HealthView(GenericAPIView):
    """
    PUBLIC METHOD.

    View that shows our API is working.
    Also, via this view we are checking that
    dramatiq worker is working.
    """

    serializer_class = HealthSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        worker_health.send()

        now = localtime()
        debug = settings.DEBUG

        return Response({"status": "ok", "now": now, "debug": debug})


class EmailRenderView(TemplateView):
    """
    View that renders emails with defined context.
    """

    email_template_map = {
        "account_removed": "email/account_removed.html",
        "card_changes": "email/card_changes.html",
        "order": "email/new_order.html",
        "payment_admin": "email/payment_fail_admin.html",
        "payment_client": "email/payment_fail_client.html",
        "subscription": "email/purchase_subscription.html",
        "credit_back": "email/accrue_credit_back.html",
        "signup": "email/signup.html",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        extra_context = get_extra_context(
            client_id=2,
            subscription_id=2,
            request_id=2,
            order_id=4,
            is_advantage=True,
            is_unpaid=True,
            full_name="Bob Brown",
            action="removed from",
            dollar_credit_back=9.89,
        )

        return {**context, **extra_context}

    def get_template_names(self):
        kwargs = self.kwargs
        email_kind = kwargs["email_kind"]

        template_name = self.email_template_map[email_kind]

        return [template_name]


def static_server(prefix, view=serve, **kwargs):
    """
    Static server view that was inspired by default
    `django.conf.urls.static`.
    """

    return [
        re_path(r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs),
    ]
