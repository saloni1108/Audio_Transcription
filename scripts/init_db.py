import os

import django
from django.contrib.auth import get_user_model  # ✅ moved up

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "darwix_ai.settings")
django.setup()

User = get_user_model()

def init_db():
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin"
        )
        print(" Superuser 'admin' created with password 'admin'")
    else:
        print(" Superuser 'admin' already exists")

if __name__ == "__main__":
    from django.core.management import call_command
    call_command("migrate")
    init_db()
