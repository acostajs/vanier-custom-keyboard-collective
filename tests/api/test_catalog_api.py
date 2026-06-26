import pytest
import requests
from django.urls import reverse


@pytest.mark.django_db
def test_catalog_index_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    url = f"{live_server.url}{reverse('inventory:index')}"
    response = requests.get(url, allow_redirects=True)
    assert response.status_code == 200
    assert p1.name in response.text
    assert p2.name in response.text


@pytest.mark.django_db
def test_category_detail_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    url = f"{live_server.url}{reverse('inventory:category', args=[category.id])}"
    response = requests.get(url, allow_redirects=True)
    assert response.status_code == 200
    assert category.name in response.text
    assert p1.name in response.text


@pytest.mark.django_db
def test_product_detail_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    url = f"{live_server.url}{reverse('inventory:product', args=[p1.id])}"
    response = requests.get(url, allow_redirects=True)
    assert response.status_code == 200
    assert p1.name in response.text
    assert p1.description in response.text


@pytest.mark.django_db
def test_catalog_search_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    url = f"{live_server.url}{reverse('inventory:results')}"
    response = requests.get(url, params={"search": "MX Master"}, allow_redirects=True)
    assert response.status_code == 200
    assert "MX Master 3S" in response.text
    assert "Keychron Q1" not in response.text


@pytest.mark.django_db
def test_catalog_filter_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    url = f"{live_server.url}{reverse('inventory:category', args=[category.id])}"
    response = requests.get(
        url, params={"filter_criteria": ["discount_percentage"]}, allow_redirects=True
    )
    assert response.status_code == 200
    assert "Keychron Q1" in response.text
    assert "MX Master 3S" not in response.text
