# Execute commands in running container
docker compose exec app sh           # Shell into app
docker compose exec db psql -U postgres  # Connect to postgres