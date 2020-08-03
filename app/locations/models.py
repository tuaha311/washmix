from django.db import models

from core.common_models import Common


class City(Common):
    """
    City that we support.
    Only at this cities we can pickup or deliver.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "city"
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class ZipCode(Common):
    """
    Zip codes of supported addresses where our laundry works.
    Only at this zip codes we can pickup or deliver.
    """

    city = models.ForeignKey(
        "locations.City",
        related_name="zipcode_list",
        on_delete=models.CASCADE,
    )

    value = models.CharField(
        verbose_name="value",
        max_length=20,
        unique=True,
    )

    class Meta:
        verbose_name = "zip code"
        verbose_name_plural = "zip codes"

    def __str__(self):
        return f"{self.value}"


class Address(Common):
    """
    Addresses of our clients.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="address_list",
        on_delete=models.CASCADE,
    )
    zip_code = models.ForeignKey(
        "locations.ZipCode",
        verbose_name="zip code",
        related_name="address_list",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        verbose_name="title of address",
        max_length=80,
    )
    address_line_1 = models.TextField(
        verbose_name="address line 1",
    )
    address_line_2 = models.TextField(
        verbose_name="address line 2",
    )
    state = models.CharField(
        verbose_name="state",
        max_length=30,
    )

    class Meta:
        verbose_name = "address"
        verbose_name_plural = "addresses"

    @property
    def city(self):
        return self.zip_code.city
