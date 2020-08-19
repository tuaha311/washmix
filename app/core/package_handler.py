from users.models import Client


class PackageHandler:
    def __init__(self, client: Client):
        self._client = client

    def change(self, package):
        self._client.package = package
        self._client.save()

        return self._client.package
