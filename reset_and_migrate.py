# reset_and_migrate.py
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "renova.settings")
django.setup()

def reset_database():
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
    print("✅ Database schema reset.")

def run_migrations():
    os.system("python manage.py makemigrations")
    os.system("python manage.py migrate")
    print("✅ Migrations complete.")

if __name__ == "__main__":
    reset_database()
    run_migrations()
