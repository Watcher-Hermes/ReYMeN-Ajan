# GOOD — use [profile] for user-invokable functions
[profile]
common = """
  deploy() { kubectl apply -f k8s/; }
"""
```