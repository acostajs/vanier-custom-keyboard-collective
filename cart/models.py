from inventory.models import Product
from account.models import Account
import stripe
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    """Represents an Order and its Status."""

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True)
    payment_id = models.CharField(
        _("payment_id"), max_length=255, unique=True, null=True, blank=True
    )
    total_cents = models.IntegerField(_("total_cents"))
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    billing_address_line1 = models.CharField(
        _("billing_address_line1"), max_length=255, blank=True, null=True
    )
    billing_address_line2 = models.CharField(
        _("billing_address_line2"), max_length=255, blank=True, null=True
    )
    billing_city = models.CharField(
        _("billing_city"), max_length=100, blank=True, null=True
    )
    billing_postal_code = models.CharField(
        _("billing_postal_code"), max_length=20, blank=True, null=True
    )
    billing_country = models.CharField(
        _("billing_country"), max_length=100, blank=True, null=True
    )

    shipping_address_line1 = models.CharField(
        _("shipping_address_line1"), max_length=255, blank=True, null=True
    )
    shipping_address_line2 = models.CharField(
        _("shipping_address_line2"), max_length=255, blank=True, null=True
    )
    shipping_city = models.CharField(
        _("shipping_city"), max_length=100, blank=True, null=True
    )
    shipping_postal_code = models.CharField(
        _("shipping_postal_code"), max_length=20, blank=True, null=True
    )
    shipping_country = models.CharField(
        _("shipping_country"), max_length=100, blank=True, null=True
    )

    def set_status(self, status: str) -> None:
        """Represents the status of an Order,"""
        current_status = status.lower()
        if current_status not in {
            self.STATUS_PENDING,
            self.STATUS_PAID,
            self.STATUS_CANCELLED,
        }:
            raise ValueError(f"Invalid status: {status}")
        self.status = current_status
        self.save()

    def fulfill(
        self,
        name: str,
        email: str,
        payment_id: str,
        total_cents: int,
        billing_address_line1: str,
        billing_address_line2: str,
        billing_city: str,
        billing_postal_code: str,
        billing_country: str,
        shipping_address_line1: str,
        shipping_address_line2: str,
        shipping_city: str,
        shipping_postal_code: str,
        shipping_country: str,
    ) -> None:
        """Fulfill order with payment details."""
        self.name = name
        self.email = email
        self.payment_id = payment_id
        self.total_cents = total_cents
        self.billing_address_line1 = billing_address_line1
        self.billing_address_line2 = billing_address_line2
        self.billing_city = billing_city
        self.billing_postal_code = billing_postal_code
        self.billing_country = billing_country
        self.shipping_address_line1 = shipping_address_line1
        self.shipping_address_line2 = shipping_address_line2
        self.shipping_city = shipping_city
        self.shipping_postal_code = shipping_postal_code
        self.shipping_country = shipping_country
        self.save()

    @classmethod
    def create_from_cart(cls, request, cart):
        """Create Order + OrderItems from cart and return Stripe Checkout session."""
        cart_items = list(cart.items())
        if not cart_items:
            return None, None

        order = cls(total_cents=cart.subtotal_cents())
        if request.user.is_authenticated:
            order.user = request.user
        order.save()

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                unit_price_cents=item["unit_cents"],
            )

        line_items = []
        for item in cart_items:
            line_items.append(
                {
                    "price_data": {
                        "unit_amount": item["unit_cents"],
                        "currency": "cad",
                        "product_data": {
                            "name": item["product"].name,
                            "images": [
                                request.build_absolute_uri(item["product"].image.url)
                            ]
                            if item["product"].image
                            else [],
                        },
                    },
                    "quantity": item["quantity"],
                }
            )

        session_args = {
            "client_reference_id": str(order.id),
            "line_items": line_items,
            "mode": "payment",
            "success_url": request.build_absolute_uri(reverse("cart:success"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": request.build_absolute_uri(reverse("cart:cancel")),
        }

        if request.user.is_authenticated:
            session_args["customer_email"] = request.user.email
            session_args["billing_address_collection"] = "auto"
        else:
            session_args["billing_address_collection"] = "required"
            session_args["shipping_address_collection"] = {
                "allowed_countries": ["US", "CA"]
            }

        checkout_session = stripe.checkout.Session.create(**session_args)
        return checkout_session, order

    def __str__(self):
        return f"Order #{self.payment_id} - {self.user.email}"


class OrderItem(models.Model):
    """Represents Individual items in an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(_("quantity"))
    unit_price_cents = models.IntegerField(_("unit_price_cents"))

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def line_total_cents(self):
        return self.quantity * self.unit_price_cents


class Cart(models.Model):
    """Represents an account related Cart."""

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="CartItem")

    def items(self):
        """Returns all CartItem objects for this cart."""
        return CartItem.objects.filter(cart=self)

    def add(self, product: Product, quantity=1, replace=False):
        """Add a product to the cart or update its quantity."""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self, product=product, defaults={"quantity": quantity}
        )
        if not created:
            if replace:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()

    def remove(self, product: Product):
        """Remove a product completely from the cart."""
        CartItem.objects.filter(cart=self, product=product).delete()

    def clear(self):
        """Remove all products from the cart."""
        CartItem.objects.filter(cart=self).delete()

    def count(self):
        """Count all items in the cart."""
        total_quantity = 0
        for item in CartItem.objects.filter(cart=self):
            total_quantity += item.quantity
        return total_quantity

    def subtotal_cents(self):
        """Total cents added to the cart."""
        total = 0
        items = CartItem.objects.filter(cart=self)
        for item in items:
            total += item.total_cents
        return total

    def __str__(self):
        return f"This cart belongs to account {self.account.email}"


class CartItem(models.Model):
    """Represents an individual items inside an account related cart."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(_("quantity"), validators=[MinValueValidator(1)])

    @property
    def total_cents(self):
        """Calculate the total cost of an Item."""
        return self.quantity * self.product.price

    @property
    def unit_cents(self):
        """Returns the price in cents of a single unit."""
        return self.product.price

    @property
    def line_cents(self):
        """Calculate the total cost of an Item."""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} cart item"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_product_per_cartItem"
            )
        ]
