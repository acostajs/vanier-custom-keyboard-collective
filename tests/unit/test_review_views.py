import pytest
from django.test.client import Client
from django.urls import reverse
from django.contrib.messages import get_messages

from account.models import Account
from inventory.models import Category, Product
from review.models import Review, Vote, Comment, Flag
from cart.models import Order, OrderItem


@pytest.mark.django_db
def test_review_not_purchased(
    order_user: Account, seed_data: tuple[Category, Product, Product, Product]
) -> None:
    """Review.create_review should fail if user has not purchased the product."""
    _, p1, _, _ = seed_data
    review, msg = Review.create_review(
        user=order_user,
        product=p1,
        rating=5,
        message="Great keyboard!",
    )
    assert review is None
    assert "must purchase" in msg


@pytest.mark.django_db
def test_review_already_reviewed(
    order_user: Account, seed_data: tuple[Category, Product, Product, Product]
) -> None:
    """Review.create_review should fail if user has already reviewed the product."""
    _, p1, _, _ = seed_data

    # Purchase record
    order = Order.objects.create(user=order_user, total_cents=1000)
    OrderItem.objects.create(order=order, product=p1, quantity=1, unit_price_cents=1000)

    # First review
    review, msg = Review.create_review(
        user=order_user,
        product=p1,
        rating=5,
        message="First!",
    )
    assert review is not None

    # Second review (should fail with IntegrityError internally and return None)
    review2, msg2 = Review.create_review(
        user=order_user,
        product=p1,
        rating=4,
        message="Second!",
    )
    assert review2 is None
    assert "already reviewed" in msg2


@pytest.mark.django_db
def test_unique_vote_already_voted(
    vote_setup: tuple[Account, Review, Review, Vote, Vote, Vote],
) -> None:
    """Vote.create_vote should return None and error message if user already voted."""
    user1, review, _, _, _, _ = vote_setup

    # Second vote by user1 on the same review
    vote, msg = Vote.create_vote(user1, review)
    assert vote is None
    assert "already voted" in msg


@pytest.mark.django_db
def test_unique_flag_already_flagged(
    flag_setup: tuple[Account, Review, Flag, Flag],
) -> None:
    """Flag.create_flag should return None and error message if user already flagged."""
    user1, review, _, _ = flag_setup

    # Second flag by user1 on the same review
    flag, msg = Flag.create_flag(user1, review, "fake")
    assert flag is None
    assert "already flagged" in msg


@pytest.mark.django_db
def test_flag_total_flags(flag_setup: tuple[Account, Review, Flag, Flag]) -> None:
    """Flag.total_flags calculates the number of flags on a review."""
    _, review, _, _ = flag_setup
    assert Flag.total_flags(review) == 2


@pytest.mark.django_db
def test_string_representations(
    comment_setup: tuple[Review, Comment, Comment],
    flag_setup: tuple[Account, Review, Flag, Flag],
    vote_setup: tuple[Account, Review, Review, Vote, Vote, Vote],
) -> None:
    """Test string representations for Review, Vote, Comment, and Flag models."""
    review, comment1, _ = comment_setup
    user1, _, _, vote1, _, _ = vote_setup
    _, _, flag1, _ = flag_setup

    assert str(review) == f"Review for {review.product.name} - {review.rating} stars"
    assert str(vote1) == f"{vote1.user.email} found the review '{vote1.review}' helpful"
    assert (
        str(comment1)
        == f"{comment1.user.email} wrote a comment on the review '{comment1.review}'"
    )
    assert str(flag1) == f"{flag1.user.email} tagged the review '{flag1.review}'"


