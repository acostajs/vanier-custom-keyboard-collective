from .models import Cart
from .session_cart import SessionCart


def get_cart(request):
    """Helper function to determine which cart to use."""
    if request.user.is_authenticated:
        account = request.user
        cart, _ = Cart.objects.get_or_create(account=account)
        return cart
    else:
        return SessionCart(request)


def parse_quantity(request):
    """Helper function to determine how many items we have."""
    try:
        qty = int(request.POST.get("quantity", "1"))
    except (ValueError, TypeError):
        qty = 1
    return max(1, qty)
