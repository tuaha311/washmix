from rest_framework import serializers

from users.models import Client


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)
    subscription = serializers.SlugRelatedField(slug_field="name", read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    balance = serializers.IntegerField(read_only=True)
    dollar_balance = serializers.FloatField(read_only=True)

    class Meta:
        model = Client
        exclude = [
            "user",
            "created",
            "changed",
        ]