@pytest.mark.django_db
def test_review_submit_invalid_form(
    test_client: Client,
    order_user: Account,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """POST to review_submit with invalid data re-renders the review form."""
    _, p1, _, _ = seed_data
    test_client.force_login(order_user)

    response = test_client.post(
        reverse("review:review_submit", kwargs={"product_id": p1.id}),
        data={"rating": "invalid", "message": ""},
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_review_submit_creation_failed(
    test_client: Client,
    order_user: Account,
    seed_data: tuple[Category, Product, Product, Product],
) -> None:
    """POST to review_submit when review creation fails (e.g. not purchased) redirects with error message."""
    _, p1, _, _ = seed_data
    test_client.force_login(order_user)

    response = test_client.post(
        reverse("review:review_submit", kwargs={"product_id": p1.id}),
        data={"rating": "5", "message": "Good keyboard!"},
    )
    assert response.status_code == 302
    assert response.url == reverse("inventory:product", kwargs={"product_id": p1.id})

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "must purchase" in str(messages[0])


@pytest.mark.django_db
def test_vote_get_view(
    test_client: Client,
    order_user: Account,
    vote_setup: tuple[Account, Review, Review, Vote, Vote, Vote],
) -> None:
    """GET to vote view renders the vote form."""
    _, review, _, _, _, _ = vote_setup
    test_client.force_login(order_user)

    response = test_client.get(reverse("review:vote", kwargs={"review_id": review.id}))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["review"] == review


@pytest.mark.django_db
def test_vote_submit_already_voted(
    test_client: Client,
    vote_setup: tuple[Account, Review, Review, Vote, Vote, Vote],
) -> None:
    """POST to vote_submit when user has already voted redirects with error message."""
    user1, review, _, _, _, _ = vote_setup
    test_client.force_login(user1)

    response = test_client.post(
        reverse("review:vote_submit", kwargs={"review_id": review.id})
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "inventory:product", kwargs={"product_id": review.product.id}
    )

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "already voted" in str(messages[0])


@pytest.mark.django_db
def test_comment_get_view(
    test_client: Client,
    order_user: Account,
    comment_setup: tuple[Review, Comment, Comment],
) -> None:
    """GET to comment view renders the comment form."""
    review, _, _ = comment_setup
    test_client.force_login(order_user)

    response = test_client.get(
        reverse("review:comment", kwargs={"review_id": review.id})
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["review"] == review


@pytest.mark.django_db
def test_comment_submit_invalid_form(
    test_client: Client,
    order_user: Account,
    comment_setup: tuple[Review, Comment, Comment],
) -> None:
    """POST to comment_submit with invalid data re-renders the comment form."""
    review, _, _ = comment_setup
    test_client.force_login(order_user)

    response = test_client.post(
        reverse("review:comment_submit", kwargs={"review_id": review.id}),
        data={"message": ""},
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_flag_get_view(
    test_client: Client,
    order_user: Account,
    flag_setup: tuple[Account, Review, Flag, Flag],
) -> None:
    """GET to flag view renders the flag form."""
    _, review, _, _ = flag_setup
    test_client.force_login(order_user)

    response = test_client.get(reverse("review:flag", kwargs={"review_id": review.id}))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["review"] == review


@pytest.mark.django_db
def test_flag_submit_invalid_form(
    test_client: Client,
    order_user: Account,
    flag_setup: tuple[Account, Review, Flag, Flag],
) -> None:
    """POST to flag_submit with invalid data re-renders the flag form."""
    _, review, _, _ = flag_setup
    test_client.force_login(order_user)

    response = test_client.post(
        reverse("review:flag_submit", kwargs={"review_id": review.id}),
        data={"flag_type": "invalid"},
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_flag_submit_already_flagged(
    test_client: Client,
    flag_setup: tuple[Account, Review, Flag, Flag],
) -> None:
    """POST to flag_submit when user has already flagged redirects with error message."""
    user1, review, _, _ = flag_setup
    test_client.force_login(user1)

    response = test_client.post(
        reverse("review:flag_submit", kwargs={"review_id": review.id}),
        data={"flag_type": "fake"},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "inventory:product", kwargs={"product_id": review.product.id}
    )

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "already flagged" in str(messages[0])
