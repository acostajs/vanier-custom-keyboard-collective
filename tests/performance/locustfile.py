import random
import re
import uuid
from locust import HttpUser, between, task


class KeyboardCollectiveUser(HttpUser):
    """Simulates real-world traffic by dynamically creating unique users

    and driving them through browsing, wishlisting, and checkout lifecycles.
    """

    wait_time = between(1.5, 5)

    def on_start(self) -> None:
        """Runs immediately when a virtual user is spawned."""
        self.product_urls: list[str] = []
        self.category_urls: list[str] = []
        self.csrf_token: str = ""

        # 1. Initialize clean, unique user identity state properties
        unique_id: str = uuid.uuid4().hex[:8]
        self.username: str = f"user_{unique_id}"
        self.email: str = f"{self.username}@example.com"
        self.password: str = "E2Epassword123!"

        # 2. Execute structured account lifecycle steps sequentially
        self.register_account()
        self.login_account()
        self.discover_products()

    def register_account(self) -> None:
        """Handles the complete step-by-step registration flow for a new user."""
        response = self.client.get("/en/account/registration/")
        csrf_token: str = self.extract_csrf(response.text)

        if not csrf_token:
            return

        payload: dict[str, str] = {
            "username": self.username,
            "first_name": "Perf",
            "last_name": "User",
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
            "address_line1": "123 Performance Way",
            "address_line2": "",
            "city": "PerfCity",
            "postal_code": "12345",
            "country": "Canada",
            "csrfmiddlewaretoken": response.cookies.get("csrftoken", csrf_token),
        }
        headers: dict[str, str] = {"Referer": f"{self.host}/en/account/registration/"}
        self.client.post(
            "/en/account/registration/",
            data=payload,
            headers=headers,
            name="/en/account/registration/",
        )

    def login_account(self) -> None:
        """Handles the separate authentication sequence for the created user session."""
        response = self.client.get("/en/account/login/")
        csrf_token: str = self.extract_csrf(response.text)

        if not csrf_token:
            return

        payload: dict[str, str] = {
            "username": self.username,
            "password": self.password,
            "csrfmiddlewaretoken": response.cookies.get("csrftoken", csrf_token),
        }
        headers: dict[str, str] = {"Referer": f"{self.host}/en/account/login/"}
        self.client.post(
            "/en/account/login_submit/",
            data=payload,
            headers=headers,
            name="/en/account/login_submit/",
        )

    def discover_products(self) -> None:
        """Scrapes the localized shop catalog view to collect active product and category item layers."""
        response = self.client.get("/en/")
        if response.status_code == 200:
            found_products: list[str] = re.findall(
                r'href="((?:/[a-z]{2})?/product/\d+/)"', response.text
            )
            if found_products:
                self.product_urls = list(set(found_products))

            found_categories: list[str] = re.findall(
                r'href="((?:/[a-z]{2})?/category/\d+/)"', response.text
            )
            if found_categories:
                self.category_urls = list(set(found_categories))

    def extract_csrf(self, html_text: str) -> str:
        """Helper utility using regex parsing to pull csrf token parameters out of layouts."""
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html_text)
        return match.group(1) if match else ""

    @task(4)
    def browse_catalog(self) -> None:
        """High frequency: Simulates general exploration of indexes and main covers."""
        self.client.get("/en/")
        if self.category_urls:
            target_category: str = random.choice(self.category_urls)
            self.client.get(target_category, name="/en/category/[id]/")

    @task(3)
    def view_random_product(self) -> None:
        """Medium frequency: Clicking deeper into individual product details layers."""
        if self.product_urls:
            target_product: str = random.choice(self.product_urls)
            self.client.get(target_product, name="/en/product/[id]/")

    @task(2)
    def interact_with_cart(self) -> None:
        """Lower frequency: Appending items to the cart and loading the cart review layout."""
        if self.product_urls:
            target_product: str = random.choice(self.product_urls)
            match = re.search(r"\d+", target_product)
            if not match:
                return
            product_id: str = match.group()

            payload: dict[str, str | int] = {
                "quantity": 1,
                "csrfmiddlewaretoken": self.client.cookies.get("csrftoken", ""),
            }
            headers: dict[str, str] = {"Referer": f"{self.host}{target_product}"}

            self.client.post(
                f"/en/cart/{product_id}/add/",
                data=payload,
                headers=headers,
                name="/en/cart/[id]/add/",
            )
            self.client.get("/en/cart/", name="/en/cart/")

    @task(1)
    def interact_with_wishlist(self) -> None:
        """Lower frequency: Adding a product to the wishlist and viewing the account wishlist panel."""
        if self.product_urls:
            target_product: str = random.choice(self.product_urls)
            match = re.search(r"\d+", target_product)
            if not match:
                return
            product_id: str = match.group()

            payload: dict[str, str] = {
                "csrfmiddlewaretoken": self.client.cookies.get("csrftoken", ""),
            }
            headers: dict[str, str] = {"Referer": f"{self.host}{target_product}"}

            # Post to the wishlist addition route
            self.client.post(
                f"/en/account/wishlist/add/{product_id}/",
                data=payload,
                headers=headers,
                name="/en/account/wishlist/add/[id]/",
            )
            # Navigate to look at the aggregated wishlist page layout
            self.client.get("/en/account/wishlist/", name="/en/account/wishlist/")

    @task(1)
    def complete_checkout_flow(self) -> None:
        """Lower frequency: Simulates loading the checkout overview page and

        triggering the Stripe Checkout Session initialization endpoint.
        """
        # 1. Access the checkout overview layout page to capture dynamic session cookies
        checkout_form_resp = self.client.get(
            "/en/cart/checkout/", name="/en/cart/checkout/"
        )

        # Guard clause to ensure the session contains cart items before checking out
        if (
            "Your cart is empty" in checkout_form_resp.text
            or "Your Cart is Empty" in checkout_form_resp.text
        ):
            return

        # 2. Trigger the Stripe session generation endpoint via GET
        # Set allow_redirects=False to verify the redirection to checkout.stripe.com without sending load testing queries to Stripe itself.
        self.client.get(
            "/en/cart/checkout/create-checkout-session/",
            allow_redirects=False,
            name="/en/cart/checkout/create-checkout-session/",
        )
