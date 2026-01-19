from django.test import TestCase
from account.models import Account, Wishlist
from inventory.models import Product, Category


class AccountModelTests(TestCase):
    def test_create_account_and_str(self):
        user = Account.objects.create_user(
            username="juan",
            email="juan@example.com",
            password="pass1234",
            address_line1="123 Main St",
            city="Montreal",
            postal_code="H1H1H1",
            country="Canada",
        )

        self.assertEqual(user.username, "juan")
        self.assertEqual(user.email, "juan@example.com")
        self.assertEqual(user.address_line1, "123 Main St")
        self.assertEqual(user.city, "Montreal")
        self.assertEqual(user.postal_code, "H1H1H1")
        self.assertEqual(user.country, "Canada")
        self.assertEqual(str(user), "juan")


class WishlistModelTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="wishlistuser",
            email="wishlist@example.com",
            password="pass1234",
            address_line1="123 Main St",
            city="Montreal",
            postal_code="H1H1H1",
            country="Canada",
        )
        self.wishlist = Wishlist.objects.create(account=self.user)

        self.category = Category.objects.create(name="Keyboards")

        self.product1 = Product.objects.create(
            name="Prod 1",
            price=1000,
            quantity=10,
            category=self.category,
        )
        self.product2 = Product.objects.create(
            name="Prod 2",
            price=2000,
            quantity=5,
            category=self.category,
        )

    def test_add_and_count(self):
        self.wishlist.add(self.product1)
        self.wishlist.add(self.product2)
        self.assertEqual(self.wishlist.count(), 2)
        self.assertIn(self.product1, self.wishlist.product.all())
        self.assertIn(self.product2, self.wishlist.product.all())

    def test_remove(self):
        self.wishlist.add(self.product1)
        self.wishlist.add(self.product2)

        self.wishlist.remove(self.product1)
        self.assertEqual(self.wishlist.count(), 1)
        self.assertNotIn(self.product1, self.wishlist.product.all())
        self.assertIn(self.product2, self.wishlist.product.all())

    def test_clear(self):
        self.wishlist.add(self.product1)
        self.wishlist.add(self.product2)

        self.wishlist.clear()
        self.assertEqual(self.wishlist.count(), 0)
        self.assertEqual(self.wishlist.product.count(), 0)
