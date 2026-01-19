from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
    path("", views.account, name="account"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("login_submit/", views.login_submit, name="login_submit"),
    path("registration/", views.registration, name="registration"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path(
        "reset-password/<uidb64>/<token>/",
        views.reset_password_submit,
        name="reset_password_submit",
    ),
    path("wishlist/", views.wishlist_detail, name="wishlist_detail"),
    path(
        "wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"
    ),
    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path(
        "wishlist/transfer/<int:product_id>/",
        views.transfer_to_cart,
        name="transfer_to_cart",
    ),
    path("wishlist/clear/", views.clear_wishlist, name="clear_wishlist"),
]
