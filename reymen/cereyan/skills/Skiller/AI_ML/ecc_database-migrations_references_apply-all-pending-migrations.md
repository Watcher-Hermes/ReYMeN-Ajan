# Apply all pending migrations
migrate -path migrations -database "$DATABASE_URL" up