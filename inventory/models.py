from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Represents a Category of products."""

    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"))
    image = models.ImageField(_("image"))

    def __str__(self):
        return self.name


class Product(models.Model):
    """Represents a single Product."""

    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"))
    quantity = models.IntegerField(_("quantity"), default=0)
    image = models.ImageField(_("image"))
    price = models.IntegerField(_("price"), default=0)
    created_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_percentage = models.IntegerField(
        _("discount_percentage"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    @property
    def is_available(self):
        """To check if the product is available or not."""
        return self.quantity > 0

    @property
    def price_in_dollars(self):
        """Return the cent price in dollars with two decimals."""
        return f"${self.price / 100:.2f}"

    @property
    def discounted_price_in_dollars(self):
        """Return the price in dollars with the percentage discount applied."""
        discounted = self.get_discounted_price()
        dollars = discounted // 100
        cents = discounted % 100
        return f"${dollars}.{cents:02d}"

    def get_discounted_price(self):
        """if there is a discount, return the discounted price"""
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) // 100
            return self.price - discount_amount
        return self.price

    def created_recently(self):
        """Return if the Product was created recently."""
        return self.created_date >= timezone.now() - datetime.timedelta(days=1)

    def new_arrival(self):
        """Return if the Product is a new arrival - time window 30 days."""
        return self.created_date >= timezone.now() - datetime.timedelta(days=30)

    @classmethod
    def sort_by(cls, sort_criteria, products=None):
        """Sort products by various criteria on any queryset."""
        if products is None:
            products = cls.objects.all()
        if sort_criteria == "new-old":
            return products.order_by("-created_date")
        if sort_criteria == "old-new":
            return products.order_by("created_date")
        if sort_criteria == "price-high-low":
            return products.order_by("-price")
        if sort_criteria == "price-low-high":
            return products.order_by("price")
        if sort_criteria == "discount-high-low":
            return products.order_by("-discount_percentage")
        if sort_criteria == "discount-low-high":
            return products.order_by("discount_percentage")
        if sort_criteria == "a-z":
            return products.order_by("name")
        if sort_criteria == "z-a":
            return products.order_by("-name")
        if sort_criteria == "rating-high-low":
            return products.annotate(avg_rating=models.Avg("reviews__rating")).order_by(
                "-avg_rating"
            )
        return products.order_by("-created_date")

    @classmethod
    def filter_by(cls, filter_criteria_list, products=None):
        """Filter products by multiple criteria on any queryset."""
        if products is None:
            products = cls.objects.all()
        if not filter_criteria_list:
            return products
        for filter_criteria in filter_criteria_list:
            if filter_criteria == "quantity":
                products = products.filter(quantity__gt=0)
            elif filter_criteria == "discount_percentage":
                products = products.filter(discount_percentage__gt=0)
            elif filter_criteria == "created_recently":
                products = products.filter(
                    created_date__gte=timezone.now() - datetime.timedelta(days=30)
                )
        return products

    @classmethod
    def search_by_name(cls, search_name, products=None):
        """function to search products by name"""
        if products is None:
            products = cls.objects.all()

        if search_name:
            products = products.filter(name__icontains=search_name)

        return products

    def __str__(self):
        return self.name
