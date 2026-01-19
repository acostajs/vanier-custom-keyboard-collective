from account.models import Wishlist, Account


def wishlist_info(request):
    """Get the total count of products inside Wishlist."""
    try:
        user = Account.objects.get(username=request.user.username)
        wishlist = Wishlist.objects.get(account=user)
        count = wishlist.count()
    except (Account.DoesNotExist, Wishlist.DoesNotExist):
        count = 0
    return {"wishlist_count": count}
