import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instaapp.settings')

# Initialize Celery application with the project name
app = Celery('instaapp')

# Load Celery configuration from Django settings, using the 'CELERY_' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover Celery tasks from all registered Django apps
app.autodiscover_tasks()