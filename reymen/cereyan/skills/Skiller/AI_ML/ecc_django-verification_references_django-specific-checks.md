# Django-specific checks
python manage.py check --deploy
```

Common issues:
- Missing type hints on public functions
- PEP 8 formatting violations
- Unsorted imports
- Debug settings left in production configuration