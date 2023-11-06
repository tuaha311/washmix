from django.core.management.base import BaseCommand
from users.models import Role
from users.models.role import RoleChoices
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Apply default role permissions to existing users'

    def handle(self, *args, **kwargs):
        # Find all users with roles that don't have the default
        # users_without_default_role = User.objects.filter(role__isnull=True)
        users_without_default_role = User.objects.all()
        
        # Apply the default role to these users
        for user in users_without_default_role:
            groups = user.groups.all()
            user_is_admin = any(group.name.lower() in ["admin", "admins"] for group in groups)

            # print(user_is_admin)
            if user.is_superuser:
                # Superuser should not be assigned the default role
                Role.objects.create(user=user, position=RoleChoices.SUPERADMIN)
            if user_is_admin:
                # Users in the "Admins" group should not be assigned the default role
                Role.objects.create(user=user, position=RoleChoices.ADMIN)
            else:
                # Check if the user doesn't already have a role
                Role.objects.create(user=user, position=RoleChoices.USER)
                pass
            
        self.stdout.write(self.style.SUCCESS('Default role permissions applied to existing users.'))
