import pytest
from inventory.models import Product, Category
from review.models import Review
from account.models import Account


@pytest.mark.django_db
def test_category_fields(category_setup):
    category = category_setup
    assert category.name == "Test Category"
    assert category.description == "A description for testing."
    assert category.image


@pytest.mark.django_db
def test_category_str(category_setup):
    category = category_setup
    assert str(category) == "Test Category"


@pytest.mark.django_db
def test_is_available(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    assert prod1.is_available
    assert not prod2.is_available


@pytest.mark.django_db
def test_price_in_dollars(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    assert prod1.price_in_dollars == "$120.00"
    assert prod2.price_in_dollars == "$19.99"


@pytest.mark.django_db
def test_discounted_price_in_dollars(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    assert prod1.discounted_price_in_dollars == "$108.00"
    assert prod2.discounted_price_in_dollars == "$19.99"
    assert prod3.discounted_price_in_dollars == "$4.00"


@pytest.mark.django_db
def test_get_discounted_price(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    assert prod1.get_discounted_price() == 10800
    assert prod2.get_discounted_price() == 1999
    assert prod3.get_discounted_price() == 400


@pytest.mark.django_db
def test_created_recently(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    assert prod3.created_recently()
    assert not prod1.created_recently()


@pytest.mark.django_db
def test_new_arrival(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    assert prod1.new_arrival()
    assert prod2.new_arrival()
    assert prod3.new_arrival()


@pytest.mark.django_db
def test_sort_by(product_setup: tuple[Category, Product, Product, Product]) -> None:
    cat, prod1, prod2, prod3 = product_setup

    # price-low-high
    products = list(Product.sort_by("price-low-high"))
    assert products[0] == prod3
    assert products[-1] == prod1

    # new-old
    products = list(Product.sort_by("new-old"))
    assert products[0] == prod3

    # old-new
    products = list(Product.sort_by("old-new"))
    assert products[-1] == prod3

    # price-high-low
    products = list(Product.sort_by("price-high-low"))
    assert products[0] == prod1
    assert products[-1] == prod3

    # discount-high-low
    products = list(Product.sort_by("discount-high-low"))
    assert products[0] == prod3  # 20%
    assert products[1] == prod1  # 10%
    assert products[2] == prod2  # 0%

    # discount-low-high
    products = list(Product.sort_by("discount-low-high"))
    assert products[0] == prod2  # 0%
    assert products[-1] == prod3  # 20%

    # a-z
    products = list(Product.sort_by("a-z"))
    assert products[0] == prod3  # Cable Organizer
    assert products[1] == prod1  # Keyboard X
    assert products[2] == prod2  # Mouse Z

    # z-a
    products = list(Product.sort_by("z-a"))
    assert products[0] == prod2  # Mouse Z
    assert products[-1] == prod3  # Cable Organizer

    # rating-high-low
    # Let's create dummy user and reviews
    user = Account.objects.create_user(
        username="ratinguser", email="rating@example.com", password="pw"
    )
    # prod1 gets 5 stars, prod3 gets 3 stars
    Review.objects.create(user=user, product=prod1, rating=5)
    Review.objects.create(user=user, product=prod3, rating=3)

    products = list(Product.sort_by("rating-high-low"))
    assert products[0] == prod1
    assert products[1] == prod3

    # default/fallback case
    products = list(Product.sort_by("invalid-criteria"))
    assert products[0] == prod3  # defaults to new-old


@pytest.mark.django_db
def test_filter_by(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    available = list(Product.filter_by(["quantity"]))
    assert prod1 in available
    assert prod3 in available
    assert prod2 not in available

    filtered = list(Product.filter_by(["created_recently", "discount_percentage"]))
    assert prod1 in filtered
    assert prod3 in filtered
    assert prod2 not in filtered

    all_products = list(Product.filter_by([]))
    assert set(all_products) == {prod1, prod2, prod3}


@pytest.mark.django_db
def test_search_by_name(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    results = list(Product.search_by_name("Cable"))
    assert prod3 in results
    assert prod1 not in results


@pytest.mark.django_db
def test_product_str(product_setup: tuple[Category, Product, Product, Product]) -> None:
    cat, prod1, prod2, prod3 = product_setup
    assert str(prod1) == "Keyboard X"
