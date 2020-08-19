from rest_framework import serializers

from users.models import Client


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)
    package = serializers.SlugRelatedField(slug_field="name", read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = Client
        exclude = ["user", "created", "changed", "detergents", "starch", "no_crease",]
