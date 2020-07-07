from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework_expiring_authtoken.models import ExpiringToken


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(label=_("Token"))

    def validate(self, attrs):

        if attrs.get("token"):
            try:
                token = ExpiringToken.objects.select_related("user").get(key=attrs.get("token"))
            except ExpiringToken.DoesNotExist:
                raise serializers.ValidationError("Token Doesn't exist")
        else:
            raise serializers.ValidationError("Token is a must")

        attrs["user"] = token.user
        attrs["token"] = token
        return attrs
