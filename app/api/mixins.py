class ProxyFieldsOnModelUpdate:
    proxy_fields = set()

    def perform_update(self, serializer):
        """
        Proxy `update_fields` value to signals.
        """

        instance = serializer.instance

        unique_fields = set(serializer.validated_data.keys())
        update_fields = self.proxy_fields & unique_fields

        super().perform_update(serializer)

        instance.save(update_fields=update_fields)
