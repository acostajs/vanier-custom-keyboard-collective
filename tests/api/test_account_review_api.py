import pytest
import requests
from django.urls import reverse
from account.models import Account
from review.models import Review, Vote, Comment, Flag
from cart.models import Order, OrderItem


@pytest.mark.django_db
def test_user_auth_flow_api(live_server, fake_user):
    session = requests.Session()

    # 1. Access registration page to populate cookies/CSRF
    reg_url = f"{live_server.url}{reverse('account:registration')}"
    response = session.get(reg_url)
    assert response.status_code == 200
    csrf_token = session.cookies.get("csrftoken")

    # 2. Register user
    reg_data = fake_user.copy()
    reg_data["csrfmiddlewaretoken"] = csrf_token
    response = session.post(reg_url, data=reg_data, allow_redirects=True)
    assert response.status_code == 200
    # Redirection back to login page
    assert "login" in response.url

    # 3. Log in with registered user
    login_url = f"{live_server.url}{reverse('account:login')}"
    csrf_token = session.cookies.get("csrftoken")
    response = session.post(
        login_url,
        data={
            "username": fake_user["username"],
            "password": fake_user["password1"],
            "csrfmiddlewaretoken": csrf_token,
        },
        allow_redirects=True,
    )
    assert response.status_code == 200
    # Redirection back to account dashboard page
    assert "account" in response.url
    assert fake_user["username"] in response.text

    # 4. Log out
    logout_url = f"{live_server.url}{reverse('account:logout')}"
    response = session.get(logout_url, allow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.url


@pytest.mark.django_db
def test_review_actions_api(live_server, seed_data):
    category, p1, p2, p3 = seed_data
    session = requests.Session()

    # 1. Create a user in the DB
    user = Account.objects.create_user(
        username="reviewer",
        email="rev@example.com",
        password="SecurePassword123!",
    )

    # 2. Add purchase record (OrderItem) in the DB so user is authorized to review
    order = Order.objects.create(user=user, payment_id="pi_rev", total_cents=15000)
    OrderItem.objects.create(
        order=order, product=p1, quantity=1, unit_price_cents=15000
    )

    # 3. Log in
    session.get(f"{live_server.url}{reverse('account:login')}")
    csrf_token = session.cookies.get("csrftoken")
    session.post(
        f"{live_server.url}{reverse('account:login')}",
        data={
            "username": "reviewer",
            "password": "SecurePassword123!",
            "csrfmiddlewaretoken": csrf_token,
        },
    )

    # 4. Access review page
    review_url = f"{live_server.url}{reverse('review:review', args=[p1.id])}"
    response = session.get(review_url)
    assert response.status_code == 200

    # 5. Submit review
    submit_url = f"{live_server.url}{reverse('review:review_submit', args=[p1.id])}"
    csrf_token = session.cookies.get("csrftoken")
    response = session.post(
        submit_url,
        data={
            "rating": "5",
            "message": "Outstanding mechanical keyboard!",
            "csrfmiddlewaretoken": csrf_token,
        },
        allow_redirects=True,
    )
    assert response.status_code == 200
    # Verifies review in the DB
    review = Review.objects.get(user=user, product=p1)
    assert review.rating == 5
    assert review.message == "Outstanding mechanical keyboard!"

    # 6. Vote on the review
    vote_submit_url = (
        f"{live_server.url}{reverse('review:vote_submit', args=[review.id])}"
    )
    csrf_token = session.cookies.get("csrftoken")
    response = session.post(
        vote_submit_url,
        data={"csrfmiddlewaretoken": csrf_token},
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert Vote.objects.filter(user=user, review=review).exists()

    # 7. Comment on the review
    comment_submit_url = (
        f"{live_server.url}{reverse('review:comment_submit', args=[review.id])}"
    )
    csrf_token = session.cookies.get("csrftoken")
    response = session.post(
        comment_submit_url,
        data={
            "message": "I second this review!",
            "csrfmiddlewaretoken": csrf_token,
        },
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert Comment.objects.filter(
        user=user, review=review, message="I second this review!"
    ).exists()

    # 8. Flag the review
    flag_submit_url = (
        f"{live_server.url}{reverse('review:flag_submit', args=[review.id])}"
    )
    csrf_token = session.cookies.get("csrftoken")
    response = session.post(
        flag_submit_url,
        data={
            "flag_type": "inappropriate",
            "csrfmiddlewaretoken": csrf_token,
        },
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert Flag.objects.filter(
        user=user, review=review, flag_type="inappropriate"
    ).exists()
