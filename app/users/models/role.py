from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission

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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update user permissions based on the role's position
        user = self.user
        if self.position == RoleChoices.SUPERADMIN:
            # Add all available permissions
            permissions = Permission.objects.all()
            user.user_permissions.set(permissions)
        elif self.position == RoleChoices.ADMIN:
            # Add admin permissions (add, change, delete, view) for all content types
            permissions = Permission.objects.filter(codename__in=[
                "add_contenttype",
                "change_contenttype",
                "delete_contenttype",
                "view_contenttype",
                # Add more permissions as needed
            ])
            user.user_permissions.set(permissions)
        else:
            # Remove all permissions for other roles
            user.user_permissions.clear()
        user.save()