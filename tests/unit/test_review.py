import pytest
from review.models import Review, Vote, Comment, Flag


@pytest.mark.django_db
def test_review_creation(review_setup):
    product1, product2, review1, review2, review3 = review_setup
    assert Review.objects.count() == 3
    assert review1.product == product1
    assert review1.user.email == "tester1@email.com"
    assert review3.rating == 4


@pytest.mark.django_db
def test_rating_average(review_setup):
    product1, product2, review1, review2, review3 = review_setup
    assert Review.rating_average(product1) == 4.5
    assert Review.rating_average(product2) == 3


@pytest.mark.django_db
def test_vote_creation(vote_setup):
    user1, review, review2, vote1, vote2, vote3 = vote_setup
    assert Vote.objects.count() == 3
    assert vote1.review == review
    assert vote1.user.email == "vote1@email.com"


@pytest.mark.django_db
def test_total_votes(vote_setup):
    user1, review, review2, vote1, vote2, vote3 = vote_setup
    assert Vote.total_votes(review) == 3
    assert Vote.total_votes(review2) == 0


@pytest.mark.django_db
def test_unique_vote_constraint(vote_setup):
    user1, review, review2, vote1, vote2, vote3 = vote_setup
    with pytest.raises(Exception):
        Vote.objects.create(review=review, user=user1)


@pytest.mark.django_db
def test_comment_creation(comment_setup):
    review, comment1, comment2 = comment_setup
    assert Comment.objects.count() == 2
    assert comment1.review == review
    assert comment2.user.email == "user2@example.com"


@pytest.mark.django_db
def test_comment_ordering(comment_setup):
    review, comment1, comment2 = comment_setup
    comments = Comment.objects.all()
    assert comments[0].created_date >= comments[1].created_date


@pytest.mark.django_db
def test_flag_creation(flag_setup):
    user1, review, flag1, flag2 = flag_setup
    assert Flag.objects.count() == 2
    assert flag1.flag_type == "inappropriate"
    assert flag1.review == review
    assert flag2.user.email == "flagger2@example.com"


@pytest.mark.django_db
def test_unique_flag_constraint(flag_setup):
    user1, review, flag1, flag2 = flag_setup
    with pytest.raises(Exception):
        Flag.objects.create(review=review, user=user1, flag_type="off-topic")
