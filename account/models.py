from django.contrib.auth.models import AbstractUser
from django.db import models
from inventory.models import Product
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Account(AbstractUser):
    """Represents a User Account."""

    address_line1 = models.CharField(_("address_line1"), max_length=255)
    address_line2 = models.CharField(_("address_line2"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=100)
    postal_code = models.CharField(_("postal_code"), max_length=20)
    country = models.CharField(_("country"), max_length=100)

    def __str__(self):
        return self.username


class Wishlist(models.Model):
    """Represents a Wishlist where User(Account) can add items."""

    product = models.ManyToManyField(Product, blank=True)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def add(self, product: Product):
        """To add a product to the wishlist."""
        self.product.add(product)
        self.save()

    def remove(self, product: Product):
        """To remove a product from the wishlist."""
        self.product.remove(product)
        self.save()

    def clear(self):
        """To clear all products from the wishlist."""
        self.product.clear()
        self.save()

    def count(self):
        """Returns the number of products in the wishlist."""
        return self.product.count()
