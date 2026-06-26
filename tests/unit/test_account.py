import pytest
from account.models import Account


@pytest.mark.django_db
def test_create_account_and_str():
    user = Account.objects.create_user(
        username="juan",
        email="juan@example.com",
        password="pass1234",
        address_line1="123 Main St",
        city="Montreal",
        postal_code="H1H1H1",
        country="Canada",
    )

    assert user.username == "juan"
    assert user.email == "juan@example.com"
    assert user.address_line1 == "123 Main St"
    assert user.city == "Montreal"
    assert user.postal_code == "H1H1H1"
    assert user.country == "Canada"
    assert str(user) == "juan"


@pytest.mark.django_db
def test_add_and_count(wishlist_setup):
    wishlist, product1, product2 = wishlist_setup
    wishlist.add(product1)
    wishlist.add(product2)
    assert wishlist.count() == 2
    assert product1 in wishlist.product.all()
    assert product2 in wishlist.product.all()


@pytest.mark.django_db
def test_remove(wishlist_setup):
    wishlist, product1, product2 = wishlist_setup
    wishlist.add(product1)
    wishlist.add(product2)

    wishlist.remove(product1)
    assert wishlist.count() == 1
    assert product1 not in wishlist.product.all()
    assert product2 in wishlist.product.all()


@pytest.mark.django_db
def test_clear(wishlist_setup):
    wishlist, product1, product2 = wishlist_setup
    wishlist.add(product1)
    wishlist.add(product2)

    wishlist.clear()
    assert wishlist.count() == 0
    assert wishlist.product.count() == 0
