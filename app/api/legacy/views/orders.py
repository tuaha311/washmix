import logging

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework_social_oauth2.authentication import SocialAuthentication

from api.legacy.permissions import CustomSocialAuthentication, RefreshTokenAuthentication
from api.legacy.serializers.orders import OrderHistorySerializer, OrderSerializer
from orders.models import Order

logging.basicConfig(level=logging.ERROR, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Orders(APIView):
    """
    This api lets you add Orders against any user, orders are linked to address.
    This api lets you add/edit orders. Following is the format for json
        {
        "order": {
            "pick_up_from_datetime": "2017-07-01T01:00:00",
            "pick_up_to_datetime": "2017-07-01T02:00:00",
            "drop_off_from_datetime": "2017-07-05T01:00:00",
            "drop_off_to_datetime": "2017-07-05T02:00:00",
            "instructions": "sample instructions for testing purpose",
            "additional_notes": "sample notes"
    
        }
        }
    """

    authentication_classes = (
        RefreshTokenAuthentication,
        CustomSocialAuthentication,
        SocialAuthentication,
    )
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def post(self, request):
        if request.user:
            request_body = request.data.get("order")

            if request_body:
                order_serializer = OrderSerializer(user=request.user, data=request_body)
                order_serializer.is_valid(raise_exception=True)
                order_id = order_serializer.save()

                if order_id:
                    return Response(
                        data={"order_id": order_id},
                        content_type="json",
                        status=status.HTTP_201_CREATED,
                    )

                return Response(
                    data={"Error": "User Address doesnt exist!"},
                    content_type="json",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                data={"Error": "Missing json body"},
                content_type="json",
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request):
        return self.process_update(request, is_partial=False)

    def patch(self, request):
        return self.process_update(request, is_partial=True)

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            api_message = "Anonymous User!"
            api_status = status.HTTP_401_UNAUTHORIZED
        else:
            try:
                user = None
                if kwargs.get("id"):
                    try:
                        user = User.objects.get(id=kwargs.get("id"))
                    except User.DoesNotExist:
                        pass
                    if not request.user.is_staff:
                        if request.user != user:
                            return Response("You are not allowed to perform this operation")
                else:
                    user = request.user

                user_orders = Order.objects.filter(user=user)
                if user_orders:
                    page = self.paginate_queryset(user_orders)
                    if page is not None:
                        serializer = OrderHistorySerializer(page, many=True)
                        orders = self.get_paginated_response(serializer.data)
                        api_status = status.HTTP_200_OK

                        return Response(
                            data={"Orders": orders.data}, content_type="json", status=api_status,
                        )
                else:
                    api_message = "No order history"
                    api_status = status.HTTP_404_NOT_FOUND
            except Exception as error:
                logger.error("Error while getting Order History: {0}".format(error.detail[0]))
                api_message = "we have experienced some internal issue"
                api_status = status.HTTP_400_BAD_REQUEST

        return Response(data={"message": api_message}, content_type="json", status=api_status)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def process_update(self, request, is_partial=False):
        if request.user:
            request_body = request.data.get("order")
            id = request_body.get("id")
            if not id:
                raise ValidationError({"Id": "Order Id is required!"})

            order = Order.objects.get(user=request.user, id=id)
            if order:
                order_serializer = OrderSerializer(
                    instance=order, data=request_body, partial=is_partial
                )
                order_serializer.is_valid(raise_exception=True)
                order_id = order_serializer.save()
                if order_id:
                    return Response(
                        data={"message": "Order Updated!"},
                        content_type="json",
                        status=status.HTTP_200_OK,
                    )

            return Response(
                data={"message": "Order not updated!"},
                content_type="json",
                status=status.HTTP_400_BAD_REQUEST,
            )
