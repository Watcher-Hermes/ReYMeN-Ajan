# View logs
docker compose logs -f app           # Follow app logs
docker compose logs --tail=50 db     # Last 50 lines from db