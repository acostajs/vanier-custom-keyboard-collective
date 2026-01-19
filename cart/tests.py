from django.test import TestCase
from account.models import Account
from inventory.models import Product, Category
from cart.models import Order, OrderItem, Cart, CartItem


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass1234",
            address_line1="123 Main St",
            city="Montreal",
            postal_code="H1H1H1",
            country="Canada",
        )

    def test_create_order_defaults(self):
        order = Order.objects.create(
            user=self.user,
            payment_id="pi_123",
            total_cents=1000,
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.payment_id, "pi_123")
        self.assertEqual(order.total_cents, 1000)
        self.assertEqual(order.status, Order.STATUS_PENDING)

    def test_set_status_valid_and_invalid(self):
        order = Order.objects.create(
            user=self.user,
            payment_id="pi_456",
            total_cents=2000,
        )

        order.set_status("PAID")
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)

        with self.assertRaises(ValueError):
            order.set_status("not-a-status")

    def test_str_representation(self):
        order = Order.objects.create(
            user=self.user,
            payment_id="pi_789",
            total_cents=3000,
        )
        self.assertEqual(str(order), "Order #pi_789 - test@example.com")


class OrderItemModelTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="orderitemuser",
            email="orderitem@example.com",
            password="pass1234",
            address_line1="1 Order St",
            city="Montreal",
            postal_code="H2H2H2",
            country="Canada",
        )

        self.category = Category.objects.create(name="Keyboards")

        self.product = Product.objects.create(
            name="Test Product",
            price=1000,
            quantity=10,
            category=self.category,
        )

        self.order = Order.objects.create(
            user=self.user,
            payment_id="pi_123",
            total_cents=1000,
        )

    def test_str_representation(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price_cents=1000,
        )
        self.assertEqual(str(item), "2x Test Product")

    def test_line_total_cents_property(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            unit_price_cents=1500,
        )
        self.assertEqual(item.line_total_cents, 3 * 1500)


class CartModelTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="cartuser",
            email="cart@example.com",
            password="pass1234",
            address_line1="10 Cart Rd",
            city="Montreal",
            postal_code="H3H3H3",
            country="Canada",
        )
        self.cart = Cart.objects.create(account=self.user)

        self.category = Category.objects.create(name="Keyboards")

        self.product1 = Product.objects.create(
            name="Prod 1",
            price=1000,
            quantity=100,
            category=self.category,
        )
        self.product2 = Product.objects.create(
            name="Prod 2",
            price=2000,
            quantity=100,
            category=self.category,
        )

    def test_str_representation(self):
        self.assertEqual(
            str(self.cart),
            f"This cart belongs to account {self.user.email}",
        )

    def test_add_creates_and_updates_quantity(self):
        self.cart.add(self.product1, quantity=2)
        item = CartItem.objects.get(cart=self.cart, product=self.product1)
        self.assertEqual(item.quantity, 2)

        self.cart.add(self.product1, quantity=3)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

        self.cart.add(self.product1, quantity=1, replace=True)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_items_remove_clear_count_and_subtotal(self):
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)
        self.assertEqual(self.cart.items().count(), 2)
        self.assertEqual(self.cart.count(), 3)
        self.assertEqual(self.cart.subtotal_cents(), 4000)
        self.cart.remove(self.product2)
        self.assertFalse(
            CartItem.objects.filter(cart=self.cart, product=self.product2).exists()
        )
        self.cart.clear()
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 0)


class CartItemModelTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="cartitemuser",
            email="cartitem@example.com",
            password="pass1234",
            address_line1="20 Item Blvd",
            city="Montreal",
            postal_code="H4H4H4",
            country="Canada",
        )
        self.cart = Cart.objects.create(account=self.user)

        self.category = Category.objects.create(name="Keyboards")

        self.product = Product.objects.create(
            name="Prod",
            price=1500,
            quantity=50,
            category=self.category,
        )

    def test_str_and_price_properties(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3,
        )
        self.assertEqual(str(item), "Prod x 3 cart item")
        self.assertEqual(item.unit_cents, 1500)
        self.assertEqual(item.line_cents, 1500 * 3)
        self.assertEqual(item.total_cents, 1500 * 3)
