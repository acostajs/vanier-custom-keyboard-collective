# review/urls.py
from django.urls import path
from . import views

app_name = "review"
urlpatterns = [
    path("product/<int:product_id>/", views.review, name="review"),
    path("product/<int:product_id>/submit/", views.review_submit, name="review_submit"),
    path("<int:review_id>/vote/", views.vote, name="vote"),
    path("<int:review_id>/vote/submit/", views.vote_submit, name="vote_submit"),
    path("<int:review_id>/comment/", views.comment, name="comment"),
    path(
        "<int:review_id>/comment/submit/", views.comment_submit, name="comment_submit"
    ),
    path("<int:review_id>/flag/", views.flag, name="flag"),
    path("<int:review_id>/flag/submit/", views.flag_submit, name="flag_submit"),
]
