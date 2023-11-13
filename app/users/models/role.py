from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

def filter_permissions(permissions):
    # Define the codenames to exclude
    exclude_codenames = ['view_role', 'change_role', 'add_role', 'delete_role', 'view_group', 'change_group', 'add_group', 'delete_group', 'view_permission', 'change_permission', 'add_permission', 'delete_permission']

    # Exclude permissions based on codenames
    permissions_to_add = [permission for permission in permissions if not any(exclude_codename in permission.codename for exclude_codename in exclude_codenames)]

    return permissions_to_add

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
        User,
        on_delete=models.CASCADE,
        related_name="role",
    )

    position = models.CharField(
        verbose_name="position of employee",
        max_length=20,
        choices=RoleChoices.CHOICES,
        default=RoleChoices.USER,
    )
    
    def __str__(self):
        return f"{self.user} {self.position}"
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update user permissions based on the role's position
        user = self.user
        if self.position == RoleChoices.SUPERADMIN:
            # Add all available permissions
            permissions = Permission.objects.all()
            user.user_permissions.set(permissions)
        elif self.position == RoleChoices.ADMIN:
            # Add admin permissions (add, change, view) for all content types
            permissions = Permission.objects.filter(
                Q(codename__icontains='add') |
                Q(codename__icontains='change') |
                Q(codename__icontains='view')
            )

            # Exclude permissions based on codenames
            permissions_to_add = filter_permissions(permissions)

            # Add the filtered permissions to the user
            user.user_permissions.clear()
            user.user_permissions.add(*permissions_to_add)

        elif self.position == RoleChoices.EMPLOYEE:
            # Add admin permissions view) for all content types
            permissions = Permission.objects.filter(codename__icontains='view')

            # Exclude permissions based on codenames
            permissions_to_add = filter_permissions(permissions)

            user.user_permissions.clear()
            user.user_permissions.add(*permissions_to_add)
        else:
            # Remove all permissions for other roles
            user.user_permissions.clear()
        user.save()
