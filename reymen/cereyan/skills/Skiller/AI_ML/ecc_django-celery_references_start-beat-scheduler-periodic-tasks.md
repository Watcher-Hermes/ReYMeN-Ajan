# Start beat scheduler (periodic tasks)
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler