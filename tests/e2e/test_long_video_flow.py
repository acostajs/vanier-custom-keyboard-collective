import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.registration_page import RegistrationPage
from pages.login_page import LoginPage
from pages.account_page import AccountPage
from pages.wishlist_page import WishlistPage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """
    Override browser context arguments for this module to enable video recording
    in WebM format with a standard viewport size.
    """
    return {
        **browser_context_args,
        "record_video_dir": "tests/e2e/videos/",
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """
    Override browser launch arguments for this module to introduce a 1-second delay
    (slow_mo=1000ms) between actions.
    """
    return {
        **browser_type_launch_args,
        "slow_mo": 1000,
    }


@pytest.mark.django_db
def test_long_user_flow_with_video(
    page: Page, live_server, seed_data: tuple, fake_user: dict[str, str]
) -> None:
    """
    Perform a long end-to-end user journey:
    1. Navigate to the Homepage.
    2. Register a new user.
    3. Log in with the newly registered user.
    4. View Wishlist and verify it's empty.
    5. Navigate back to Homepage and browse "Keyboards" category.
    6. Select "Keychron Q1" and add 2 units to the cart.
    7. Search for "MX Master".
    8. Select "MX Master 3S" from search results.
    9. Add "MX Master 3S" to the wishlist.
    10. Go to Wishlist and verify "MX Master 3S" is present.
    11. Transfer "MX Master 3S" from wishlist to the cart.
    12. Verify both products exist in the cart, and update quantities.
    13. Clear the cart.
    14. Go to Account dashboard and log out.
    """
    home = HomePage(page)
    reg_page = RegistrationPage(page)
    login_page = LoginPage(page)
    account_page = AccountPage(page)
    wishlist_page = WishlistPage(page)
    cart_page = CartPage(page)

    # 1. Navigate to Homepage
    home.navigate(live_server.url)

    # 2. Click "Register" and register a new user
    home.register_link.click()
    assert "/account/registration/" in page.url
    reg_page.register(fake_user)

    # 3. Log in with registered credentials
    assert "/account/login/" in page.url
    login_page.login(fake_user["username"], fake_user["password1"])
    assert page.url.endswith("/account/")
    assert account_page.get_username() == fake_user["username"]

    # 4. View Wishlist and verify it's empty
    account_page.wishlist_link.click()
    assert "/account/wishlist/" in page.url
    assert wishlist_page.get_wishlist_item_count() == 0

    # 5. Navigate to Homepage and click on "Keyboards" category
    wishlist_page.brand_link.click()
    home.click_category_by_name("Keyboards")

    # 6. Click on "Keychron Q1" and add 2 units to the cart
    home.click_product_by_name("Keychron Q1")
    product_page = ProductPage(page)
    assert product_page.get_product_name() == "Keychron Q1"
    product_page.add_to_cart(qty=2)

    # Verify redirection to the cart page
    assert "/cart/" in page.url
    assert cart_page.get_cart_item_count() == 1
    assert cart_page.get_subtotal() == "$300.00"

    # 7. Search for "MX Master" from the cart page
    cart_page.search_for("MX Master")

    # 8. Click on "MX Master 3S" from search results
    home.click_product_by_name("MX Master 3S")
    assert product_page.get_product_name() == "MX Master 3S"

    # 9. Add "MX Master 3S" to wishlist
    product_page.add_to_wishlist()
    # Adding to wishlist redirects back to product details with success alert
    assert "Added MX Master 3S to wishlist." in product_page.get_alert_messages()

    # 10. Go to Wishlist page and verify "MX Master 3S" is present
    product_page.wishlist_link.click()
    assert "/account/wishlist/" in page.url
    assert wishlist_page.get_wishlist_item_count() == 1
    assert wishlist_page.get_wishlist_item_by_name("MX Master 3S").is_visible()

    # 11. Transfer "MX Master 3S" from wishlist to the cart
    wishlist_page.transfer_to_cart("MX Master 3S")

    # 12. Verify both products exist in the cart
    assert "/cart/" in page.url
    assert cart_page.get_cart_item_count() == 2
    assert cart_page.get_subtotal() == "$399.00"

    # Update quantity of "MX Master 3S" to 3
    cart_page.update_item_quantity("MX Master 3S", qty=3)
    assert cart_page.get_subtotal() == "$597.00"

    # 13. Clear the cart
    cart_page.clear_cart()
    assert cart_page.empty_cart_message.is_visible()
    assert cart_page.get_cart_item_count() == 0

    # 14. Go to Account dashboard and log out
    cart_page.account_link.click()
    assert page.url.endswith("/account/")
    account_page.logout()
    assert "/account/login/" in page.url
