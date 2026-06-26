import pytest
from django.utils import timezone
import datetime
from inventory.models import Product, Category
from review.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_get_discounted_price(models_logic_category):
    """
    Verify product get_discounted_price calculation.
    """
    # Product with 10% discount
    prod_discount = Product.objects.create(
        name="Discounted Keyboard",
        price=10000,  # $100.00
        quantity=5,
        category=models_logic_category,
        discount_percentage=10,
    )
    assert prod_discount.get_discounted_price() == 9000  # $90.00

    # Product with 0% discount
    prod_regular = Product.objects.create(
        name="Regular Keyboard",
        price=15000,  # $150.00
        quantity=5,
        category=models_logic_category,
        discount_percentage=0,
    )
    assert prod_regular.get_discounted_price() == 15000


@pytest.mark.django_db
def test_price_in_dollars_properties(models_logic_category):
    """
    Verify price_in_dollars and discounted_price_in_dollars formatting.
    """
    product = Product.objects.create(
        name="Format Keyboard",
        price=12345,  # $123.45
        quantity=5,
        category=models_logic_category,
        discount_percentage=20,  # 20% discount on 12345 is 9876 cents -> $98.76
    )
    assert product.price_in_dollars == "$123.45"
    assert product.discounted_price_in_dollars == "$98.76"


@pytest.mark.django_db
def test_creation_windows(models_logic_category):
    """
    Verify created_recently and new_arrival date range logic.
    """
    now = timezone.now()

    # Created recently (now) -> both true
    prod_now = Product.objects.create(
        name="Now Keyboard",
        price=1000,
        quantity=5,
        category=models_logic_category,
        created_date=now,
    )
    assert prod_now.created_recently()
    assert prod_now.new_arrival()

    # Created 2 days ago -> created_recently is False (window is 1 day), new_arrival is True (window is 30 days)
    prod_past = Product.objects.create(
        name="Old Keyboard",
        price=1000,
        quantity=5,
        category=models_logic_category,
        created_date=now - datetime.timedelta(days=2),
    )
    assert not prod_past.created_recently()
    assert prod_past.new_arrival()

    # Created 45 days ago -> both False
    prod_ancient = Product.objects.create(
        name="Ancient Keyboard",
        price=1000,
        quantity=5,
        category=models_logic_category,
        created_date=now - datetime.timedelta(days=45),
    )
    assert not prod_ancient.created_recently()
    assert not prod_ancient.new_arrival()


@pytest.mark.django_db
def test_rating_average():
    """
    Verify rating_average calculation across reviews.
    """
    category = Category.objects.create(name="Review Test Category")
    product = Product.objects.create(
        name="Review Keyboard",
        price=5000,
        quantity=10,
        category=category,
    )
    user = User.objects.create_user(
        username="reviewer",
        email="rev@example.com",
        password="pass",
    )

    # No reviews -> average should be 0
    assert Review.rating_average(product) == 0

    # One review -> average is that review rating
    Review.objects.create(user=user, product=product, rating=4)
    assert Review.rating_average(product) == 4

    # Second review -> average is average of both
    user2 = User.objects.create_user(
        username="reviewer2",
        email="rev2@example.com",
        password="pass",
    )
    Review.objects.create(user=user2, product=product, rating=5)
    assert Review.rating_average(product) == 4.5
