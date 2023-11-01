from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

class Application(models.Model):
    installed_apps = settings.INSTALLED_APPS
    name = models.CharField(
        max_length=255,
        choices=[(app, app) for app in installed_apps],
        unique=True,
    )

    def __str__(self):
        return self.name
    
class PermissionAssignment(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    permissions = models.ManyToManyField(Permission, null=True, blank=True)
