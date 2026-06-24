# Check connectivity
docker compose exec app wget -qO- http://api:3000/health