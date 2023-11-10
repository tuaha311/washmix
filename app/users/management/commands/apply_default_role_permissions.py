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
        users_without_default_role = User.objects.filter(role__isnull=True)
        
        # Apply the default role to these users
        for user in users_without_default_role:
            groups = user.groups.all()
            user_is_admin = any(group.name.lower() in ["admin", "admins"] for group in groups)
            existing_role = Role.objects.filter(user=user).first()

            if not existing_role:
                if user.is_superuser:
                    # Superuser should not be assigned the default role
                    Role.objects.create(user=user, position=RoleChoices.SUPERADMIN)
                elif user_is_admin:
                    # Users in the "Admins" group should not be assigned the default role
                    Role.objects.create(user=user, position=RoleChoices.ADMIN)
                else:
                    # Check if the user doesn't already have a role
                    Role.objects.create(user=user, position=RoleChoices.USER)
            else:
                # Handle the case where a role already exists for the user
                # You can update the existing role or skip the user
                print(f"Role already exists for user {user.username}")
            
        self.stdout.write(self.style.SUCCESS('Default role permissions applied to existing users.'))
