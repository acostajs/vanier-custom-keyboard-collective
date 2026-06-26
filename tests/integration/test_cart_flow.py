import pytest
from django.urls import reverse
from unittest.mock import patch


@pytest.mark.django_db
def test_catalog_search_and_filter(test_client, seed_data):
    """
    Integration test for catalog searching and filtering views.
    """
    category, p1, p2, p3 = seed_data

    # 1. Access the main catalog index
    response = test_client.get(reverse("inventory:index"))
    assert response.status_code == 200
    assert "Keychron Q1" in response.content.decode()

    # 2. Search for "MX Master"
    response = test_client.get(reverse("inventory:results"), {"search": "MX Master"})
    assert response.status_code == 200
    content = response.content.decode()
    assert "MX Master 3S" in content
    assert "Keychron Q1" not in content

    # 3. Filter products on category page by discount
    response = test_client.get(
        reverse("inventory:category", args=[category.id]),
        {"filter_criteria": ["discount_percentage"]},
    )
    assert response.status_code == 200
    content = response.content.decode()
    # Keychron Q1 is discounted (10%) -> should be present
    assert "Keychron Q1" in content
    # MX Master 3S has no discount -> should not be present
    assert "MX Master 3S" not in content


@pytest.mark.django_db
def test_guest_shopping_cart_flow(test_client, seed_data):
    """
    Integration test for the guest shopping cart flow using TestClient.
    """
    category, p1, p2, p3 = seed_data

    # 1. Verify cart is initially empty
    response = test_client.get(reverse("cart:cart_detail"))
    assert response.status_code == 200
    assert "Your cart is empty" in response.content.decode()

    # 2. Add product to cart with custom quantity (2)
    response = test_client.post(
        reverse("cart:add_to_cart", args=[p1.id]),
        {"quantity": "2"},
    )
    # Redirects to cart_detail
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    # Verify session state contains the correct item and quantity
    session = test_client.session
    assert session["cart"] == {str(p1.id): {"qty": 2}}

    # 3. Verify cart detail page displays the product
    response = test_client.get(reverse("cart:cart_detail"))
    assert response.status_code == 200
    assert p1.name in response.content.decode()

    # 4. Update cart item quantity (3)
    response = test_client.post(
        reverse("cart:update_cart", args=[p1.id]),
        {"quantity": "3"},
    )
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    # Verify session updated
    session = test_client.session
    assert session["cart"] == {str(p1.id): {"qty": 3}}

    # 5. Clear the cart
    response = test_client.post(reverse("cart:clear_cart"))
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    # Verify session cart is cleared
    session = test_client.session
    assert session["cart"] == {}


@pytest.mark.django_db
@patch("stripe.checkout.Session.create")
def test_checkout_and_session_creation(mock_stripe_create, test_client, seed_data):
    """
    Integration test for cart checkout and Stripe checkout session creation.
    """
    category, p1, p2, p3 = seed_data

    # Mock the stripe session creation response
    class MockSession:
        url = "https://checkout.stripe.com/pay/cs_test_12345"
        id = "cs_test_12345"

    mock_stripe_create.return_value = MockSession()

    # 1. Add product to cart first (checkout requires a non-empty cart)
    test_client.post(
        reverse("cart:add_to_cart", args=[p1.id]),
        {"quantity": "1"},
    )

    # 2. Access checkout overview page
    response = test_client.get(reverse("cart:checkout"))
    assert response.status_code == 200
    assert p1.name in response.content.decode()

    # 3. Request a Stripe checkout session
    response = test_client.get(reverse("cart:create_checkout_session"))

    # Verify redirect to Stripe Checkout URL (Django's redirect yields 302 status code)
    assert response.status_code == 302
    assert response.url == "https://checkout.stripe.com/pay/cs_test_12345"

    # Verify Stripe was called with the correct parameters
    mock_stripe_create.assert_called_once()
    called_kwargs = mock_stripe_create.call_args[1]
    assert called_kwargs["mode"] == "payment"
    assert len(called_kwargs["line_items"]) == 1
    assert called_kwargs["line_items"][0]["quantity"] == 1
    assert (
        called_kwargs["line_items"][0]["price_data"]["unit_amount"]
        == p1.get_discounted_price()
    )
