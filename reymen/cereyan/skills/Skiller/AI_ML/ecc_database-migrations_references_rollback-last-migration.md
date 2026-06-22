# Rollback last migration
migrate -path migrations -database "$DATABASE_URL" down 1