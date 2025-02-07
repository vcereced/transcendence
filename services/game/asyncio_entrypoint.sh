echo "Starting game consumer..."

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is available."

exec python game_consumer.py