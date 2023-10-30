from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UMAE_db.settings')

app = Celery('UMAE_db')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps:
app.autodiscover_tasks()