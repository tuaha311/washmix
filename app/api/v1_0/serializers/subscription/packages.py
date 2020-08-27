from rest_framework import serializers

from billing.models import Invoice, Package


class SetPackageSerializer(serializers.Serializer):
    package = serializers.SlugRelatedField(slug_field="name", queryset=Package.objects.all(),)


class SetPackageInvoiceSerializer(serializers.ModelSerializer):
    package = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Invoice
        fields = ["id", "amount", "package"]
