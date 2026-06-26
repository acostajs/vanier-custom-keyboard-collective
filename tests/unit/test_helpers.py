import pytest
from cart.templatetags.currency import cents_to_dollars
from cart.helpers import parse_quantity, get_cart
from cart.session_cart import SessionCart
from cart.models import Cart
from account.models import Account


class MockUser:
    def __init__(self, is_authenticated=False, email="user@example.com"):
        self.is_authenticated = is_authenticated
        self.email = email
        self.id = 1


class MockRequest:
    def __init__(self, user=None, post_data=None, session=None):
        self.user = user or MockUser(is_authenticated=False)
        self.POST = post_data or {}
        self.session = session if session is not None else {}


def test_cents_to_dollars():
    """
    Unit tests for cents_to_dollars template filter.
    """
    # Valid integers
    assert cents_to_dollars(100) == "$1.00"
    assert cents_to_dollars(1500) == "$15.00"
    assert cents_to_dollars(50) == "$0.50"
    assert cents_to_dollars(0) == "$0.00"

    # Valid string representation
    assert cents_to_dollars("2500") == "$25.00"

    # Invalid values should return $0.00
    assert cents_to_dollars("invalid") == "$0.00"
    assert cents_to_dollars(None) == "$0.00"
    assert cents_to_dollars([]) == "$0.00"


def test_parse_quantity():
    """
    Unit tests for parse_quantity helper function.
    """
    # Normal POST value
    req = MockRequest(post_data={"quantity": "3"})
    assert parse_quantity(req) == 3

    # Missing quantity defaults to 1
    req = MockRequest(post_data={})
    assert parse_quantity(req) == 1

    # Non-numeric quantity defaults to 1
    req = MockRequest(post_data={"quantity": "invalid"})
    assert parse_quantity(req) == 1

    # Negative quantity clamped to 1
    req = MockRequest(post_data={"quantity": "-5"})
    assert parse_quantity(req) == 1


@pytest.mark.django_db
def test_get_cart_authenticated():
    """
    get_cart returns a DB Cart when user is authenticated.
    """
    user = Account.objects.create_user(
        username="carthelperuser",
        email="helper@example.com",
        password="pass1234",
    )
    req = MockRequest(user=user)

    cart = get_cart(req)
    assert isinstance(cart, Cart)
    assert cart.account == user


def test_get_cart_anonymous():
    """
    get_cart returns a SessionCart when user is anonymous.
    """
    req = MockRequest(user=MockUser(is_authenticated=False), session={})
    cart = get_cart(req)
    assert isinstance(cart, SessionCart)
