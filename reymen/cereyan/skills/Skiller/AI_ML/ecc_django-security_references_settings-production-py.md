# settings/production.py
import os

DEBUG = False  # CRITICAL: Never use True in production

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')