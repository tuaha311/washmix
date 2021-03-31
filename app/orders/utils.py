from pathlib import Path

from django.conf import settings
from django.db.models import QuerySet
from django.template.loader import render_to_string

from weasyprint import HTML

from core.utils import generate_pdf_report_path
from notifications.utils import get_extra_context
from orders.models import Order
from subscriptions.utils import is_advantage_program


def prepare_order_prefetch_queryset() -> QuerySet:
    """
    Prepare Order queryset with `prefetch_related` and `select_related` options
    """

    return Order.objects.prefetch_related(
        "basket__quantity_list__price__service",
        "basket__quantity_list__price__item",
        "request__delivery_list",
    ).select_related("subscription", "employee", "coupon", "invoice")


def convert_html_to_pdf(html_content: str, pdf_path: Path):
    """
    Convert HTML-string into PDF-file and write it.
    """

    html = HTML(string=html_content, media_type="all")
    html.write_pdf(
        pdf_path,
    )


def generate_pdf_from_html(order_id: int) -> Path:
    """
    Generates PDF report for Order based on HTML-template.
    """

    order = Order.objects.get(id=order_id)
    client = order.client
    client_id = client.id
    subscription = client.subscription
    is_pdf = True
    is_advantage = is_advantage_program(subscription.name)

    event = settings.NEW_ORDER
    event_info = settings.EMAIL_EVENT_INFO[event]
    context = get_extra_context(
        client_id, order_id=order_id, is_advantage=is_advantage, is_pdf=is_pdf
    )

    template_name = event_info["template_name"]
    html_content = render_to_string(template_name, context=context)

    absolute_pdf_path = generate_pdf_report_path(order_id)

    convert_html_to_pdf(html_content, absolute_pdf_path)

    return absolute_pdf_path
