docker stop postgres 2>/dev/null
docker rm postgres 2>/dev/null
docker run -d \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  --name postgres \
  postgres

echo "Waiting for PostgreSQL to be ready..."
until docker exec postgres pg_isready -U postgres >/dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is ready. Creating database..."
docker exec -it postgres psql -U postgres -c "CREATE DATABASE foodtracker;"

echo "Activating virtual environment"
. .venv/bin/activate

echo "Running alembic commands..."
alembic stamp head --purge
alembic revision --autogenerate
alembic upgrade head