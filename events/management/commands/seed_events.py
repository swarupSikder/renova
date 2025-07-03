from django.core.management.base import BaseCommand
from events.models import Category, Event, Participant
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seed the database with fake Event and Participant data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Optional: clear existing data
        Event.objects.all().delete()
        Participant.objects.all().delete()

        # Ensure some categories exist
        categories = Category.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.WARNING("No categories found. Seeding default categories..."))
            predefined = Category.CATEGORY_CHOICES
            for key, label in predefined:
                Category.objects.create(name=key, description=f"{label} description")
            categories = Category.objects.all()

        # Create 20 fake Events
        for _ in range(20):
            event = Event.objects.create(
                name=fake.sentence(nb_words=3),
                description=fake.text(),
                date=fake.date_this_year(),
                time=fake.time(),
                location=fake.address(),
                category=random.choice(categories),
            )

            # Add participants to the event
            for _ in range(random.randint(1, 5)):
                name = fake.name()
                email = fake.unique.email()
                participant, created = Participant.objects.get_or_create(
                    email=email,
                    defaults={'name': name}
                )
                participant.events.add(event)

        self.stdout.write(self.style.SUCCESS("Successfully seeded fake Event and Participant data."))
