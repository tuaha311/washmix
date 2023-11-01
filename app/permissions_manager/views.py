from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Application, CustomPermission
from django.contrib.auth.models import Group
from .forms import ApplicationForm

class ApplicationCreateView(CreateView):
    form_class = ApplicationForm
    model = Application
    fields = ['name']
    template_name = 'templates/application_form.html'
    success_url = reverse_lazy('application-list')
    
class GroupCreateView(CreateView):
    model = Group
    fields = ['name']
    template_name = 'templates/group_form.html'
    success_url = reverse_lazy('group-list')
    
class PermissionCreateView(CreateView):
    model = CustomPermission
    fields = ['app', 'name']
    template_name = 'templates/permission_form.html'
    success_url = reverse_lazy('permission-list')