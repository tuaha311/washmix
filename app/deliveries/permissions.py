# deliveries/permissions.py

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# Define your app and module names
job_module, created = ContentType.objects.get_or_create(model='job')

# Create permissions for Manager role
manager_permissions = [
    'create_job',
    'retrieve_job',
    'update_job',
    'delete_job',
]

# Create permissions for Driver role
driver_permissions = [
    'retrieve_job',
]

# Create permissions for Driver role
staff_permissions = [
    'create_job',
    'retrieve_job',
    'update_job',
]

# Assign permissions to Manager and Driver groups
for codename in manager_permissions:
    permission = Permission.objects.get(codename=codename)
    settings.group_manager.permissions.add(permission)

for codename in driver_permissions:
    permission = Permission.objects.get(codename=codename)
    settings.group_admins.permissions.add(permission)

for codename in staff_permissions:
    permission = Permission.objects.get(codename=codename)
    settings.group_staff.permissions.add(permission)
