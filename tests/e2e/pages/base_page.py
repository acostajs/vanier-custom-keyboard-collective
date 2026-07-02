from playwright.sync_api import Page, Locator


class BasePage:
    """
    Base page object containing elements and actions shared across all pages,
    such as the header, search, navigation links, and language switcher.
    """

    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self.brand_link: Locator = page.locator("a.brand")
        self.search_input: Locator = page.locator('.search-form input[name="search"]')
        self.search_button: Locator = page.locator('.search-form button[type="submit"]')
        self.cart_link: Locator = page.locator('a[href*="/cart/"]')
        self.login_link: Locator = page.locator('a[href*="/account/login/"]')
        self.register_link: Locator = page.locator('a[href*="/account/registration/"]')
        self.wishlist_link: Locator = page.locator('a[href*="/account/wishlist/"]')
        self.account_link: Locator = page.locator(
            'a[href$="/account/"]'
        )  # matches ending with /account/ to avoid login/registration
        self.language_select: Locator = page.locator(
            '.lang-form select[name="language"]'
        )

    def navigate_to(self, url: str) -> None:
        """
        Navigate to the specified absolute or relative URL.
        """
        self.page.goto(url)

    def search_for(self, query: str) -> None:
        """
        Input a query into the search bar and submit.
        """
        self.search_input.fill(query)
        self.search_button.click()

    def switch_language(self, language_code: str) -> None:
        """
        Change the site language (e.g. 'en', 'fr') using the language dropdown.
        """
        self.language_select.select_option(value=language_code)
