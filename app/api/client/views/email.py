from rest_framework import generics, serializers
from users.models import Client
from api.client.serializers.email import ClientVerificationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.shortcuts import redirect


class ClientVerificationView(generics.RetrieveAPIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    queryset = Client.objects.all()
    serializer_class = ClientVerificationSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the email is already verified
        if instance.verified_email:
            return redirect(f"https://{settings.DOMAIN}/?email-verified=true&message=This email has already been verified")

        # Perform the email verification logic here
        hash_param = self.kwargs.get('hash')
        
        if hash_param == instance.verified_email_hash:
            instance.verified_email = True
            instance.save()
            redirect_url = f"https://{settings.DOMAIN}/?email-verified=true&message=Thank You! Your email has been verified successfully"
            return redirect(redirect_url)
        else:
            redirect_url = f"https://{settings.DOMAIN}/?email-verified=false&message=Email verification failed. Please check the link or request a new one"
            return redirect(redirect_url)


