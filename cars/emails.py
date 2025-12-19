from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(email, username):
    if not settings.EMAIL_ENABLED:
        return

    try:
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
    except Exception as e:
        print("Email error:", e)
