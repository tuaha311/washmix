from rest_framework import serializers

from users.models import Client


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)

    class Meta:
        model = Client
        exclude = ["user", "created", "changed", "detergents", "starch", "no_crease"]
