from django.db import models
from django.conf import settings

class RoleChoices:
    SUPERADMIN = "super_admin"
    ADMIN = "admin"
    EMPLOYEE = "employee"
    USER = "user"
    MAP = {
        SUPERADMIN: "Super Admin",
        ADMIN: "Admin",
        EMPLOYEE: "Employee",
        USER: "User",
    }
    CHOICES = list(MAP.items())
    
class Role(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role",
    )

    position = models.CharField(
        verbose_name="position of employee",
        max_length=20,
        choices=RoleChoices.CHOICES,
        default=RoleChoices.USER,
    )