from rest_framework import serializers

from users.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "email",
            "phone",
            "full_name",
            "zip_code",
            "address",
            "kind",
        ]
