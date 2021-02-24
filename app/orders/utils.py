from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string

from weasyprint import HTML

from core.utils import generate_pdf_report_path
from notifications.utils import get_extra_context
from orders.models import Order
from subscriptions.utils import is_advantage_program


def generate_pdf_from_html(order_id: int) -> Path:
    """
    Generates PDF report for Order based on HTML-template.
    """

    order = Order.objects.get(id=order_id)
    client = order.client
    client_id = client.id
    subscription = client.subscription
    is_advantage = is_advantage_program(subscription.name)

    event = settings.NEW_ORDER
    event_info = settings.EMAIL_EVENT_INFO[event]
    context = get_extra_context(client_id, order_id=order_id, is_advantage=is_advantage)

    template_name = event_info["template_name"]
    html_content = render_to_string(template_name, context=context)

    absolute_pdf_path = generate_pdf_report_path(order_id)

    html = HTML(string=html_content)
    html.write_pdf(absolute_pdf_path)

    return absolute_pdf_path
