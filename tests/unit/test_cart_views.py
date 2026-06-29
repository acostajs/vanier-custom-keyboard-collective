import pytest
import os
from unittest.mock import patch, MagicMock
from django.test.client import Client
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.messages import get_messages

from account.models import Account
from inventory.models import Category, Product
from cart.models import Order, Cart
from cart.session_cart import SessionCart
from cart.context_processors import cart_info


@pytest.mark.django_db
def test_cart_info_context_processor(test_client: Client) -> None:
    """Test cart_info context processor return values under normal and error conditions."""
    request = RequestFactory().get("/")
    request.session = test_client.session

    # Normal anonymous user case
    context = cart_info(request)
    assert context == {"cart_count": 0}

    # Exception fallback case
    with patch(
        "cart.context_processors.get_cart", side_effect=Exception("Mock exception")
    ):
        context = cart_info(request)
        assert context == {"cart_count": 0}


@pytest.mark.django_db
def test_session_cart_items_skips_invalid_product(test_client: Client) -> None:
    """SessionCart.items should skip product IDs that do not exist in the database."""
    session = test_client.session
    session["cart"] = {"99999": {"qty": 2}}
    session.save()

    request = RequestFactory().get("/")
    request.session = session
    cart = SessionCart(request)

    items = list(cart.items())
    assert len(items) == 0


@pytest.mark.django_db
def test_order_fulfill_method(order_user: Account) -> None:
    """Directly test Order.fulfill method sets fields and saves."""
    order = Order.objects.create(
        user=order_user,
        total_cents=5000,
    )
    order.fulfill(
        name="John Doe",
        email="john@example.com",
        payment_id="pi_fulfilled",
        total_cents=5000,
        billing_address_line1="123 Bill St",
        billing_address_line2="Apt 1",
        billing_city="Toronto",
        billing_postal_code="M1M 1M1",
        billing_country="Canada",
        shipping_address_line1="456 Ship Rd",
        shipping_address_line2="",
        shipping_city="Vancouver",
        shipping_postal_code="V2V 2V2",
        shipping_country="Canada",
    )
    order.refresh_from_db()
    assert order.name == "John Doe"
    assert order.email == "john@example.com"
    assert order.payment_id == "pi_fulfilled"
    assert order.billing_address_line1 == "123 Bill St"
    assert order.billing_address_line2 == "Apt 1"
    assert order.billing_city == "Toronto"
    assert order.billing_postal_code == "M1M 1M1"
    assert order.billing_country == "Canada"
    assert order.shipping_address_line1 == "456 Ship Rd"
    assert order.shipping_address_line2 == ""
    assert order.shipping_city == "Vancouver"
    assert order.shipping_postal_code == "V2V 2V2"
    assert order.shipping_country == "Canada"


@pytest.mark.django_db
def test_order_create_from_cart_empty() -> None:
    """create_from_cart returns (None, None) for empty carts."""
    request = RequestFactory().get("/")
    request.user = Account.objects.create_user(
        username="emptyuser", email="empty@example.com", password="pw"
    )
    session = {}
    request.session = session
    cart = SessionCart(request)

    session_obj, order = Order.create_from_cart(request, cart)
    assert session_obj is None
    assert order is None


