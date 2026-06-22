# Cache verification (if using Redis)
python -c "from django.core.cache import cache; cache.set('test', 'value', 10); print(cache.get('test'))"
```