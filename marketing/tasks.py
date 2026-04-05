from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order
from .models import DiscountCode

User = get_user_model()


@shared_task
def check_and_issue_loyalty_discount(user_id):
    """
    Checks if the user has a multiple of 3 fulfilled orders.
    If so, generates a 50% discount code and sends a notification email.
    """
    try:
        user = User.objects.get(id=user_id)

        # Count only fulfilled and non-cancelled orders
        fulfilled_orders_count = Order.objects.filter(
            user=user,
            status='Fulfilled'
        ).count()

        # Check if the count is a multiple of 3
        if fulfilled_orders_count > 0 and fulfilled_orders_count % 3 == 0:
            # Generate the unique code
            code_string = f"LOYAL50-{user.username.upper()}-{fulfilled_orders_count}"

            # Create the discount code in the database
            DiscountCode.objects.create(
                code=code_string,
                discount_percentage=50,
                user=user,
                is_active=True
            )

            # Send the Loyalty Discount Email (Prints to console)
            subject = "Your 50% Loyalty Discount is Here!"
            message = f"Hi {user.username},\n\nThank you for placing {fulfilled_orders_count} orders! We've automatically applied a 50% discount code ({code_string}) to your next cart.\n\nEnjoy,\nBella Vita Wear"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True
            )

            return f"Discount code {code_string} generated and emailed for user {user.username}"

        return f"User {user.username} not eligible yet. Total fulfilled: {fulfilled_orders_count}"

    except User.DoesNotExist:
        return "User not found."