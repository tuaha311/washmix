from core.containers import BaseAmountContainer


class ExtraItemContainer(BaseAmountContainer):
    proxy_to_object = "_extra_item"

    def __init__(self, extra_item):
        self._extra_item = extra_item

    @property
    def discount(self):
        return 0

    @property
    def amount(self):
        extra_item = self._extra_item

        return extra_item["amount"]

    @property
    def title(self):
        extra_item = self._extra_item

        return extra_item["title"]

    @property
    def instructions(self):
        extra_item = self._extra_item

        return extra_item["instructions"]
