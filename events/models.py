from django.db import models
from django.conf import settings

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
        return self.get_name_display()

    




# - - - - - - - - #
#   Event Model   #
# - - - - - - - - #
class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, related_name='events')

    # Use settings.AUTH_USER_MODEL for relations to the user model
    rsvps = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rsvp_events', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')

    image = models.ImageField(upload_to='event_images/', default='event_images/default.jpg')

    def __str__(self):
        return self.name




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