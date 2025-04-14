echo "Starting game consumer..."

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is available."

echo "Waiting for PostgreSQL..."
while ! nc -z game_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."

exec python game_consumer.py