sudo docker stop postgres >/dev/null 2>&1 || true
sudo docker rm -f postgres >/dev/null 2>&1 || true
sudo docker run -d \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  --name postgres \
  postgres

echo "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
for i in $(seq 1 $MAX_RETRIES); do
  if sudo docker exec postgres pg_isready -U postgres >/dev/null 2>&1; then
    echo "PostgreSQL is up and running."
    if sudo docker exec postgres psql -U postgres -c "\q" >/dev/null 2>&1; then
      echo "PostgreSQL is ready to accept connections."
      break
    fi
  fi
  echo "Attempt $i/$MAX_RETRIES: PostgreSQL not yet ready. Waiting..."
  sleep 2 
  if [ $i -eq $MAX_RETRIES ]; then
    echo "Error: PostgreSQL did not become ready after $MAX_RETRIES attempts."
    sudo docker logs postgres
    exit 1
  fi
done

echo "PostgreSQL is ready. Creating database..."
sudo docker exec -it postgres psql -U postgres -c "CREATE DATABASE foodtracker;"

echo "Activating virtual environment"
. .venv/bin/activate

echo "Running alembic commands..."
alembic stamp head --purge
alembic revision --autogenerate
alembic upgrade head