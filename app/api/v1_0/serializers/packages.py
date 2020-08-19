from rest_framework import serializers

from billing.models import Package


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = [
            "created",
            "changed",
        ]


class SetPackageSerializer(serializers.Serializer):
    package = serializers.SlugRelatedField(slug_field="name", queryset=Package.objects.all(),)
