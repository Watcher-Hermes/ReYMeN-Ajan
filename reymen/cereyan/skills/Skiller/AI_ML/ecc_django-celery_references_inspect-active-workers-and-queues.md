# Inspect active workers and queues
celery -A config inspect active
celery -A config inspect stats
celery -A config inspect reserved