from django.urls import reverse
from django.core.exceptions import PermissionDenied
from users.models import Employee

class DriverVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                employee = Employee.objects.get(user=request.user)
                user_is_driver = True if employee.position == "driver" else False

                if user_is_driver and request.path.startswith(reverse('admin:index')) and request.path != reverse('admin:logout'):
                    # If the user is a driver and trying to access the admin page, deny access
                    raise PermissionDenied("Drivers are not allowed to access the admin page.")

            except Employee.DoesNotExist:
                pass

        response = self.get_response(request)
        return response