from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from .models import Application, PermissionAssignment

class PermissionAssignmentForm(forms.ModelForm):
    class Meta:
        model = PermissionAssignment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            application = kwargs['instance'].application
            if application:
                self.fields['content_type'].queryset = ContentType.objects.filter(app_label=application)
                self.fields['content_type'].required = True  # Make it a required field

                # Check if the form is submitted with data
                content_type = kwargs['instance'].content_type
                if content_type:
                    content_type=str(content_type).lower().replace(" ", "")
                    content_type_obj = ContentType.objects.get(model=content_type)
                    # print(content_type_obj.__dict__)
                    if content_type_obj:
                        self.fields['content_type'].initial = content_type_obj  # Set the initial value as the ContentType instance
                        self.fields['permissions'].queryset = content_type_obj.permission_set.all()


class PermissionAssignmentAdmin(admin.ModelAdmin):
    form = PermissionAssignmentForm

    def get_form(self, request, obj=None, **kwargs):
        # Store the app_label in the form's instance for later use
        self.app_label = obj.application if obj and hasattr(obj, 'application') else None
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if self.app_label:
            # Get the group associated with the PermissionAssignment
            group = obj.group

            # Get the selected permissions for the group
            selected_permissions = form.cleaned_data.get('permissions')

            # Clear existing permissions for the group
            group.permissions.clear()

            # Add the selected permissions to the group
            for permission in selected_permissions:
                group.permissions.add(permission)

        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        if obj:
            return ['application', 'group', 'content_type', 'permissions']
        return ['application', 'group', 'permissions']

admin.site.register(PermissionAssignment, PermissionAssignmentAdmin)


class ApplicationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Application, ApplicationAdmin)