@pytest.mark.django_db
@patch("stripe.checkout.Session.create")
def test_order_create_from_cart_authenticated(
    mock_stripe_create: MagicMock,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """create_from_cart sets order.user and customer details for authenticated users."""
    _, p1, _, _ = seed_data
    p1.image = "products/test.png"
    p1.save()

    user = Account.objects.create_user(
        username="authuser",
        email="authuser@example.com",
        password="password123",
    )
    cart = Cart.objects.create(account=user)
    cart.add(p1, quantity=2)

    request = RequestFactory().get("/")
    request.user = user

    class MockStripeSession:
        id = "cs_test_auth"
        url = "https://checkout.stripe.com/pay/cs_test_auth"

    mock_stripe_create.return_value = MockStripeSession()

    stripe_session, order = Order.create_from_cart(request, cart)
    assert order.user == user
    assert stripe_session.id == "cs_test_auth"

    # Verify checkout args
    args, kwargs = mock_stripe_create.call_args
    assert kwargs["customer_email"] == "authuser@example.com"
    assert kwargs["billing_address_collection"] == "auto"


@pytest.mark.django_db
def test_create_checkout_session_empty_cart_redirect(test_client: Client) -> None:
    """Accessing create_checkout_session with empty cart redirects to cart detail page."""
    response = test_client.get(reverse("cart:create_checkout_session"))
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "cart is empty" in str(messages[0])


@pytest.mark.django_db
def test_update_cart_checkout_view(
    test_client: Client,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """POST to update_cart_checkout replaces item quantity and redirects to checkout."""
    _, p1, _, _ = seed_data
    session = test_client.session
    session["cart"] = {str(p1.id): {"qty": 1}}
    session.save()

    response = test_client.post(
        reverse("cart:update_cart_checkout", kwargs={"product_id": p1.id}),
        data={"quantity": "3"},
    )
    assert response.status_code == 302
    assert response.url == reverse("cart:checkout")

    cart = SessionCart(response.wsgi_request)
    assert cart.count() == 3


@pytest.mark.django_db
def test_remove_from_cart_checkout_view(
    test_client: Client,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """POST to remove_from_cart_checkout deletes product from cart and redirects to checkout."""
    _, p1, _, _ = seed_data
    session = test_client.session
    session["cart"] = {str(p1.id): {"qty": 1}}
    session.save()

    response = test_client.post(
        reverse("cart:remove_from_cart_checkout", kwargs={"product_id": p1.id})
    )
    assert response.status_code == 302
    assert response.url == reverse("cart:checkout")

    cart = SessionCart(response.wsgi_request)
    assert cart.count() == 0


@pytest.mark.django_db
def test_order_detail_view(test_client: Client, order_user: Account) -> None:
    """order_detail view shows the requested order if it belongs to user, else 404."""
    order = Order.objects.create(
        user=order_user,
        total_cents=3000,
        payment_id="pi_user_order",
    )

    test_client.force_login(order_user)

    # 1. Successful access to own order
    response = test_client.get(
        reverse("cart:order_detail", kwargs={"order_id": order.id})
    )
    assert response.status_code == 200
    assert response.context["order"] == order

    # 2. 404 access to another user's order
    other_user = Account.objects.create_user(
        username="otheruser", email="other@example.com", password="pw"
    )
    other_order = Order.objects.create(
        user=other_user,
        total_cents=1000,
        payment_id="pi_other_order",
    )
    response = test_client.get(
        reverse("cart:order_detail", kwargs={"order_id": other_order.id})
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_stripe_webhook_invalid_signature(test_client: Client) -> None:
    """stripe_webhook returns 400 when Stripe signature verification fails."""
    # Temporarily set a mock secret
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_mock"}):
        response = test_client.post(
            reverse("cart:fulfill_stripe_checkout_webhook"),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_sig",
        )
    assert response.status_code == 400


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_stripe_webhook_completion_authenticated(
    mock_construct: MagicMock,
    test_client: Client,
    order_user: Account,
) -> None:
    """stripe_webhook handles checkout.session.completed for an authenticated user."""
    order = Order.objects.create(
        user=order_user,
        total_cents=4500,
    )

    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(order.id),
                "payment_intent": "pi_webhook_auth",
            }
        },
    }

    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_mock"}):
        response = test_client.post(
            reverse("cart:fulfill_stripe_checkout_webhook"),
            HTTP_STRIPE_SIGNATURE="mock_sig",
        )

    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "paid"
    assert order.payment_id == "pi_webhook_auth"
    assert order.billing_address_line1 == order_user.address_line1


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_stripe_webhook_completion_guest(
    mock_construct: MagicMock,
    test_client: Client,
) -> None:
    """stripe_webhook handles checkout.session.completed for a guest checkout."""
    order = Order.objects.create(
        user=None,
        total_cents=2500,
    )

    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(order.id),
                "payment_intent": "pi_webhook_guest",
                "customer_details": {
                    "name": "Guest Customer",
                    "email": "guest@example.com",
                    "address": {
                        "line1": "100 Guest St",
                        "line2": "Suite B",
                        "city": "Ottawa",
                        "postal_code": "K2K 2K2",
                        "country": "CA",
                    },
                },
                "collected_information": {
                    "shipping_details": {
                        "address": {
                            "line1": "200 Ship Ave",
                            "line2": "",
                            "city": "Ottawa",
                            "postal_code": "K2K 2K2",
                            "country": "CA",
                        }
                    }
                },
            }
        },
    }

    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_mock"}):
        response = test_client.post(
            reverse("cart:fulfill_stripe_checkout_webhook"),
            HTTP_STRIPE_SIGNATURE="mock_sig",
        )

    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "paid"
    assert order.payment_id == "pi_webhook_guest"
    assert order.billing_address_line1 == "100 Guest St"
    assert order.billing_address_line2 == "Suite B"
    assert order.shipping_address_line1 == "200 Ship Ave"


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_stripe_webhook_nonexistent_order(
    mock_construct: MagicMock,
    test_client: Client,
) -> None:
    """stripe_webhook returns 404 when the order ID in the event does not exist."""
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "999999",
                "payment_intent": "pi_none",
            }
        },
    }

    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_mock"}):
        response = test_client.post(
            reverse("cart:fulfill_stripe_checkout_webhook"),
            HTTP_STRIPE_SIGNATURE="mock_sig",
        )
    assert response.status_code == 404


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_stripe_webhook_failure_or_cancelled(
    mock_construct: MagicMock,
    test_client: Client,
    order_user: Account,
) -> None:
    """stripe_webhook marks the order as cancelled on failure/cancel events."""
    order = Order.objects.create(
        user=order_user,
        payment_id="pi_failed_payment",
        total_cents=1000,
    )

    mock_construct.return_value = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_failed_payment",
            }
        },
    }

    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_mock"}):
        response = test_client.post(
            reverse("cart:fulfill_stripe_checkout_webhook"),
            HTTP_STRIPE_SIGNATURE="mock_sig",
        )

    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "cancelled"


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_stripe_webhook_failure_nonexistent_order(
    mock_construct: MagicMock,
    test_client: Client,
) -> None:
    """stripe_webhook returns 200 when payment failure event references a non-existent payment intent."""
    mock_construct.return_value = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_nonexistent",
            }
        },
    }

    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_mock"}):
        response = test_client.post(
            reverse("cart:fulfill_stripe_checkout_webhook"),
            HTTP_STRIPE_SIGNATURE="mock_sig",
        )
    assert response.status_code == 200
