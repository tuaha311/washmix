from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Q
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.html import format_html

from core.admin import AdminWithSearch
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Holiday, Nonworkingday, Request, Schedule
from deliveries.models.categorize_routes import CategorizeRoute
from deliveries.utils import update_deliveries_to_no_show, update_cancelled_deliveries
from users.admin import CustomAutocompleteSelect
from users.models.employee import Employee
from django.shortcuts import render, redirect
from django.contrib import messages
from deliveries.choices import DeliveryStatus
from django.http import HttpResponseRedirect


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = "__all__"
        widgets = {
            "employee": CustomAutocompleteSelect(
                model._meta.get_field("employee").remote_field, "Select an Employee", admin.site
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.kind == DeliveryKind.DROPOFF:
            self.fields['status'].choices = [
                (DeliveryStatus.ACCEPTED, DeliveryStatus.MAP[DeliveryStatus.ACCEPTED]),
                (DeliveryStatus.IN_PROGRESS, DeliveryStatus.MAP[DeliveryStatus.IN_PROGRESS]),
                (DeliveryStatus.COMPLETED, DeliveryStatus.MAP[DeliveryStatus.COMPLETED]),
            ]
            
class ArchivedDeliveryForm(forms.ModelForm):
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


class DeliveryAdminMain(AdminWithSearch):
    change_list_template = 'assets/change_employee.html'
    readonly_fields = [
        "order",
        "client",
    ]
    form = DeliveryForm
    list_display_links = ['__str__']
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
    
    ''' I HAVE SET ACTIONS STYLE TO DISPLAY NONE IN change_employee.html WE WILL NEED TO REMOVE THAT IF WE ADD ANY NEW ACTION '''
    actions=["update_deliveries"]
    def update_deliveries(request):
        if request.method == 'POST':
            selected_deliveries = request.POST.getlist('selected_deliveries')
            new_employee_id = request.POST.get('new_employee_id')
            new_status = request.POST.get('new_status')
            url = request.POST.get('url')

            if selected_deliveries and (new_employee_id != "" or new_status != ""):
                update_fields = {}
                if new_employee_id != "":
                    Delivery.objects.filter(id__in=selected_deliveries).update(employee_id=new_employee_id)
                    update_fields['employee'] = new_employee_id

                if new_status != "":
                    if new_status == DeliveryStatus.NO_SHOW:
                        # Check if the delivery kind is 'DROPOFF' and new status is 'NO_SHOW'
                        for delivery_id in selected_deliveries:
                            delivery = Delivery.objects.get(id=delivery_id)
                            if delivery.kind == DeliveryKind.PICKUP:
                                update_deliveries_to_no_show(delivery)

                            if delivery.kind == DeliveryKind.DROPOFF:
                                delivery_request = delivery.request
                                pickup = delivery_request.delivery_list.get(kind=DeliveryKind.PICKUP)
                                if pickup.status is not DeliveryStatus.NO_SHOW:
                                    messages.warning(request, f"Dropoff delivery for {delivery_id} cannot be marked as No Show.")
                                    continue
                            else:
                                # Update other deliveries to the new status
                                Delivery.objects.filter(id=delivery_id).update(status=new_status)
                                update_fields['status'] = new_status
                                
                    elif selected_deliveries and new_status == DeliveryStatus.CANCELLED:
                        for delivery_id in selected_deliveries:
                            delivery = Delivery.objects.get(id=delivery_id)
                            updated_delivery = update_cancelled_deliveries(delivery)
                            if updated_delivery:
                                Delivery.objects.filter(id=delivery_id).update(status=new_status)
                                update_fields['status'] = new_status
                            else:
                                messages.warning(request, f'Delivery {delivery_id} cannot be marked cancelled because the corresponding pickup is not cancelled.')

                    else:
                        # Update all deliveries to the new status
                        Delivery.objects.filter(id__in=selected_deliveries).update(status=new_status)
                        update_fields['status'] = new_status

                if update_fields:
                    messages.success(request, 'Deliveries updated successfully.')
                else:
                    messages.warning(request, 'No valid data selected.')

            return redirect(url)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        employee_choices = [('', '...')] + [(employee.id, str(employee)) for employee in Employee.objects.all()]
        status_choices = [('', '...')] + list(DeliveryStatus.CHOICES)

        extra_context['employee_choices'] = employee_choices
        extra_context['status_choices'] = status_choices

        return super().changelist_view(request, extra_context=extra_context)

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

        if obj.kind == DeliveryKind.DROPOFF and (
        obj.status == DeliveryStatus.NO_SHOW
        or obj.status in [DeliveryStatus.IN_PROGRESS, DeliveryStatus.COMPLETED]
        ):
            if obj.status == DeliveryStatus.NO_SHOW:
                message = "Invalid status for a dropoff delivery."
            else:
                pickup_delivery = obj.request.delivery_list.filter(kind=DeliveryKind.PICKUP).first()
                if pickup_delivery and pickup_delivery.status != DeliveryStatus.COMPLETED:
                    message = "Cannot set dropoff delivery as 'In Progress' or 'Completed' when the corresponding pickup delivery is not completed."
                else:
                    pass

            if 'message' in locals():
                self.message_user(request, '', level=messages.ERROR)
                messages.set_level(request, messages.ERROR)
                messages.error(request, message)
                return

        update_fields = frozenset(form.changed_data)

        if "admin" in request.path:
            # The form was submitted from the admin panel
            if "date" in update_fields:
                print("Sending the Singnal to delivery.")
                post_save.send(
                    sender=Delivery,
                    instance=obj,
                    update_fields=update_fields,
                    created=False,
                    raw=False,
                )

        if obj.kind == DeliveryKind.PICKUP and obj.status == DeliveryStatus.NO_SHOW:
            print("Marking the Delivery to No Show and Charging client.")
            update_deliveries_to_no_show(obj)
            
        if obj.kind == DeliveryKind.PICKUP and obj.status == DeliveryStatus.CANCELLED:
            print("Marking the Delivery to Cancelled.")
            update_cancelled_deliveries(obj)

        return super().save_model(request, obj, form, change)

class DeliveryAdmin(DeliveryAdminMain):
    form = DeliveryForm
    # autocomplete_fields = ('employee',)
    def get_changelist_form(self, request, **kwargs):
        return DeliveryForm
    
    
class ArchivedDeliveryAdmin(DeliveryAdminMain):
    form = ArchivedDeliveryForm
    # autocomplete_fields = ('employee',)
    def get_changelist_form(self, request, **kwargs):
        return ArchivedDeliveryForm
    

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

class CategorizeRouteForm(forms.ModelForm):
    class Meta:
        model = CategorizeRoute
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')

        if Nonworkingday.objects.filter(day=day).exists():
            raise forms.ValidationError('This day is a non-working day.')

        return cleaned_data
    
class CategorizeRouteAdmin(admin.ModelAdmin):
    list_display = ('day', 'all_zip_codes')
    form = CategorizeRouteForm
    
    def all_zip_codes(self, obj):
        if obj.id:
            return ", ".join([str(zip_code) for zip_code in obj.zip_codes.all()])
        return ""


models = [
    [Schedule, ScheduleAdmin],
    [Delivery, DeliveryAdmin],
    [Request, RequestAdmin],
    [Nonworkingday, NonworkingdayAdmin],
    [Holiday, HolidayAdmin],
    [CategorizeRoute, CategorizeRouteAdmin],
]

for item in models:
    admin.site.register(*item)
