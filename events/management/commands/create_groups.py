from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from events.models import Event, Category

class Command(BaseCommand):
    help = "Create user roles (groups) with permissions"

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        organizer_group, created = Group.objects.get_or_create(name='Organizer')
        participant_group, created = Group.objects.get_or_create(name='Participant')

        # Admin: full permissions (you can assign all permissions)
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)

        # Organizer: can add/change/delete Event & Category
        event_ct = ContentType.objects.get_for_model(Event)
        category_ct = ContentType.objects.get_for_model(Category)

        organizer_permissions = Permission.objects.filter(
            content_type__in=[event_ct, category_ct],
            codename__in=[
                'add_event', 'change_event', 'delete_event',
                'add_category', 'change_category', 'delete_category',
            ]
        )
        organizer_group.permissions.set(organizer_permissions)

        # Participant: view only (default permissions or none)
        # Optionally add view permissions to events/categories

        self.stdout.write(self.style.SUCCESS("Groups created and permissions assigned"))