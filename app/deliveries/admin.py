from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.html import format_html

from core.admin import AdminWithSearch
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Request, Schedule


class DeliveryInlineAdmin(admin.TabularInline):
    model = Delivery
    extra = 0


class RequestAdmin(AdminWithSearch):
    inlines = [DeliveryInlineAdmin]
    list_display = [
        "__str__",
        "request_client",
        "address",
        "comment",
        "is_rush",
        "pickup_date",
        "pickup_status",
        "dropoff_date",
        "dropoff_status",
    ]

    def get_queryset(self, request):
        return Request.objects.filter(
            delivery_list__kind=DeliveryKind.DROPOFF,
            delivery_list__status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS],
        )

    def request_client(self, obj):
        return format_html(
            "<a href='{url}'>{text}</a>",
            url=reverse("admin:users_client_change", args=(obj.client.id,)),
            text=obj.client,
        )


class DeliveryAdmin(AdminWithSearch):
    readonly_fields = [
        "order",
        "client",
    ]
    list_display = [
        "__str__",
        "client",
        "date",
        "sorting",
        "employee",
        "kind",
        "status",
        "address",
        "is_rush",
        "note",
        "comment",
        "changed",
    ]
    list_editable = [
        "date",
        "employee",
        "status",
        "sorting",
    ]
    list_filter = [
        "status",
        "kind",
        "employee",
    ]

    def get_queryset(self, request):
        return Delivery.objects.filter(
            status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS]
        )

    def client(self, obj):
        return format_html(
            "<a href='{url}'>{text}</a>",
            url=reverse("admin:users_client_change", args=(obj.request.client.id,)),
            text=obj.request.client,
        )

    def save_model(self, request, obj, form, change):
        """
        We are catching the moment when admin changes Delivery's
        date and synthetically sending `post_save` signal.
        """

        delivery = obj
        update_fields = frozenset(form.changed_data)

        if "date" in update_fields:
            post_save.send(
                sender=Delivery,
                instance=delivery,
                update_fields=update_fields,
                created=False,
                raw=False,
            )

        return super().save_model(request, obj, form, change)


class ScheduleForm(forms.ModelForm):
    # we are overriding default `days` field widget
    days = forms.TypedMultipleChoiceField(
        coerce=lambda val: int(val),
        choices=settings.DELIVERY_DAY_CHOICES,
        label="Recurring pickup days",
    )

    class Meta:
        model = Schedule
        fields = "__all__"


class ScheduleAdmin(AdminWithSearch):
    form = ScheduleForm
    list_display = [
        "id",
        "schedule_days",
        "schedule_client",
    ]

    def schedule_days(self, obj):
        pretty_days = [settings.DELIVERY_DAYS_MAP[item] for item in obj.days]
        string_days = ", ".join(pretty_days)
        return string_days

    def schedule_client(self, obj):
        return format_html(
            "<a href='{url}'>{text}</a>",
            url=reverse("admin:users_client_change", args=(obj.client.id,)),
            text=obj.client,
        )


models = [[Schedule, ScheduleAdmin], [Delivery, DeliveryAdmin], [Request, RequestAdmin]]
for item in models:
    admin.site.register(*item)
