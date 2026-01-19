from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Review, Vote, Comment, Flag
from inventory.models import Product, Category

User = get_user_model()


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="tester1", email="tester1@email.com", password="pw1"
        )
        self.user2 = User.objects.create_user(
            username="tester2", email="tester2@email.com", password="pw2"
        )
        self.user3 = User.objects.create_user(
            username="tester3", email="tester3@email.com", password="pw3"
        )
        self.category = Category.objects.create(
            name="Accessories",
            description="Peripherals",
            image="categories/accessories.png",
        )
        self.product1 = Product.objects.create(
            name="Keyboard X",
            description="Pro mechanical",
            quantity=10,
            image="prod1.png",
            price=12000,
            category=self.category,
            discount_percentage=10,
        )
        self.product2 = Product.objects.create(
            name="Mouse Z",
            description="Wireless mouse",
            quantity=5,
            image="prod2.png",
            price=3500,
            category=self.category,
            discount_percentage=0,
        )
        self.review1 = Review.objects.create(
            user=self.user1,
            product=self.product1,
            rating=5,
            created_date=timezone.now(),
        )
        self.review2 = Review.objects.create(
            user=self.user2,
            product=self.product2,
            rating=3,
            created_date=timezone.now(),
        )
        self.review3 = Review.objects.create(
            user=self.user3,
            product=self.product1,
            rating=4,
            created_date=timezone.now(),
        )

    def test_review_creation(self):
        self.assertEqual(Review.objects.count(), 3)
        self.assertEqual(self.review1.product, self.product1)
        self.assertEqual(self.review1.user.email, "tester1@email.com")
        self.assertEqual(self.review3.rating, 4)

    def test_rating_average(self):
        self.assertEqual(Review.rating_average(self.product1), 4.5)
        self.assertEqual(Review.rating_average(self.product2), 3)


class VoteModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="vote1", email="vote1@email.com", password="pw1"
        )
        self.user2 = User.objects.create_user(
            username="vote2", email="vote2@email.com", password="pw2"
        )
        self.user3 = User.objects.create_user(
            username="vote3", email="vote3@email.com", password="pw3"
        )
        self.category = Category.objects.create(
            name="Accessories",
            description="Peripherals",
            image="categories/accessories.png",
        )
        self.product = Product.objects.create(
            name="Keyboard X",
            description="Pro mechanical",
            quantity=10,
            image="prod1.png",
            price=12000,
            category=self.category,
            discount_percentage=10,
        )
        self.review = Review.objects.create(
            user=self.user1,
            product=self.product,
            rating=5,
            message="Great product!",
        )
        self.review2 = Review.objects.create(
            user=self.user2,
            product=self.product,
            rating=4,
            message="Good product!",
        )
        self.vote1 = Vote.objects.create(
            review=self.review,
            user=self.user1,
        )
        self.vote2 = Vote.objects.create(
            review=self.review,
            user=self.user2,
        )
        self.vote3 = Vote.objects.create(
            review=self.review,
            user=self.user3,
        )

    def test_vote_creation(self):
        self.assertEqual(Vote.objects.count(), 3)
        self.assertEqual(self.vote1.review, self.review)
        self.assertEqual(self.vote1.user.email, "vote1@email.com")

    def test_total_votes(self):
        self.assertEqual(Vote.total_votes(self.review), 3)
        self.assertEqual(Vote.total_votes(self.review2), 0)

    def test_unique_vote_constraint(self):
        with self.assertRaises(Exception):
            Vote.objects.create(review=self.review, user=self.user1)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="comment1", email="user1@example.com", password="pw1"
        )
        self.user2 = User.objects.create_user(
            username="comment2", email="user2@example.com", password="pw2"
        )
        self.category = Category.objects.create(
            name="Test Category", description="For testing", image="test.png"
        )
        self.product = Product.objects.create(
            name="Comment Test Product",
            description="For testing comments",
            quantity=10,
            image="test.png",
            price=2999,
            category=self.category,
        )
        self.review = Review.objects.create(
            user=self.user1,
            product=self.product,
            message="Solid product overall.",
            rating=4,
        )
        self.comment1 = Comment.objects.create(
            review=self.review,
            user=self.user1,
            message="I agree with your review!",
        )
        self.comment2 = Comment.objects.create(
            review=self.review,
            user=self.user2,
            message="Helpful review, thanks!",
        )

    def test_comment_creation(self):
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.comment1.review, self.review)
        self.assertEqual(self.comment2.user.email, "user2@example.com")

    def test_comment_ordering(self):
        comments = Comment.objects.all()
        self.assertGreaterEqual(comments[0].created_date, comments[1].created_date)


class FlagModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="flag1", email="flagger1@example.com", password="pw1"
        )
        self.user2 = User.objects.create_user(
            username="flag2", email="flagger2@example.com", password="pw2"
        )
        self.category = Category.objects.create(
            name="Test Category", description="For testing", image="test.png"
        )
        self.product = Product.objects.create(
            name="Flag Test Product",
            description="For testing flags",
            quantity=5,
            image="test.png",
            price=1999,
            category=self.category,
        )
        self.review = Review.objects.create(
            user=self.user1,
            product=self.product,
            message="Not so great experience.",
            rating=2,
        )
        self.flag1 = Flag.objects.create(
            review=self.review, user=self.user1, flag_type="inappropriate"
        )
        self.flag2 = Flag.objects.create(
            review=self.review, user=self.user2, flag_type="fake"
        )

    def test_flag_creation(self):
        self.assertEqual(Flag.objects.count(), 2)
        self.assertEqual(self.flag1.flag_type, "inappropriate")
        self.assertEqual(self.flag1.review, self.review)
        self.assertEqual(self.flag2.user.email, "flagger2@example.com")

    def test_unique_flag_constraint(self):
        with self.assertRaises(Exception):
            Flag.objects.create(
                review=self.review, user=self.user1, flag_type="off-topic"
            )
