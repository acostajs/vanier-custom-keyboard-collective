from playwright.sync_api import Page, Locator
from base_page import BasePage


class WishlistPage(BasePage):
    """
    Page object representing the User Wishlist page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.wishlist_table: Locator = page.locator(".cart-table")
        self.clear_wishlist_button: Locator = page.locator(
            "button:has-text('Clear Wishlist')"
        )
        self.empty_wishlist_message: Locator = page.locator(
            "p:has-text('Your wishlist is empty.')"
        )

    def get_wishlist_item_rows(self) -> Locator:
        """
        Return the Locator for the rows of items in the wishlist table.
        """
        return self.wishlist_table.locator("tbody tr")

    def get_wishlist_item_count(self) -> int:
        """
        Return the number of unique items currently in the wishlist.
        """
        if not self.wishlist_table.is_visible():
            return 0
        return self.get_wishlist_item_rows().count()

    def get_wishlist_item_by_name(self, product_name: str) -> Locator:
        """
        Find and return the table row locator for a product name.
        """
        return self.get_wishlist_item_rows().filter(has_text=product_name).first

    def remove_item(self, product_name: str) -> None:
        """
        Remove a product from the wishlist.
        """
        row = self.get_wishlist_item_by_name(product_name)
        row.locator("button:has-text('Remove')").click()

    def transfer_to_cart(self, product_name: str) -> None:
        """
        Transfer a product from the wishlist to the cart.
        """
        row = self.get_wishlist_item_by_name(product_name)
        row.locator("button:has-text('Transfer to Cart')").click()

    def clear_wishlist(self) -> None:
        """
        Clear all items from the wishlist.
        """
        self.clear_wishlist_button.click()
