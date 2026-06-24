# Combined worker + beat (dev only, never production)
celery -A config worker --beat --loglevel=info