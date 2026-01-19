from django.urls import path
from . import views, webhooks

app_name = "cart"
urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("<int:product_id>/add/", views.add_to_cart, name="add_to_cart"),
    path("<int:product_id>/update/", views.update_cart, name="update_cart"),
    path("<int:product_id>/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "checkout/<int:product_id>/update/",
        views.update_cart_checkout,
        name="update_cart_checkout",
    ),
    path(
        "checkout/<int:product_id>/remove/",
        views.remove_from_cart_checkout,
        name="remove_from_cart_checkout",
    ),
    path(
        "checkout/create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("checkout/success/", views.success, name="success"),
    path("checkout/cancel/", views.cancel, name="cancel"),
    path(
        "webhook/",
        webhooks.stripe_webhook,
        name="fulfill_stripe_checkout_webhook",
    ),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
]
