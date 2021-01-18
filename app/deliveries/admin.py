from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models.signals import post_save

from core.admin import AdminWithSearch
from deliveries.models import Delivery, Request, Schedule


class DeliveryInlineAdmin(admin.TabularInline):
    model = Delivery
    extra = 0


class RequestAdmin(AdminWithSearch):
    inlines = [DeliveryInlineAdmin]
    list_display = [
        "__str__",
        "client",
        "address",
        "comment",
        "is_rush",
        "pickup_date",
        "pickup_status",
        "dropoff_date",
        "dropoff_status",
    ]


class DeliveryAdmin(AdminWithSearch):
    readonly_fields = [
        "order",
    ]
    list_display = [
        "__str__",
        "date",
        "sorting",
        "employee",
        "kind",
        "status",
        "address",
        "is_rush",
        "note",
        "comment",
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
    ]

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


models = [[Schedule, ScheduleAdmin], [Delivery, DeliveryAdmin], [Request, RequestAdmin]]
for item in models:
    admin.site.register(*item)
