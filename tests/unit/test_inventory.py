import pytest
from inventory.models import Product


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
def test_sort_by(product_setup):
    cat, prod1, prod2, prod3 = product_setup
    products = list(Product.sort_by("price-low-high"))
    assert products[0] == prod3
    assert products[-1] == prod1

    products = list(Product.sort_by("new-old"))
    assert products[0] == prod3


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
