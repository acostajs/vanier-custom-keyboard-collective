import os
import pytest
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from faker import Faker
from account.models import Account, Wishlist
from inventory.models import Category, Product
from cart.models import Order, Cart
from review.models import Review, Vote, Comment, Flag

User = get_user_model()

# Set dummy environment variables for tests
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_mock")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_mock")
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def fake_user() -> dict[str, str]:
    """
    Generate fake user registration data.
    """
    fake = Faker()
    return {
        "username": fake.user_name()[:30],
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "password1": "SecurePassword123!",
        "password2": "SecurePassword123!",
        "address_line1": fake.street_address(),
        "address_line2": fake.secondary_address(),
        "city": fake.city(),
        "postal_code": "K1A 0B1",
        "country": "Canada",
    }


@pytest.fixture
def seed_data(db) -> tuple[Category, Product, Product, Product]:
    """
    Seed categories and products for testing catalog searching, sorting, filtering,
    and shopping cart operations.
    """
    cat = Category.objects.create(
        name="Keyboards",
        description="Premium Mechanical Keyboards",
        image="categories/keyboard.png",
    )

    p1 = Product.objects.create(
        name="Keychron Q1",
        description="Aluminum custom mechanical keyboard",
        quantity=5,
        price=15000,
        category=cat,
        discount_percentage=10,
        image="products/q1.png",
    )

    p2 = Product.objects.create(
        name="MX Master 3S",
        description="Wireless ergonomic office mouse",
        quantity=10,
        price=9900,
        category=cat,
        discount_percentage=0,
        image="products/mx.png",
    )

    p3 = Product.objects.create(
        name="Cable Organizer",
        description="Desk cable organizer",
        quantity=0,
        price=1500,
        category=cat,
        discount_percentage=0,
        image="products/cable.png",
    )

    return cat, p1, p2, p3


@pytest.fixture
def test_client():
    """Fixture providing a Django test client, referred to as TestClient."""
    from django.test import Client as TestClient

    return TestClient()


@pytest.fixture
def wishlist_setup(db):
    user = Account.objects.create_user(
        username="wishlistuser",
        email="wishlist@example.com",
        password="pass1234",
        address_line1="123 Main St",
        city="Montreal",
        postal_code="H1H1H1",
        country="Canada",
    )
    wishlist = Wishlist.objects.create(account=user)
    category = Category.objects.create(name="Keyboards")
    product1 = Product.objects.create(
        name="Prod 1",
        price=1000,
        quantity=10,
        category=category,
    )
    product2 = Product.objects.create(
        name="Prod 2",
        price=2000,
        quantity=5,
        category=category,
    )
    return wishlist, product1, product2


@pytest.fixture
def order_user(db):
    return Account.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="pass1234",
        address_line1="123 Main St",
        city="Montreal",
        postal_code="H1H1H1",
        country="Canada",
    )


@pytest.fixture
def order_item_setup(db):
    user = Account.objects.create_user(
        username="orderitemuser",
        email="orderitem@example.com",
        password="pass1234",
        address_line1="1 Order St",
        city="Montreal",
        postal_code="H2H2H2",
        country="Canada",
    )
    category = Category.objects.create(name="Keyboards")
    product = Product.objects.create(
        name="Test Product",
        price=1000,
        quantity=10,
        category=category,
    )
    order = Order.objects.create(
        user=user,
        payment_id="pi_123",
        total_cents=1000,
    )
    return order, product


@pytest.fixture
def cart_setup(db):
    user = Account.objects.create_user(
        username="cartuser",
        email="cart@example.com",
        password="pass1234",
        address_line1="10 Cart Rd",
        city="Montreal",
        postal_code="H3H3H3",
        country="Canada",
    )
    cart = Cart.objects.create(account=user)
    category = Category.objects.create(name="Keyboards")
    product1 = Product.objects.create(
        name="Prod 1",
        price=1000,
        quantity=100,
        category=category,
    )
    product2 = Product.objects.create(
        name="Prod 2",
        price=2000,
        quantity=100,
        category=category,
    )
    return cart, product1, product2


@pytest.fixture
def cart_item_setup(db):
    user = Account.objects.create_user(
        username="cartitemuser",
        email="cartitem@example.com",
        password="pass1234",
        address_line1="20 Item Blvd",
        city="Montreal",
        postal_code="H4H4H4",
        country="Canada",
    )
    cart = Cart.objects.create(account=user)
    category = Category.objects.create(name="Keyboards")
    product = Product.objects.create(
        name="Prod",
        price=1500,
        quantity=50,
        category=category,
    )
    return cart, product


@pytest.fixture
def category_setup(db):
    from django.core.files.uploadedfile import SimpleUploadedFile

    image = SimpleUploadedFile(
        name="test_image.jpg", content=b"", content_type="image/jpeg"
    )
    return Category.objects.create(
        name="Test Category", description="A description for testing.", image=image
    )


