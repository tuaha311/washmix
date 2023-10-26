from rest_framework import serializers
from users.models import Client

class ClientVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('verified_email',)
