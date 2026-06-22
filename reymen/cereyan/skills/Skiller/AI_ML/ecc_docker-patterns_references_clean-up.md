# Clean up
docker compose down                   # Stop and remove containers
docker compose down -v                # Also remove volumes (DESTRUCTIVE)
docker system prune                   # Remove unused images/containers
```

### Debugging Network Issues

```bash