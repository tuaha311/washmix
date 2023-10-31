##############
# PERMISSION MANAGMENT #
##############

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Define your app and module names
job_module, created = ContentType.objects.get_or_create(model='job')

# Create permissions for the job module
Permission.objects.get_or_create(codename='create_job', name='Can create job', content_type=job_module)
Permission.objects.get_or_create(codename='retrieve_job', name='Can retrieve job', content_type=job_module)
Permission.objects.get_or_create(codename='update_job', name='Can update job', content_type=job_module)
Permission.objects.get_or_create(codename='delete_job', name='Can delete job', content_type=job_module)


from django.contrib.auth.models import Group

# Create the Driver and Manager groups
group_admin, created = Group.objects.get_or_create(name="Admins")
group_staff, created = Group.objects.get_or_create(name="Staff")
group_manager, created = Group.objects.get_or_create(name="Manager")