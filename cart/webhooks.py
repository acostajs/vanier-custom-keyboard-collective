import os
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Order


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe events."""
    print("webhook is running")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        print("Handling checkout.session.completed")
        stripe_session = event["data"]["object"]
        print("session:", stripe_session)
        order_id = stripe_session["client_reference_id"]
        print("order_id:", order_id)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse(status=404)

        if order.user:
            account = order.user
            order.fulfill(
                name=f"{account.first_name} {account.last_name}".strip(),
                email=account.email,
                payment_id=stripe_session["payment_intent"],
                total_cents=order.total_cents,
                billing_address_line1=account.address_line1,
                billing_address_line2=account.address_line2,
                billing_city=account.city,
                billing_postal_code=account.postal_code,
                billing_country=account.country,
                shipping_address_line1=account.address_line1,
                shipping_address_line2=account.address_line2,
                shipping_city=account.city,
                shipping_postal_code=account.postal_code,
                shipping_country=account.country,
            )
        else:
            customer_details = stripe_session["customer_details"]
            billing = customer_details["address"]

            collected_info = stripe_session.get("collected_information", {})
            shipping_details = collected_info.get("shipping_details", {})
            shipping = shipping_details.get("address", {})

            order.fulfill(
                name=customer_details["name"],
                email=customer_details["email"],
                payment_id=stripe_session["payment_intent"],
                total_cents=order.total_cents,
                billing_address_line1=billing["line1"],
                billing_address_line2=billing["line2"],
                billing_city=billing["city"],
                billing_postal_code=billing["postal_code"],
                billing_country=billing["country"],
                shipping_address_line1=shipping.get("line1"),
                shipping_address_line2=shipping.get("line2"),
                shipping_city=shipping.get("city"),
                shipping_postal_code=shipping.get("postal_code"),
                shipping_country=shipping.get("country"),
            )

        order.set_status("paid")

    elif event["type"] in ("payment_intent.payment_failed", "payment_intent.canceled"):
        payment_intent = event["data"]["object"]
        pi_id = payment_intent["id"]

        try:
            order = Order.objects.get(payment_id=pi_id)
        except Order.DoesNotExist:
            return HttpResponse(status=200)

        order.set_status("cancelled")

    return HttpResponse(status=200)
