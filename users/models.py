from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """
    Extends Django's AbstractUser with a phone number and profile picture.
    Keeps username/login behavior while adding the requested fields.
    """

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Optional. Format: +999999999"
    )

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.png',
        blank=True,
        null=True,
        help_text="Profile image (optional)."
    )

    def __str__(self):
        return self.get_username()