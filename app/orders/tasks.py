from django.db.transaction import atomic

import dramatiq
from weasyprint import HTML

from core.utils import generate_pdf_report_path
from orders.models import Order


@dramatiq.actor
def generate_pdf_from_html(report_html: str, order_pk: int):
    with atomic():
        order = Order.objects.get(pk=order_pk)
        pdf_path = generate_pdf_report_path(order_pk)

        html = HTML(string=report_html)
        html.write_pdf(pdf_path)

        order.is_pdf_ready = True
        order.save()
