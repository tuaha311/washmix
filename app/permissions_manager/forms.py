from django import forms
from .models import Application, CustomPermission
from django.contrib.auth.models import Group

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name']
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class PermissionForm(forms.ModelForm):
    class Meta:
        model = CustomPermission
        fields = ['app', 'name']
