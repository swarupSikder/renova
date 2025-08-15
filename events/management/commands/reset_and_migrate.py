from django.core.management.base import BaseCommand
from django.db import connection
import os

class Command(BaseCommand):
    help = "Reset DB and run migrations"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
        self.stdout.write(self.style.SUCCESS("✅ Database reset."))

        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        self.stdout.write(self.style.SUCCESS("✅ Migrations complete."))
