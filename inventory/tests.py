from django.test import TestCase
from .models import Product, Category
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime


class CategoryModelTests(TestCase):
    def setUp(self):
        """To set up category examples to be able to test."""
        image = SimpleUploadedFile(
            name="test_image.jpg", content=b"", content_type="image/jpeg"
        )
        self.category = Category.objects.create(
            name="Test Category", description="A description for testing.", image=image
        )

    def test_category_fields(self):
        """Fields should store and retrieve values correctly"""
        category = self.category
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "A description for testing.")
        self.assertTrue(category.image)

    def test_category_str(self):
        """__str__ method should return the category name"""
        self.assertEqual(str(self.category), "Test Category")


class ProductModelTests(TestCase):
    def setUp(self):
        """To set up different products to be able to test."""
        self.cat = Category.objects.create(
            name="Accessories",
            description="Peripherals",
            image="categories/accessories.png",
        )
        now = timezone.now()
        self.prod1 = Product.objects.create(
            name="Keyboard X",
            description="Pro mechanical",
            quantity=10,
            image="prod1.png",
            price=12000,
            created_date=now - datetime.timedelta(days=5),
            category=self.cat,
            discount_percentage=10,
        )
        self.prod2 = Product.objects.create(
            name="Mouse Z",
            description="Wireless mouse",
            quantity=0,
            image="prod2.png",
            price=1999,
            created_date=now - datetime.timedelta(days=2),
            category=self.cat,
            discount_percentage=0,
        )
        self.prod3 = Product.objects.create(
            name="Cable Organizer",
            description="Tidy cables",
            quantity=5,
            image="prod3.png",
            price=500,
            created_date=now,
            category=self.cat,
            discount_percentage=20,
        )

    def test_is_available(self):
        """Should return True if the product is available, Should pass the test if the product is not available."""
        self.assertTrue(self.prod1.is_available)
        self.assertFalse(self.prod2.is_available)

    def test_price_in_dollars(self):
        """Should return True if the convertion of the price in cents to dollars is working correctly."""
        self.assertEqual(self.prod1.price_in_dollars, "$120.00")
        self.assertEqual(self.prod2.price_in_dollars, "$19.99")

    def test_discounted_price_in_dollars(self):
        """Should return True if the discount is applied to the price."""
        self.assertEqual(self.prod1.discounted_price_in_dollars, "$108.00")
        self.assertEqual(self.prod2.discounted_price_in_dollars, "$19.99")
        self.assertEqual(self.prod3.discounted_price_in_dollars, "$4.00")

    def test_get_discounted_price(self):
        """Should return True if it is properly getting the discount price in cents."""
        self.assertEqual(self.prod1.get_discounted_price(), 10800)
        self.assertEqual(self.prod2.get_discounted_price(), 1999)
        self.assertEqual(self.prod3.get_discounted_price(), 400)

    def test_created_recently(self):
        """Should return True if the product was created recently, should pass the test if is false that the product has not been created recently."""
        self.assertTrue(self.prod3.created_recently())
        self.assertFalse(self.prod1.created_recently())

    def test_new_arrival(self):
        """Should return True if the product is a new arrival."""
        self.assertTrue(self.prod1.new_arrival())
        self.assertTrue(self.prod2.new_arrival())
        self.assertTrue(self.prod3.new_arrival())

    def test_sort_by(self):
        """Should pass the tests if the sorting is working properly."""

        products = list(Product.sort_by("price-low-high"))
        self.assertEqual(products[0], self.prod3)
        self.assertEqual(products[-1], self.prod1)

        products = list(Product.sort_by("new-old"))
        self.assertEqual(products[0], self.prod3)

    def test_filter_by(self):
        """Should pass the tests if the products are being filtered correctly."""

        available = list(Product.filter_by(["quantity"]))
        self.assertIn(self.prod1, available)
        self.assertIn(self.prod3, available)
        self.assertNotIn(self.prod2, available)

        filtered = list(Product.filter_by(["created_recently", "discount_percentage"]))
        self.assertIn(self.prod1, filtered)
        self.assertIn(self.prod3, filtered)
        self.assertNotIn(self.prod2, filtered)

        all_products = list(Product.filter_by([]))
        self.assertCountEqual(all_products, [self.prod1, self.prod2, self.prod3])

    def test_search_by_name(self):
        """Should pass the test if the search finds the name inside the products."""
        results = list(Product.search_by_name("Cable"))
        self.assertIn(self.prod3, results)
        self.assertNotIn(self.prod1, results)
