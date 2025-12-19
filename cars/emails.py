from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(email, username):
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
        fail_silently=False,
    )


def send_enquiry_email(dealer_email, message):
    send_mail(
        subject="New Enquiry 🚗",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[dealer_email],
        fail_silently=False,
    )