@pytest.fixture
def product_setup(db):
    cat = Category.objects.create(
        name="Accessories",
        description="Peripherals",
        image="categories/accessories.png",
    )
    now = timezone.now()
    prod1 = Product.objects.create(
        name="Keyboard X",
        description="Pro mechanical",
        quantity=10,
        image="prod1.png",
        price=12000,
        created_date=now - datetime.timedelta(days=5),
        category=cat,
        discount_percentage=10,
    )
    prod2 = Product.objects.create(
        name="Mouse Z",
        description="Wireless mouse",
        quantity=0,
        image="prod2.png",
        price=1999,
        created_date=now - datetime.timedelta(days=2),
        category=cat,
        discount_percentage=0,
    )
    prod3 = Product.objects.create(
        name="Cable Organizer",
        description="Tidy cables",
        quantity=5,
        image="prod3.png",
        price=500,
        created_date=now,
        category=cat,
        discount_percentage=20,
    )
    return cat, prod1, prod2, prod3


@pytest.fixture
def review_setup(db):
    user1 = User.objects.create_user(
        username="tester1", email="tester1@email.com", password="pw1"
    )
    user2 = User.objects.create_user(
        username="tester2", email="tester2@email.com", password="pw2"
    )
    user3 = User.objects.create_user(
        username="tester3", email="tester3@email.com", password="pw3"
    )
    category = Category.objects.create(
        name="Accessories",
        description="Peripherals",
        image="categories/accessories.png",
    )
    product1 = Product.objects.create(
        name="Keyboard X",
        description="Pro mechanical",
        quantity=10,
        image="prod1.png",
        price=12000,
        category=category,
        discount_percentage=10,
    )
    product2 = Product.objects.create(
        name="Mouse Z",
        description="Wireless mouse",
        quantity=5,
        image="prod2.png",
        price=3500,
        category=category,
        discount_percentage=0,
    )
    review1 = Review.objects.create(
        user=user1,
        product=product1,
        rating=5,
        created_date=timezone.now(),
    )
    review2 = Review.objects.create(
        user=user2,
        product=product2,
        rating=3,
        created_date=timezone.now(),
    )
    review3 = Review.objects.create(
        user=user3,
        product=product1,
        rating=4,
        created_date=timezone.now(),
    )
    return product1, product2, review1, review2, review3


@pytest.fixture
def vote_setup(db):
    user1 = User.objects.create_user(
        username="vote1", email="vote1@email.com", password="pw1"
    )
    user2 = User.objects.create_user(
        username="vote2", email="vote2@email.com", password="pw2"
    )
    user3 = User.objects.create_user(
        username="vote3", email="vote3@email.com", password="pw3"
    )
    category = Category.objects.create(
        name="Accessories",
        description="Peripherals",
        image="categories/accessories.png",
    )
    product = Product.objects.create(
        name="Keyboard X",
        description="Pro mechanical",
        quantity=10,
        image="prod1.png",
        price=12000,
        category=category,
        discount_percentage=10,
    )
    review = Review.objects.create(
        user=user1,
        product=product,
        rating=5,
        message="Great product!",
    )
    review2 = Review.objects.create(
        user=user2,
        product=product,
        rating=4,
        message="Good product!",
    )
    vote1 = Vote.objects.create(
        review=review,
        user=user1,
    )
    vote2 = Vote.objects.create(
        review=review,
        user=user2,
    )
    vote3 = Vote.objects.create(
        review=review,
        user=user3,
    )
    return user1, review, review2, vote1, vote2, vote3


@pytest.fixture
def comment_setup(db):
    user1 = User.objects.create_user(
        username="comment1", email="user1@example.com", password="pw1"
    )
    user2 = User.objects.create_user(
        username="comment2", email="user2@example.com", password="pw2"
    )
    category = Category.objects.create(
        name="Test Category", description="For testing", image="test.png"
    )
    product = Product.objects.create(
        name="Comment Test Product",
        description="For testing comments",
        quantity=10,
        image="test.png",
        price=2999,
        category=category,
    )
    review = Review.objects.create(
        user=user1,
        product=product,
        message="Solid product overall.",
        rating=4,
    )
    comment1 = Comment.objects.create(
        review=review,
        user=user1,
        message="I agree with your review!",
    )
    comment2 = Comment.objects.create(
        review=review,
        user=user2,
        message="Helpful review, thanks!",
    )
    return review, comment1, comment2


@pytest.fixture
def flag_setup(db):
    user1 = User.objects.create_user(
        username="flag1", email="flagger1@example.com", password="pw1"
    )
    user2 = User.objects.create_user(
        username="flag2", email="flagger2@example.com", password="pw2"
    )
    category = Category.objects.create(
        name="Test Category", description="For testing", image="test.png"
    )
    product = Product.objects.create(
        name="Flag Test Product",
        description="For testing flags",
        quantity=5,
        image="test.png",
        price=1999,
        category=category,
    )
    review = Review.objects.create(
        user=user1,
        product=product,
        message="Not so great experience.",
        rating=2,
    )
    flag1 = Flag.objects.create(review=review, user=user1, flag_type="inappropriate")
    flag2 = Flag.objects.create(review=review, user=user2, flag_type="fake")
    return user1, review, flag1, flag2


@pytest.fixture
def models_logic_category(db):
    return Category.objects.create(
        name="Testing",
        description="Test Category",
    )
