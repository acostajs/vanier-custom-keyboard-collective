from cart.helpers import get_cart


def cart_info(request):
    """
    Get the total cart count from session or database cart consistently.
    """
    try:
        cart = get_cart(request)
        count = cart.count()
    except Exception:
        count = 0
    return {"cart_count": count}
