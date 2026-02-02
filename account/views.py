from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    get_user_model,
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.template.loader import render_to_string
from .models import Wishlist
from cart.helpers import get_cart
from inventory.models import Product
from cart.models import Cart, Order
from cart.session_cart import SessionCart
from django.utils.translation import gettext_lazy as _
from django.utils import translation


@login_required(login_url="account:login")
def account(request):
    """Display the current user's account page with their order history if the user is logged in."""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "orders": orders,
    }
    return render(request, "account/account.html", context)


def login(request):
    """Handles user login, if the user is logged it, is redirected to their account."""
    if request.user.is_authenticated:
        return redirect("account:account")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("account:account")
    else:
        form = AuthenticationForm(request)

    return render(request, "account/login.html", {"form": form})


def logout(request):
    """Logs out the current user and redirects to login page."""
    auth_logout(request)
    return redirect("account:login")


@require_POST
def login_submit(request):
    """Process the login form submission with authentication."""
    form = LoginForm(request.POST)

    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user:
            auth_login(request, user)
            cart = get_cart(request)
            session_cart = SessionCart(request)
            for item in session_cart.items():
                product = item["product"]
                quantity = item["quantity"]
                cart.add(product, quantity=int(quantity))
            session_cart.clear()
            return redirect("account:account")
        else:
            form.add_error(None, _("Invalid username or password"))

    return render(request, "account/login.html", {"form": form})


def registration(request):
    """Handle new user registration with cart/wishlist setup."""

    form = RegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        Wishlist.objects.create(account=user)
        cart = Cart.objects.create(account=user)

        session_cart = SessionCart(request)
        for item in session_cart.items():
            product = item["product"]
            quantity = item["quantity"]
            cart.add(product, quantity=int(quantity))
        session_cart.clear()

        return redirect("account:login")

    return render(request, "account/registration.html", {"form": form})


def reset_password(request):
    """Handles initiation of password reset via email."""
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            associated_users = get_user_model().objects.filter(email=user_email)

            for user in associated_users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse("account:reset_password_submit", args=[uid, token])
                )

                lang = translation.get_language()
                if lang.startswith("fr"):
                    template_name = "account/reset_password_email_fr.txt"
                else:
                    template_name = "account/reset_password_email.txt"

                subject = _("Password reset")
                message = render_to_string(
                    template_name,
                    {
                        "user": user,
                        "reset_link": reset_link,
                    },
                )

                user.email_user(subject, message)

            messages.success(
                request,
                _(
                    "If an account with that email exists, a password reset link has been sent."
                ),
            )
            return redirect("account:login")
    else:
        form = PasswordResetForm()

    return render(request, "account/reset_password.html", {"form": form})


def reset_password_submit(request, uidb64, token):
    """Completes and confirm the password reset process."""
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, _("Your password has been reset. You can now log in.")
                )
                return redirect("account:login")
        else:
            form = SetPasswordForm(user)

        return render(request, "account/reset_password_submit.html", {"form": form})
    else:
        messages.error(request, _("The reset link is invalid or has expired."))
        return redirect("account:reset_password")


@login_required(login_url="account:login")
@require_GET
def wishlist_detail(request):
    """Display the wishlist if the user is logged in."""
    wishlist = get_object_or_404(Wishlist, account=request.user)
    wishlist_products = wishlist.product.all()

    context = {
        "wishlist": wishlist,
        "wishlist_products": wishlist_products,
    }
    return render(request, "account/wishlist.html", context)


@login_required(login_url="account:login")
@require_POST
def add_to_wishlist(request, product_id):
    """Adds a product to the wishlist if the user is logged in."""
    product = get_object_or_404(Product, pk=product_id)
    wishlist = get_object_or_404(Wishlist, account=request.user)
    wishlist.add(product)
    messages.success(request, f"Added {product.name} to wishlist.")
    return redirect("inventory:product", product_id)


@login_required(login_url="account:login")
@require_POST
def remove_from_wishlist(request, product_id):
    """Removes a product from the wishlist if the user is logged in."""
    product = get_object_or_404(Product, pk=product_id)
    user = request.user
    wishlist = get_object_or_404(Wishlist, account=user)
    wishlist.remove(product)
    messages.info(request, f"Removed {product.name} from wishlist.")
    return redirect("account:wishlist_detail")


@login_required(login_url="account:login")
@require_POST
def clear_wishlist(request):
    """Clear the wishlist from all products if the user is logged in."""
    wishlist = get_object_or_404(Wishlist, account=request.user)
    wishlist.clear()
    messages.info(request, _("Wishlist cleared."))
    return redirect("account:wishlist_detail")


@login_required(login_url="account:login")
@require_POST
def transfer_to_cart(request, product_id):
    """Transfer all the products in the wishlist to the user account related cart."""
    wishlist = Wishlist.objects.get(account=request.user)
    cart = get_cart(request)
    for product in wishlist.product.all():
        cart.add(product, quantity=1)
    wishlist.clear()

    return redirect("cart:cart_detail")
