from django.conf import settings

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from notifications.models import Notification, NotificationTypes
from notifications.tasks import send_email
from users.api.serializers.customers import CustomerSerializer
from users.choices import CustomerKind
from users.models import Customer


class CustomerCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    def post(self, request, *args, **kwargs):
        resp = super(CustomerCreateView, self).post(request, args, kwargs)

        try:
            customer = Customer.objects.get(pk=resp.data.get("id"))
            if customer.kind == CustomerKind.INTERESTED:
                Notification.create_notification(
                    None, NotificationTypes.POTENTIAL_CUSTOMER, customer
                )

                send_email(
                    event=settings.SEND_ADMIN_PCUSTOMER_INFORMATION,
                    recipient_list=settings.ADMIN_EMAIL_LIST,
                    extra_context={
                        "customer": customer,
                    },
                )
        except:
            pass

        return resp
