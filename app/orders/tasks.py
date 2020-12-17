from django.conf import settings
from django.template.loader import render_to_string

import dramatiq
from weasyprint import HTML

from core.utils import generate_pdf_report_path
from notifications.utils import get_extra_context
from orders.models import Order


@dramatiq.actor
def generate_pdf_from_html(order_id: int):
    """
    Generates PDF report for Order based on HTML-template.
    """

    order = Order.objects.get(id=order_id)
    client_id = order.client_id
    event = settings.NEW_ORDER
    event_info = settings.EMAIL_EVENT_INFO[event]
    context = get_extra_context(client_id, order_id=order_id)

    template_name = event_info["template_name"]
    html_content = render_to_string(template_name, context=context)

    pdf_path = generate_pdf_report_path(order_id)

    html = HTML(string=html_content)
    html.write_pdf(pdf_path)

    order.is_pdf_ready = True
    order.save()
