from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_editor.settings')

app = Celery('video_editor')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()