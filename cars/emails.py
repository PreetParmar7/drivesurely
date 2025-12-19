from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_welcome_email(email, username):
    if not settings.SENDGRID_API_KEY:
        raise RuntimeError("SENDGRID_API_KEY missing")

    if not settings.DEFAULT_FROM_EMAIL:
        raise RuntimeError("DEFAULT_FROM_EMAIL missing")

    send_mail(
        subject="Welcome to DriveSurely 🚗",
        message=(
            f"Hi {username},\n\n"
            "Welcome to DriveSurely!\n\n"
            "Please complete your profile.\n\n"
            "— DriveSurely Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,  # IMPORTANT
    )
