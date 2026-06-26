import pytest
from playwright.sync_api import Page


@pytest.mark.django_db
def test_homepage_health(page: Page, live_server) -> None:
    """
    Verify the root homepage is healthy, redirects correctly to the language path,
    and returns an OK status response with visible available products.
    """
    response = page.goto(live_server.url)
    assert response is not None
    assert response.ok
    assert response.status == 200
    assert "/en/" in page.url
    
    # Check that "Available Products" is present on the page
    assert page.locator("h2:has-text('Available Products')").is_visible()


@pytest.mark.django_db
def test_category_page_health(page: Page, live_server, seed_data) -> None:
    """
    Verify the category page loads and displays the category name.
    """
    category, _, _, _ = seed_data
    url = f"{live_server.url}/en/category/{category.id}/"
    response = page.goto(url)
    assert response is not None
    assert response.ok
    assert response.status == 200
    
    # Verify the category heading is visible
    assert page.locator(f"h1:has-text('{category.name}')").is_visible()


@pytest.mark.django_db
def test_product_page_health(page: Page, live_server, seed_data) -> None:
    """
    Verify the product page loads and displays the product name.
    """
    _, product, _, _ = seed_data
    url = f"{live_server.url}/en/product/{product.id}/"
    response = page.goto(url)
    assert response is not None
    assert response.ok
    assert response.status == 200
    
    # Verify the product heading is visible
    assert page.locator(f"h2:has-text('{product.name}')").is_visible()


@pytest.mark.django_db
def test_login_page_health(page: Page, live_server) -> None:
    """
    Verify the login page loads and contains the login form.
    """
    url = f"{live_server.url}/en/account/login/"
    response = page.goto(url)
    assert response is not None
    assert response.ok
    assert response.status == 200
    
    # Check for Login heading and form input fields
    assert page.locator("h3:has-text('Login')").is_visible()
    assert page.locator("input[name='username']").is_visible()
    assert page.locator("input[name='password']").is_visible()


@pytest.mark.django_db
def test_registration_page_health(page: Page, live_server) -> None:
    """
    Verify the registration page loads and contains the registration form.
    """
    url = f"{live_server.url}/en/account/registration/"
    response = page.goto(url)
    assert response is not None
    assert response.ok
    assert response.status == 200
    
    # Check for Registration heading and form input fields
    assert page.locator("h3:has-text('Create an Account')").is_visible()
    assert page.locator("input[name='username']").is_visible()
    assert page.locator("input[name='email']").is_visible()


@pytest.mark.django_db
def test_cart_page_health(page: Page, live_server) -> None:
    """
    Verify the cart page loads and displays the empty cart message or table headers.
    """
    url = f"{live_server.url}/en/cart/"
    response = page.goto(url)
    assert response is not None
    assert response.ok
    assert response.status == 200
    
    # Verify the cart heading is visible
    assert page.locator("h2:has-text('Your Cart')").is_visible()
