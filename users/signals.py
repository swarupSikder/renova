# users/signals.py
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        # Create UID and token
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)

        # Full activation URL
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{uid}/{token}/"

        subject = "Activate Your Account"
        message = (
            f"Hi {instance.username},\n\n"
            f"Please activate your account by clicking on the link below:\n"
            f"{activation_url}\n\n"
            "Thank you."
        )
        recipient_list = [instance.email]

        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            print(f"Failed to send email to {instance.email}: {str(e)}")