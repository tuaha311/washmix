# deliveries/permissions.py

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from deliveries.models import Delivery

# Define your app and module names
delivery_module, created = ContentType.objects.get_or_create(model=Delivery)

# Create permissions for the delivery module
Permission.objects.get_or_create(codename='create_delivery', name='Can create delivery', content_type=delivery_module)
Permission.objects.get_or_create(codename='retrieve_delivery', name='Can retrieve delivery', content_type=delivery_module)
Permission.objects.get_or_create(codename='update_delivery', name='Can update delivery', content_type=delivery_module)
Permission.objects.get_or_create(codename='delete_delivery', name='Can delete delivery', content_type=delivery_module)


from django.contrib.auth.models import Group

# Create the Driver and Manager groups
group_admin, created = Group.objects.get_or_create(name="Admin_Lite")
group_staff, created = Group.objects.get_or_create(name="Staff")
group_manager, created = Group.objects.get_or_create(name="Manager")

# Define your app and module names
delivery_module, created = ContentType.objects.get_or_create(model='delivery')

# Create permissions for Manager role
manager_permissions = [
    'create_delivery',
    'retrieve_delivery',
    'update_delivery',
    'delete_delivery',
]

# Create permissions for Driver role
admin_permissions = [
    'retrieve_delivery',
]

# Create permissions for Driver role
staff_permissions = [
    'create_delivery',
    'retrieve_delivery',
    'update_delivery',
]

# Assign permissions to Manager and Driver groups
for codename in manager_permissions:
    permission = Permission.objects.get(codename=codename)
    group_manager.permissions.add(permission)

for codename in admin_permissions:
    permission = Permission.objects.get(codename=codename)
    group_admin.permissions.add(permission)

for codename in staff_permissions:
    permission = Permission.objects.get(codename=codename)
    group_staff.permissions.add(permission)
