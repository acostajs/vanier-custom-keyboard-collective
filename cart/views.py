from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order
from .helpers import get_cart, parse_quantity
from inventory.models import Product
from django.utils.translation import gettext_lazy as _


def add_to_cart(request, product_id):
    """Add a specified product ot the user's shopping cart."""
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart = get_cart(request)
    cart.add(product, quantity=qty)
    messages.success(request, f"Added {product.name} (x{qty}) to cart.")
    return redirect("cart:cart_detail")


def cart_detail(request):
    """Display details of the user's shopping cart."""
    cart = get_cart(request)
    context = {
        "cart_items": list(cart.items()),
        "subtotal_cents": cart.subtotal_cents(),
        "cart_count": cart.count(),
    }
    return render(request, "cart/cart.html", context)


@require_POST
def update_cart(request, product_id):
    """Update the quantity of a product in the cart."""
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart = get_cart(request)
    cart.add(product, quantity=qty, replace=True)
    messages.success(request, f"Updated {product.name} to x{qty}.")
    return redirect("cart:cart_detail")


@require_POST
def remove_from_cart(request, product_id):
    """Remove a product from the user's shopping cart."""
    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from cart.")
    return redirect("cart:cart_detail")


@require_POST
def clear_cart(request):
    """Empty the user's shopping cart completely."""
    cart = get_cart(request)
    cart.clear()
    messages.info(request, "Cart cleared.")
    return redirect("cart:cart_detail")


def checkout(request):
    """Display checkout page with cart summary."""
    cart = get_cart(request)
    context = {
        "cart_items": list(cart.items()),
        "subtotal_cents": cart.subtotal_cents(),
        "cart_count": cart.count(),
    }
    return render(request, "cart/checkout.html", context)


@require_GET
def create_checkout_session(request):
    """Create Stripe Checkout session from cart and redirect to Stripe."""
    cart = get_cart(request)
    session, order = Order.create_from_cart(request, cart)

    if not session:
        messages.warning(request, _("Your cart is empty."))
        return redirect("cart:cart_detail")

    return redirect(session.url, code=303)


def success(request):
    """Handle succesful Stripe Payments."""
    session_id = request.GET.get("session_id")
    cart = get_cart(request)
    cart.clear()
    messages.success(request, _("Payment successful! Your order has been placed."))
    return render(request, "cart/success.html", {"session_id": session_id})


def cancel(request):
    """Handle cancelled Stripe Checkout Sessions."""
    return render(request, "cart/cancel.html")


@require_POST
def update_cart_checkout(request, product_id):
    """Update a product's quantity during checkout."""
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart = get_cart(request)
    cart.add(product, quantity=qty, replace=True)
    messages.success(request, f"Updated {product.name} to x{qty}.")
    return redirect("cart:checkout")


@require_POST
def remove_from_cart_checkout(request, product_id):
    """Remove a product from the cart during checkout."""
    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from cart.")
    return redirect("cart:checkout")


@login_required(login_url="account:login")
def order_detail(request, order_id):
    """Display details of a specific order belonging to the logged-in user."""
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "cart/order.html", {"order": order})
