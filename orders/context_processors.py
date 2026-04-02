from .models import Order


def cart_count(request):
    """
    Returns the total number of items in the user's active cart.
    Returns 0 if the user is anonymous or has no active cart.
    """
    if request.user.is_authenticated:
        # Find the pending cart for this user
        cart = Order.objects.filter(user=request.user, is_checked_out=False).first()
        if cart:
            # Sum up the quantities of all items in that cart
            count = sum(item.quantity for item in cart.items.all())
            return {'cart_count': count}

    return {'cart_count': 0}