from django.db import models
from django.contrib.auth.models import User

# - - - - - - - - - - #
#    Category Model   #
# - - - - - - - - - - #
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('CASUAL', 'Casual Party'),
        ('BIRTHDAY', 'Birthday Party'),
        ('WEDDING', 'Wedding Party'),
        ('FORMAL', 'Formal Party'),
    ]
    name = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default="CASUAL")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    




# - - - - - - - - #
#   Event Model   #
# - - - - - - - - #
class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=150)
    # category (ForeignKey)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        default=1,
        related_name='events',
    )
    rsvps = models.ManyToManyField(User, related_name='rsvp_events', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')

    def __str__(self):
        return f"Event Name: {self.name}"




# - - - - - - - - - - - #
#   Participant Model   #
# - - - - - - - - - - - #
class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # ManyToMany relationship with Event
    events = models.ManyToManyField(Event)

    def __str__(self):
        return f"Participant: {self.name}, Email: {self.email}"