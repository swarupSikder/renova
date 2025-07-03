# events/management/commands/generate_fake_data.py

from django.core.management.base import BaseCommand
from faker import Faker
from events.models import Event, Category, Participant
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate fake categories, events, and participants'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Optional: Clear previous data
        # Participant.objects.all().delete()
        # Event.objects.all().delete()
        # Category.objects.all().delete()

        # Create categories (if not already exist)
        categories = dict(Category.CATEGORY_CHOICES)
        for key, label in categories.items():
            Category.objects.get_or_create(name=key, defaults={'description': f"{label} Description"})

        category_objs = list(Category.objects.all())

        # Create events
        for _ in range(20):
            event = Event.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=100),
                date=fake.date_between(start_date='-30d', end_date='+60d'),
                time=fake.time(),
                location=fake.city(),
                category=random.choice(category_objs),
            )

            # Add participants
            for _ in range(random.randint(5, 15)):
                name = fake.name()
                email = fake.unique.email()

                participant, created = Participant.objects.get_or_create(
                    email=email,
                    defaults={"name": name}
                )
                participant.events.add(event)

        self.stdout.write(self.style.SUCCESS('✅ Fake data generated successfully!'))
