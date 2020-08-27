from rest_framework import serializers

from billing.models import Invoice, Package


class SetPackageSerializer(serializers.Serializer):
    package = serializers.SlugRelatedField(slug_field="name", queryset=Package.objects.all(),)


class SetPackageInvoiceSerializer(serializers.ModelSerializer):
    package = serializers.CharField(read_only=True, source="package.name")

    class Meta:
        model = Invoice
        fields = ["id", "amount", "package"]
