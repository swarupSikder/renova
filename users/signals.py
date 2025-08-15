from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{uid}/{token}/"
        send_mail(
            "Activate Your Account",
            f"Hi {instance.username},\n\nActivate your account:\n{activation_url}",
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=True,
        )
