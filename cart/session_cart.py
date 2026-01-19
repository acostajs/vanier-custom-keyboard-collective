from dataclasses import dataclass
from typing import Dict, TypedDict
from inventory.models import Product

CART_KEY = "cart"  # session key


class CartItemDict(TypedDict):
    """Type alias for a cart item stored in the session."""

    qty: int


@dataclass
class SessionCartItem:
    """Represents an Item in the user's cart session."""

    product_id: int
    quantity: int


class SessionCart:
    """Session-backed shopping cart for Products."""

    _CartData = Dict[str, CartItemDict]

    def __init__(self, request):
        """Initialize a SessionCart instance."""
        self.session = request.session
        cart = self.session.get(CART_KEY)
        if cart is None:
            cart = {}
            self.session[CART_KEY] = cart
        self._cart: SessionCart._CartData = cart

    def save(self):
        """Updates the session with the current cart state."""
        self.session[CART_KEY] = self._cart
        self.session.modified = True

    def add(self, product: Product, quantity: int = 1, replace: bool = False):
        """Add a product to the cart of update its quantity."""
        pid = str(product.id)
        current = self._cart.get(pid, {"qty": 0})
        new_qty = quantity if replace else current["qty"] + quantity
        # clamp to available stock
        new_qty = max(1, min(new_qty, max(product.quantity, 1)))
        self._cart[pid] = {"qty": new_qty}
        self.save()

    def remove(self, product: Product):
        """Removes a product from the user's cart"""
        pid = str(product.id)
        if pid in self._cart:
            del self._cart[pid]
            self.save()

    def clear(self):
        """Empty all items from the user's cart."""
        self.session[CART_KEY] = {}
        self.session.modified = True

    def items(self):
        """Yield full product objects with qty and line totals (in cents)."""
        pids = [int(pid) for pid in self._cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=pids)}
        for pid_str, data in self._cart.items():
            pid = int(pid_str)
            product = products.get(pid)
            if not product:
                continue
            qty = data["qty"]
            unit_cents = product.get_discounted_price()  # cents
            line_cents = unit_cents * qty
            yield {
                "product": product,
                "quantity": qty,
                "unit_cents": unit_cents,
                "line_cents": line_cents,
            }

    def count(self) -> int:
        """Return the total number of items in the user's cart."""
        return sum(data["qty"] for data in self._cart.values())

    def subtotal_cents(self) -> int:
        """Calculate the subtotal cost of the cart contents in cents."""
        return sum(item["line_cents"] for item in self.items())
