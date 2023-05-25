from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.html import format_html

from core.admin import AdminWithSearch
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Holiday, Nonworkingday, Request, Schedule
from users.admin import CustomAutocompleteSelect
from users.models.employee import Employee


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = "__all__"
        widgets = {
            "employee": CustomAutocompleteSelect(
                model._meta.get_field("employee").remote_field, "Select an Employee", admin.site
            )
        }


class DeliveryInlineAdmin(admin.TabularInline):
    model = Delivery
    extra = 0
    form = DeliveryForm
    autocomplete_fields = ("employee",)


class RequestAdmin(AdminWithSearch):
    inlines = [DeliveryInlineAdmin]
    autocomplete_fields = ("client", "address", "schedule")
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

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(Q(id__contains=request.GET.get("q", "")))
        return queryset, use_distinct


class DeliveryAdmin(AdminWithSearch):
    readonly_fields = [
        "order",
        "client",
    ]
    form = DeliveryForm
    list_display = [
        "__str__",
        "full_name",
        "phone",
        "email",
        "date",
        "kind",
        "sorting",
        "employee",
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

    # autocomplete_fields = ('employee',)
    def get_changelist_form(self, request, **kwargs):
        return DeliveryForm

    def get_queryset(self, request):
        return Delivery.objects.filter(
            status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS]
        )

    def full_name(self, obj):
        return format_html(
            "<a href='{url}'>{text}</a>",
            url=reverse("admin:users_client_change", args=(obj.request.client.id,)),
            text=obj.request.client.full_name,
        )

    def phone(self, obj):
        client = obj.client
        if hasattr(client.main_phone, "number"):
            return client.main_phone.number
        return client.main_phone

    def email(self, obj):
        return obj.client.email

    def save_model(self, request, obj, form, change):
        """
        We are catching the moment when admin changes Delivery's
        date and synthetically sending `post_save` signal.
        """
        delivery = obj
        update_fields = frozenset(form.changed_data)

        # if "date" or (
        #     "status" in update_fields and update_fields["status"] == DeliveryStatus.CANCELLED
        # ):
        #     post_save.send(
        #         sender=Delivery,
        #         instance=delivery,
        #         update_fields=update_fields,
        #         created=False,
        #         raw=False,
        #     )
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
        widgets = {
            "client": CustomAutocompleteSelect(
                model._meta.get_field("client").remote_field, "Select a Client", admin.site
            ),
            "address": CustomAutocompleteSelect(
                model._meta.get_field("address").remote_field, "Select an Address", admin.site
            ),
        }


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

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(
                Q(client__user__email__icontains=request.GET.get("q", ""))
                | Q(id__contains=request.GET.get("q", ""))
            )
        return queryset, use_distinct


class NonworkingdayAdmin(AdminWithSearch):
    list_display = [
        "day",
    ]


class HolidayAdmin(AdminWithSearch):
    list_display = [
        "date",
    ]


models = [
    [Schedule, ScheduleAdmin],
    [Delivery, DeliveryAdmin],
    [Request, RequestAdmin],
    [Nonworkingday, NonworkingdayAdmin],
    [Holiday, HolidayAdmin],
]

for item in models:
    admin.site.register(*item)
