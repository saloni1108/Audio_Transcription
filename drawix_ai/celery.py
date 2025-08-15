import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "darwix_ai.settings")

app = Celery("darwix_ai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
