from ..commands import *
import requests


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("creating admin user...")
        User.objects.create_superuser(
            email="admin@washmix.com",
            username="admin@washmix.com",
            password="aWM$19786_"
        )

        # Add test user via API
        requests.post('http://localhost:8000/users/', json={
            'users': [
                {
                    'email': 'testuser@example.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'password': 'securepass1974',
                    'phone': '6501231231'
                },
                {
                    'email': 'staff@example.com',
                    'first_name': 'Staff',
                    'last_name': 'User',
                    'password': 'staff1974',
                    'phone': '6501231231',
                    'is_staff': True
                }
            ]
        })
