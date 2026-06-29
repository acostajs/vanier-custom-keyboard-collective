import pytest
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils import translation
from django.core import mail
from django.contrib.messages import get_messages

from account.models import Account, Wishlist
from inventory.models import Category, Product
from cart.models import Cart

User = get_user_model()


@pytest.mark.django_db
def test_login_authenticated(test_client: Client) -> None:
    """If the user is already authenticated, accessing login should redirect to account."""
    user = Account.objects.create_user(
        username="loggeduser",
        email="logged@example.com",
        password="password123",
    )
    test_client.force_login(user)

    # Test GET
    response = test_client.get(reverse("account:login"))
    assert response.status_code == 302
    assert response.url == reverse("account:account")

    # Test POST
    response = test_client.post(reverse("account:login"), data={})
    assert response.status_code == 302
    assert response.url == reverse("account:account")


@pytest.mark.django_db
def test_login_submit_session_cart_transfer(
    test_client: Client,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """Logging in via login_submit transfers session cart items to the user's DB cart."""
    _, p1, p2, _ = seed_data
    user = Account.objects.create_user(
        username="cartuser1",
        email="cart1@example.com",
        password="password123",
    )

    # Populates DB cart for the user beforehand to check merging/adding
    cart = Cart.objects.create(account=user)
    cart.add(p1, quantity=1)

    # Add items to the session cart
    session = test_client.session
    session["cart"] = {
        str(p1.id): {"qty": 2},
        str(p2.id): {"qty": 3},
    }
    session.save()

    # Call login_submit POST with valid credentials
    response = test_client.post(
        reverse("account:login_submit"),
        data={
            "username": "cartuser1",
            "password": "password123",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("account:account")

    # Verify session cart is cleared
    assert test_client.session.get("cart") == {}

    # Verify items are added to user's DB cart
    # p1 should have 1 (pre-existing) + 2 (session) = 3
    # p2 should have 3 (session)
    cart_items = cart.cartitem_set.all()
    assert cart_items.filter(product=p1).first().quantity == 3
    assert cart_items.filter(product=p2).first().quantity == 3


@pytest.mark.django_db
def test_login_submit_invalid_credentials(test_client: Client) -> None:
    """Submitting invalid credentials to login_submit returns login page with error."""
    # Test valid structure but wrong credentials
    response = test_client.post(
        reverse("account:login_submit"),
        data={
            "username": "nonexistent",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_registration_session_cart_transfer(
    test_client: Client,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """Registering a new user transfers session cart items to the new DB cart."""
    _, p1, _, _ = seed_data

    # Add items to session cart
    session = test_client.session
    session["cart"] = {
        str(p1.id): {"qty": 2},
    }
    session.save()

    # Register user
    reg_data = {
        "username": "newregistered",
        "first_name": "New",
        "last_name": "User",
        "email": "new@example.com",
        "password1": "SecurePassword123!",
        "password2": "SecurePassword123!",
        "address_line1": "123 Main St",
        "address_line2": "",
        "city": "Montreal",
        "postal_code": "K1A 0B1",
        "country": "Canada",
    }
    response = test_client.post(reverse("account:registration"), data=reg_data)
    assert response.status_code == 302
    assert response.url == reverse("account:login")

    # Verify the user, wishlist, and cart were created
    new_user = Account.objects.get(username="newregistered")
    assert Wishlist.objects.filter(account=new_user).exists()
    new_cart = Cart.objects.get(account=new_user)

    # Verify session cart was cleared and transferred
    assert test_client.session.get("cart") == {}
    assert new_cart.cartitem_set.filter(product=p1).first().quantity == 2


@pytest.mark.django_db
def test_reset_password_get(test_client: Client) -> None:
    """GET request to reset_password displays the form."""
    response = test_client.get(reverse("account:reset_password"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_reset_password_post_valid_english(test_client: Client) -> None:
    """POST request to reset_password sends reset link email in English."""
    Account.objects.create_user(
        username="resetuser",
        email="reset@example.com",
        password="password123",
    )

    with translation.override("en"):
        response = test_client.post(
            reverse("account:reset_password"),
            data={"email": "reset@example.com"},
        )

    assert response.status_code == 302
    assert response.url == reverse("account:login")

    # Check that success message was added
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "password reset link has been sent" in str(messages[0])

    # Check email outbox
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == ["reset@example.com"]
    assert "Password reset" in email.subject
    assert "reset-password" in email.body


@pytest.mark.django_db
def test_reset_password_post_valid_french(test_client: Client) -> None:
    """POST request to reset_password sends reset link email in French if language starts with fr."""
    Account.objects.create_user(
        username="resetuserfr",
        email="resetfr@example.com",
        password="password123",
    )

    with translation.override("fr"):
        response = test_client.post(
            reverse("account:reset_password"),
            data={"email": "resetfr@example.com"},
        )
        assert response.status_code == 302
        assert response.url == reverse("account:login")

    # Check email outbox for French template
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == ["resetfr@example.com"]
    assert "Réinitialisation" in email.subject or "Password reset" in email.subject
    # Check that French template contents are used (e.g. greeting or text)
    # The template name for French is reset_password_email_fr.txt
    # We can just verify it was loaded
    assert "Bonjour" in email.body or "réinitialiser" in email.body


@pytest.mark.django_db
def test_reset_password_post_nonexistent_email(test_client: Client) -> None:
    """POST request to reset_password with non-existent email redirects without sending email."""
    response = test_client.post(
        reverse("account:reset_password"),
        data={"email": "notfound@example.com"},
    )
    assert response.status_code == 302
    assert response.url == reverse("account:login")
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_reset_password_submit_invalid_uidb64(test_client: Client) -> None:
    """Accessing reset_password_submit with invalid uidb64 redirects to reset_password."""
    response = test_client.get(
        reverse(
            "account:reset_password_submit",
            kwargs={"uidb64": "invalid-b64-value!!!", "token": "some-token"},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse("account:reset_password")

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "link is invalid" in str(messages[0])


@pytest.mark.django_db
def test_reset_password_submit_invalid_token(test_client: Client) -> None:
    """Accessing reset_password_submit with valid uidb64 but invalid token redirects to reset_password."""
    user = Account.objects.create_user(
        username="resetuser2",
        email="reset2@example.com",
        password="password123",
    )
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    response = test_client.get(
        reverse(
            "account:reset_password_submit",
            kwargs={"uidb64": uidb64, "token": "invalid-token"},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse("account:reset_password")


@pytest.mark.django_db
def test_reset_password_submit_get_valid(test_client: Client) -> None:
    """Accessing reset_password_submit GET with valid uidb64 and token renders submit page."""
    user = Account.objects.create_user(
        username="resetuser3",
        email="reset3@example.com",
        password="password123",
    )
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = test_client.get(
        reverse(
            "account:reset_password_submit",
            kwargs={"uidb64": uidb64, "token": token},
        )
    )
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_reset_password_submit_post_invalid(test_client: Client) -> None:
    """Accessing reset_password_submit POST with valid uidb64/token but invalid passwords re-renders page."""
    user = Account.objects.create_user(
        username="resetuser4",
        email="reset4@example.com",
        password="password123",
    )
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = test_client.post(
        reverse(
            "account:reset_password_submit",
            kwargs={"uidb64": uidb64, "token": token},
        ),
        data={
            "new_password1": "short",
            "new_password2": "mismatch",
        },
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_reset_password_submit_post_valid(test_client: Client) -> None:
    """Accessing reset_password_submit POST with valid passwords redirects to login and updates password."""
    user = Account.objects.create_user(
        username="resetuser5",
        email="reset5@example.com",
        password="password123",
    )
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = test_client.post(
        reverse(
            "account:reset_password_submit",
            kwargs={"uidb64": uidb64, "token": token},
        ),
        data={
            "new_password1": "SecureNewPassword123!",
            "new_password2": "SecureNewPassword123!",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("account:login")

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "password has been reset" in str(messages[0])


@pytest.mark.django_db
def test_wishlist_detail_view(
    test_client: Client,
    wishlist_setup: tuple[Wishlist, Product, Product],
) -> None:
    """GET wishlist_detail returns the user's wishlist and its products."""
    wishlist, p1, p2 = wishlist_setup
    p1.image = "products/test1.png"
    p1.save()
    p2.image = "products/test2.png"
    p2.save()
    wishlist.add(p1)
    wishlist.add(p2)

    test_client.force_login(wishlist.account)
    response = test_client.get(reverse("account:wishlist_detail"))
    assert response.status_code == 200
    assert response.context["wishlist"] == wishlist
    assert list(response.context["wishlist_products"]) == [p1, p2]


@pytest.mark.django_db
def test_add_to_wishlist_view(
    test_client: Client,
    wishlist_setup: tuple[Wishlist, Product, Product],
) -> None:
    """POST to add_to_wishlist adds product to wishlist and redirects to product detail."""
    wishlist, p1, _ = wishlist_setup

    test_client.force_login(wishlist.account)
    response = test_client.post(
        reverse("account:add_to_wishlist", kwargs={"product_id": p1.id})
    )
    assert response.status_code == 302
    assert response.url == reverse("inventory:product", kwargs={"product_id": p1.id})
    assert wishlist.product.filter(id=p1.id).exists()


@pytest.mark.django_db
def test_remove_from_wishlist_view(
    test_client: Client,
    wishlist_setup: tuple[Wishlist, Product, Product],
) -> None:
    """POST to remove_from_wishlist removes product from wishlist and redirects to wishlist_detail."""
    wishlist, p1, _ = wishlist_setup
    wishlist.add(p1)

    test_client.force_login(wishlist.account)
    response = test_client.post(
        reverse("account:remove_from_wishlist", kwargs={"product_id": p1.id})
    )
    assert response.status_code == 302
    assert response.url == reverse("account:wishlist_detail")
    assert not wishlist.product.filter(id=p1.id).exists()


@pytest.mark.django_db
def test_clear_wishlist_view(
    test_client: Client,
    wishlist_setup: tuple[Wishlist, Product, Product],
) -> None:
    """POST to clear_wishlist clears wishlist and redirects to wishlist_detail."""
    wishlist, p1, p2 = wishlist_setup
    wishlist.add(p1)
    wishlist.add(p2)

    test_client.force_login(wishlist.account)
    response = test_client.post(reverse("account:clear_wishlist"))
    assert response.status_code == 302
    assert response.url == reverse("account:wishlist_detail")
    assert wishlist.count() == 0


@pytest.mark.django_db
def test_transfer_to_cart_view(
    test_client: Client,
    wishlist_setup: tuple[Wishlist, Product, Product],
) -> None:
    """POST to transfer_to_cart transfers wishlist products to DB cart and clears wishlist."""
    wishlist, p1, p2 = wishlist_setup
    p1.image = "products/test1.png"
    p1.save()
    p2.image = "products/test2.png"
    p2.save()
    wishlist.add(p1)
    wishlist.add(p2)

    user = wishlist.account
    test_client.force_login(user)

    # Call transfer_to_cart view (argument product_id is required in URL but unused in function)
    response = test_client.post(
        reverse("account:transfer_to_cart", kwargs={"product_id": p1.id})
    )
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    # Verify wishlist is empty
    assert wishlist.count() == 0

    # Verify DB cart contains both products
    cart = Cart.objects.get(account=user)
    cart_products = [item.product for item in cart.cartitem_set.all()]
    assert p1 in cart_products
    assert p2 in cart_products
