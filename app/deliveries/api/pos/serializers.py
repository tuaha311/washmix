from rest_framework import serializers

from api.fields import RequestField


class RequestChooseSerializer(serializers.Serializer):
    request = RequestField()
