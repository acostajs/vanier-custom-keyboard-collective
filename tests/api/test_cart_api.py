import pytest
import requests
from django.urls import reverse
from unittest.mock import patch


@pytest.mark.django_db
def test_cart_lifecycle_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    session = requests.Session()

    # 1. Verify cart is initially empty
    url = f"{live_server.url}{reverse('cart:cart_detail')}"
    response = session.get(url, allow_redirects=True)
    assert response.status_code == 200
    assert "Your cart is empty" in response.text

    # Extract CSRF token from cookies
    csrf_token = session.cookies.get("csrftoken")

    # 2. Add product to cart with custom quantity (2)
    add_url = f"{live_server.url}{reverse('cart:add_to_cart', args=[p1.id])}"
    response = session.post(
        add_url,
        data={"quantity": "2", "csrfmiddlewaretoken": csrf_token},
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert p1.name in response.text
    # Unit price $150.00, 10% discount -> $135.00 * 2 = $270.00 subtotal
    assert "$270.00" in response.text

    # 3. Update quantity to 3
    csrf_token = session.cookies.get("csrftoken")
    update_url = f"{live_server.url}{reverse('cart:update_cart', args=[p1.id])}"
    response = session.post(
        update_url,
        data={"quantity": "3", "csrfmiddlewaretoken": csrf_token},
        allow_redirects=True,
    )
    assert response.status_code == 200
    # $135.00 * 3 = $405.00 subtotal
    assert "$405.00" in response.text

    # 4. Remove product from cart
    csrf_token = session.cookies.get("csrftoken")
    remove_url = f"{live_server.url}{reverse('cart:remove_from_cart', args=[p1.id])}"
    response = session.post(
        remove_url,
        data={"csrfmiddlewaretoken": csrf_token},
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert "Your cart is empty" in response.text


@pytest.mark.django_db
def test_cart_clear_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    session = requests.Session()

    session.get(f"{live_server.url}{reverse('cart:cart_detail')}")
    csrf_token = session.cookies.get("csrftoken")

    # Add item
    add_url = f"{live_server.url}{reverse('cart:add_to_cart', args=[p1.id])}"
    session.post(
        add_url,
        data={"quantity": "1", "csrfmiddlewaretoken": csrf_token},
    )

    # Clear cart
    csrf_token = session.cookies.get("csrftoken")
    clear_url = f"{live_server.url}{reverse('cart:clear_cart')}"
    response = session.post(
        clear_url,
        data={"csrfmiddlewaretoken": csrf_token},
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert "Your cart is empty" in response.text


@pytest.mark.django_db
@patch("stripe.checkout.Session.create")
def test_checkout_and_session_creation_api(mock_stripe_create, live_server, seed_data):
    category, p1, p2, p3 = seed_data
    session = requests.Session()

    class MockSession:
        url = "https://checkout.stripe.com/pay/cs_test_12345"
        id = "cs_test_12345"

    mock_stripe_create.return_value = MockSession()

    session.get(f"{live_server.url}{reverse('cart:cart_detail')}")
    csrf_token = session.cookies.get("csrftoken")

    add_url = f"{live_server.url}{reverse('cart:add_to_cart', args=[p1.id])}"
    session.post(
        add_url,
        data={"quantity": "1", "csrfmiddlewaretoken": csrf_token},
    )

    # Verify checkout page loads
    checkout_url = f"{live_server.url}{reverse('cart:checkout')}"
    response = session.get(checkout_url)
    assert response.status_code == 200
    assert p1.name in response.text

    # Request Stripe Checkout Session
    create_session_url = f"{live_server.url}{reverse('cart:create_checkout_session')}"
    response = session.get(create_session_url, allow_redirects=False)
    # Redirects to Stripe (302/303 See Other)
    assert response.status_code in [302, 303]
    assert (
        response.headers["Location"] == "https://checkout.stripe.com/pay/cs_test_12345"
    )


@pytest.mark.django_db
def test_checkout_success_cancel_pages_api(live_server):
    session = requests.Session()
    success_url = f"{live_server.url}{reverse('cart:success')}?session_id=cs_test"
    response = session.get(success_url)
    assert response.status_code == 200
    assert "successful" in response.text.lower()

    cancel_url = f"{live_server.url}{reverse('cart:cancel')}"
    response = session.get(cancel_url)
    assert response.status_code == 200
