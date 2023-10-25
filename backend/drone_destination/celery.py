from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# setting the Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drone_destination.settings')
app = Celery('drone_destination')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Looks up for task modules in Django applications and loads them
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'timelog-violation-password-reset': {
        'task': 'users.tasks.watch_timelog_violations',
        'schedule': crontab(minute='45', hour='19'),
    },
}

app.conf.timezone = 'UTC'
