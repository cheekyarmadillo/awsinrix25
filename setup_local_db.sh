#!/bin/sh
set -e

CONTAINER_NAME="maphole-test"
DB_NAME="maphole_db"
DB_USER="maphole_user"
DB_PASS="securepasskey123"
DB_PORT=5432
IMAGE="postgis/postgis:16-3.4"

echo "🚀 Spinning up local Postgres + PostGIS test DB..."

# --- Step 1: Ensure Docker is running ---
if ! docker info > /dev/null 2>&1; then
  echo "🐋 Docker is not running. Attempting to start it..."
  
  case "$(uname -s)" in
    Darwin)
      # macOS — open Docker Desktop
      open -a Docker
      echo "⏳ Waiting for Docker Desktop to start..."
      until docker info > /dev/null 2>&1; do
        sleep 2
      done
      ;;
    Linux)
      # Linux — try system service
      sudo systemctl start docker || true
      echo "⏳ Waiting for Docker daemon..."
      until docker info > /dev/null 2>&1; do
        sleep 2
      done
      ;;
    *)
      echo "❌ Unsupported OS: $(uname -s)"
      exit 1
      ;;
  esac
fi

# --- Step 2: Create or reuse container ---
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}\$"; then
  echo "⚙️  Container '${CONTAINER_NAME}' already exists. Starting it..."
  docker start "${CONTAINER_NAME}" > /dev/null
else
  echo "🧱 Creating new container '${CONTAINER_NAME}'..."
  docker run -d \
    --name "${CONTAINER_NAME}" \
    -e POSTGRES_USER="${DB_USER}" \
    -e POSTGRES_PASSWORD="${DB_PASS}" \
    -e POSTGRES_DB="${DB_NAME}" \
    -p "${DB_PORT}":5432 \
    "${IMAGE}"
fi

# --- Step 3: Wait for Postgres to accept connections ---
echo "⏳ Waiting for Postgres to be ready..."
until docker exec "${CONTAINER_NAME}" pg_isready -U "${DB_USER}" > /dev/null 2>&1; do
  sleep 1
done
echo "✅ Postgres is ready!"

# --- Step 4: Enable PostGIS extension ---
echo "🧩 Ensuring PostGIS extension exists..."
docker exec -i "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS postgis;" > /dev/null
echo "✅ PostGIS extension is active."

# --- Step 5: Summary ---
cat <<EOF

🎉 Local Postgres + PostGIS test DB is ready!

Connection info:
  📦 Database: ${DB_NAME}
  👤 User: ${DB_USER}
  🔑 Password: ${DB_PASS}
  🔌 Port: ${DB_PORT}

You can connect with:
  psql postgresql://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}

Flask connection string:
  postgresql://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}

To stop it:
  docker stop ${CONTAINER_NAME}

To remove it:
  docker rm -f ${CONTAINER_NAME}
EOF
