import os
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from core.utils import generate_pdf_report_path

from orders.api.pos.serializers.orders import OrderSerializer
from orders.choices import OrderPaymentChoices
from orders.containers.order import OrderContainer
from orders.utils import generate_pdf_from_html, prepare_order_prefetch_queryset
from django.conf import settings


class OrderListView(ListAPIView):
    """
    View that show list of order.
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        client = self.request.user.client

        order_list = prepare_order_prefetch_queryset().filter(
            payment=OrderPaymentChoices.PAID, client=client
        )

        return [OrderContainer(item) for item in order_list]


class OrderRepeatView(GenericAPIView):
    """
    View for repeating order.
    """

    def post(self, request: Request, *args, **kwargs):
        return Response()


class OrderRetrieveView(GenericAPIView):
    """
    View to retrieve a specific order by its ID.
    """
    
    def _generate_pdf_report(self, request):
        """
        PDF-report generator method.
        """
        order_id = self.kwargs.get('pk')  # Use self.kwargs to get the order's primary key
        base_dir = settings.BASE_DIR
        base_url = request.get_host()
        existing_pdf = generate_pdf_report_path(order_id)

        if os.path.exists(existing_pdf):
            relative_to_base_dir = existing_pdf.relative_to(base_dir)
            complete_path = f"https://{base_url}/{str(relative_to_base_dir)}"
            return str(complete_path)

        absolute_path = generate_pdf_from_html(order_id)  # Use the order_id as an argument

        relative_to_base_dir = absolute_path.relative_to(base_dir)
        complete_path = f"https://{base_url}/{str(relative_to_base_dir)}"
        return str(complete_path)

    def post(self, request, *args, **kwargs):
        absolute_path = self._generate_pdf_report(request)
        return Response({"pdf_path": absolute_path})