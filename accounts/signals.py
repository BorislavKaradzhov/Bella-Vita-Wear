from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail


# Listen for the exact moment a CustomUser is saved
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Background Task: Automatically sends a welcome email
    whenever a new user registers for the site.
    """
    if created:
        subject = 'Welcome to Bella Vita Wear!'
        message = f'Hi {instance.username},\n\nThank you for registering at Bella Vita Wear. We are thrilled to have you shopping with us!\n\nBest,\nThe Bella Vita Team'

        # We use fail_silently=True so if the email system ever goes down,
        # it doesn't crash the user's registration process!
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True
        )