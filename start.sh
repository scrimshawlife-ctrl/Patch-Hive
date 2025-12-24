#!/bin/bash
# PatchHive Replit Startup Script
# This script initializes and starts both backend and frontend services

set -e

echo "🐝 Starting PatchHive on Replit..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if PostgreSQL is running
check_postgres() {
    pg_isready -h localhost -p 5432 > /dev/null 2>&1
    return $?
}

# Initialize PostgreSQL if not already initialized
if [ ! -d "$PGDATA" ]; then
    echo -e "${BLUE}📦 Initializing PostgreSQL database...${NC}"
    mkdir -p $PGDATA
    initdb -D $PGDATA

    # Configure PostgreSQL
    echo "unix_socket_directories = '/tmp'" >> $PGDATA/postgresql.conf
    echo "listen_addresses = 'localhost'" >> $PGDATA/postgresql.conf
    echo "port = 5432" >> $PGDATA/postgresql.conf
fi

# Start PostgreSQL if not running
if ! check_postgres; then
    echo -e "${BLUE}🚀 Starting PostgreSQL...${NC}"
    pg_ctl -D $PGDATA -l $PGDATA/logfile start

    # Wait for PostgreSQL to be ready
    for i in {1..30}; do
        if check_postgres; then
            echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
            break
        fi
        echo "Waiting for PostgreSQL to start... ($i/30)"
        sleep 1
    done
fi

# Create database if it doesn't exist
echo -e "${BLUE}📊 Setting up database...${NC}"
psql -h localhost -U $USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'patchhive'" | grep -q 1 || \
    psql -h localhost -U $USER -d postgres -c "CREATE DATABASE patchhive"

# Set environment variables for backend
export DATABASE_URL="postgresql://$USER@localhost:5432/patchhive"
export SECRET_KEY="${SECRET_KEY:-development-secret-key-change-in-production}"
export CORS_ORIGINS='["http://localhost:5173", "https://*.repl.co", "https://*.replit.dev"]'

# Install/update backend dependencies
echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
cd backend
pip install -q -r requirements.txt
pip install -q alembic

# Run database migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
alembic upgrade head

# Seed data (optional - comment out if not needed)
if [ ! -f "$PGDATA/.seeded" ]; then
    echo -e "${YELLOW}🌱 Seeding initial data...${NC}"
    python seed_data.py || echo "Warning: Seed data failed or not needed"
    touch $PGDATA/.seeded
fi

cd ..

# Install frontend dependencies
echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Start backend in background
echo -e "${GREEN}🚀 Starting backend API on port 8000...${NC}"
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    sleep 1
done

# Start frontend
echo -e "${GREEN}🚀 Starting frontend on port 5173...${NC}"
cd frontend
export VITE_API_BASE_URL="http://localhost:8000"
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd ..

# Display status
echo ""
echo -e "${GREEN}✨ PatchHive is now running! ✨${NC}"
echo ""
echo -e "${BLUE}📍 Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}📍 Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}📍 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}💡 Tip: The Replit webview will show the frontend automatically${NC}"
echo ""

# Tail logs from both services
tail -f /tmp/backend.log &

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
