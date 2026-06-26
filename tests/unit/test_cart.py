import pytest
from cart.models import Order, OrderItem, CartItem


@pytest.mark.django_db
def test_create_order_defaults(order_user):
    order = Order.objects.create(
        user=order_user,
        payment_id="pi_123",
        total_cents=1000,
    )
    assert order.user == order_user
    assert order.payment_id == "pi_123"
    assert order.total_cents == 1000
    assert order.status == Order.STATUS_PENDING


@pytest.mark.django_db
def test_set_status_valid_and_invalid(order_user):
    order = Order.objects.create(
        user=order_user,
        payment_id="pi_456",
        total_cents=2000,
    )

    order.set_status("PAID")
    order.refresh_from_db()
    assert order.status == Order.STATUS_PAID

    with pytest.raises(ValueError):
        order.set_status("not-a-status")


@pytest.mark.django_db
def test_order_str_representation(order_user):
    order = Order.objects.create(
        user=order_user,
        payment_id="pi_789",
        total_cents=3000,
    )
    assert str(order) == "Order #pi_789 - test@example.com"


@pytest.mark.django_db
def test_order_item_str_representation(order_item_setup):
    order, product = order_item_setup
    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price_cents=1000,
    )
    assert str(item) == "2x Test Product"


@pytest.mark.django_db
def test_line_total_cents_property(order_item_setup):
    order, product = order_item_setup
    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=3,
        unit_price_cents=1500,
    )
    assert item.line_total_cents == 3 * 1500


@pytest.mark.django_db
def test_cart_str_representation(cart_setup):
    cart, product1, product2 = cart_setup
    assert str(cart) == f"This cart belongs to account {cart.account.email}"


@pytest.mark.django_db
def test_add_creates_and_updates_quantity(cart_setup):
    cart, product1, product2 = cart_setup
    cart.add(product1, quantity=2)
    item = CartItem.objects.get(cart=cart, product=product1)
    assert item.quantity == 2

    cart.add(product1, quantity=3)
    item.refresh_from_db()
    assert item.quantity == 5

    cart.add(product1, quantity=1, replace=True)
    item.refresh_from_db()
    assert item.quantity == 1


@pytest.mark.django_db
def test_items_remove_clear_count_and_subtotal(cart_setup):
    cart, product1, product2 = cart_setup
    cart.add(product1, quantity=2)
    cart.add(product2, quantity=1)
    assert cart.items().count() == 2
    assert cart.count() == 3
    assert cart.subtotal_cents() == 4000
    cart.remove(product2)
    assert not CartItem.objects.filter(cart=cart, product=product2).exists()
    cart.clear()
    assert CartItem.objects.filter(cart=cart).count() == 0


@pytest.mark.django_db
def test_cart_item_str_and_price_properties(cart_item_setup):
    cart, product = cart_item_setup
    item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=3,
    )
    assert str(item) == "Prod x 3 cart item"
    assert item.unit_cents == 1500
    assert item.line_cents == 1500 * 3
    assert item.total_cents == 1500 * 3
