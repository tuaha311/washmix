from notifications.tasks import send_admin_client_information
from users.models import Log


class ProxyFieldsOnModelUpdate:
    proxy_fields = set()

    def perform_update(self, serializer):
        """
        Proxy `update_fields` value to signals.
        """

        instance = serializer.instance

        unique_fields = set(serializer.validated_data.keys())
        update_fields = self.proxy_fields & unique_fields
        old_fields = {}
        if "starch" in unique_fields:
            old_fields["starch"] = self.request.user.client.starch
            old_fields["crease"] = self.request.user.client.no_crease
            old_fields["tears"] = self.request.user.client.fix_tears

        super().perform_update(serializer)
        log = ""
        for up in update_fields:
            log += str(up) + ", "
        if log:
            log = log[:-2]
            Log.objects.create(customer=self.request.user.email, action=f"The user updated {log}")
            send_admin_client_information(self.request.user.client.id, f"The user updated {log}")

        if "starch" in unique_fields:
            starch_log = ""
            if old_fields["starch"] != self.request.user.client.starch:
                starch_log += "Starch, "
            if old_fields["crease"] != self.request.user.client.no_crease:
                starch_log += "No Crease, "
            if old_fields["tears"] != self.request.user.client.fix_tears:
                starch_log += "Fix Tears, "
            if starch_log:
                Log.objects.create(
                    customer=self.request.user.email, action=f"The user updated {starch_log[:-2]}"
                )
                send_admin_client_information(
                    self.request.user.client.id, f"The user updated {starch_log[:-2]}"
                )
        instance.save(update_fields=update_fields)
