# Check for migration conflicts
python manage.py makemigrations --merge  # Only if conflicts exist
```

Report:
- Number of pending migrations
- Any migration conflicts
- Model changes without migrations