from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from users.models import Code  # Import your Code model here
from django.conf import settings
from django.shortcuts import redirect

class SuperAdminVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is a super admin and not on the verification page
        if request.user.is_authenticated and request.user.is_superuser and not request.path.startswith(reverse('verification_view')):
            try:
                code = Code.objects.get(user=request.user)
                if code.authenticated is not True and request.path != reverse('admin:logout'):
                    return redirect('verification_view')
            except Code.DoesNotExist:
                # Super admin doesn't have a code instance, redirect them to create one
                code = Code(user = request.user)
                code.save()
                return redirect('verification_view')
        
        response = self.get_response(request)
        return response
