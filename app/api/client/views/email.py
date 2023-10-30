from rest_framework import generics, serializers
from users.models import Client
from api.client.serializers.email import ClientVerificationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class ClientVerificationView(generics.RetrieveAPIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    queryset = Client.objects.all()
    serializer_class = ClientVerificationSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Perform the email verification logic here
        instance.verified_email = True
        instance.save()
        
        return Response("Thank You! Your email has been verified successfully", status=status.HTTP_200_OK)
