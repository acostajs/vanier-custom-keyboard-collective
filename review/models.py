from django.db import models, IntegrityError
from inventory.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import Account
from cart.models import OrderItem
from django.utils.translation import gettext_lazy as _


class Review(models.Model):
    """Represents a product review submitted by the user."""

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(
        _("rating"), validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    message = models.TextField(_("message"))
    created_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_review(cls, user, product, rating, message):
        """Validates if the user has already purchased the product, and only one review per user per product."""
        has_purchased = OrderItem.objects.filter(
            order__user=user, product=product
        ).exists()
        if not has_purchased:
            return None, "You must purchase this product to leave a review."

        try:
            review = cls.objects.create(
                user=user, product=product, rating=rating, message=message
            )
            return review, "Thank you for your review."
        except IntegrityError:
            return None, "You have already reviewed this product."

    @classmethod
    def rating_average(cls, product):
        """Calculate the average rating for a given product, excluding reviews with >5 flags."""
        reviews = (
            cls.objects.filter(product=product)
            .annotate(flag_count=models.Count("flags"))
            .filter(flag_count__lte=5)
        )

        if not reviews.exists():
            return 0

        total_rating = sum(review.rating for review in reviews)
        return total_rating / reviews.count()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_review_per_user_per_product"
            )
        ]

    def __str__(self):
        return f"Review for {self.product.name} - {self.rating} stars"


class Vote(models.Model):
    """Represents a vote based on a review, submitted by the user."""

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="votes")

    @classmethod
    def create_vote(cls, user, review):
        """Validate that there is a unique vote per user per review and raise error message."""
        try:
            vote = cls.objects.create(user=user, review=review)
            return vote, "Thanks for your feedback."
        except IntegrityError:
            return None, "You have already voted on this review."

    @classmethod
    def total_votes(cls, review):
        """Calculate any type of the votes for a given review."""
        return cls.objects.filter(review=review).count()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "review"], name="unique_vote_per_user_per_review"
            )
        ]

    def __str__(self):
        return f"{self.user.email} found the review '{self.review}' helpful"


class Comment(models.Model):
    """Represents a comment based on a review, submitted by the user."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="comments")
    message = models.TextField(_("message"))
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.user.email} wrote a comment on the review '{self.review}'"


class Flag(models.Model):
    """Represents a flag based on a review, submitted by the user."""

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="flags")
    FLAG_CHOICES = [
        ("off-topic", "Off-topic"),
        ("inappropriate", "Inappropriate"),
        ("fake", "Fake"),
    ]
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="flags")
    flag_type = models.CharField(_("flag_type"), max_length=20, choices=FLAG_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_flag(cls, user, review, flag_type):
        """Validate if there is an unique flag per user and raise error message."""
        try:
            return cls.objects.create(
                user=user, review=review, flag_type=flag_type
            ), "Thank you for flagging this review."
        except IntegrityError:
            return None, "You have already flagged this review."

    @classmethod
    def total_flags(cls, review):
        """Calculate any type of the flags for a given review."""
        return cls.objects.filter(review=review).count()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "review"], name="unique_flag_per_user"
            )
        ]

    def __str__(self):
        return f"{self.user.email} tagged the review '{self.review}'"
