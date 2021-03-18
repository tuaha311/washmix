from django.db import models

from core.common_models import Common


class City(Common):
    """
    Service-side entity.

    City that we support.
    Only at this cities we can pickup or deliver.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=50,
        unique=True,
    )
    zip_code_list = models.ManyToManyField(
        "locations.ZipCode",
        related_name="city_list",
    )

    class Meta:
        verbose_name = "city"
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class ZipCode(Common):
    """
    Service-side entity.

    Zip codes of supported addresses where our laundry works.
    Only at this zip codes we can pickup or deliver.
    """

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
    Client-side entity.

    Addresses of our clients.

    IMPORTANT: Address entity has a signal receiver on `post_save`.
    Signal location - `locations.signals`
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
    address_line_1 = models.CharField(
        verbose_name="address line 1",
        max_length=250,
    )
    address_line_2 = models.CharField(
        verbose_name="address line 2",
        max_length=250,
        blank=True,
    )
    instructions = models.TextField(
        verbose_name="delivery instructions",
        blank=True,
    )
    has_doorman = models.BooleanField(
        verbose_name="is doorman at this address",
        default=False,
    )

    class Meta:
        verbose_name = "address"
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.zip_code}, {self.address_line_1}"
