#!/bin/bash

# ============================================
# Uganda Electronics Platform - Deployment Script
# ============================================
# This script deploys the platform to DigitalOcean
# Run this on your DigitalOcean Droplet

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================
# Deployment Lock & Error Handling
# ============================================

# Prevent concurrent deployments
LOCKFILE="/tmp/uganda_electronics_deploy.lock"
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    print_error "Another deployment is already running."
    print_error "If this is incorrect, remove: $LOCKFILE"
    exit 1
fi

# Show which line failed when an error occurs
trap 'print_error "Deployment failed at line $LINENO. Check logs above for details."; exit 1' ERR

# Release lock on exit
trap 'flock -u 200' EXIT

echo "🚀 Starting deployment of Uganda Electronics Platform..."
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is okay for initial setup."
fi

# ============================================
# 1. System Requirements Check
# ============================================
print_status "Checking system requirements..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Install Docker with:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo "Install Docker Compose plugin"
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Check available disk space (need at least 10GB)
AVAILABLE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    print_warning "Available disk space is less than 10GB. Consider upgrading your Droplet."
fi

# Check available memory (need at least 2GB)
AVAILABLE_MEMORY=$(free -g | awk 'NR==2 {print $2}')
if [ "$AVAILABLE_MEMORY" -lt 2 ]; then
    print_warning "Available memory is less than 2GB. Consider upgrading your Droplet."
fi

# ============================================
# 2. Environment Configuration
# ============================================
print_status "Checking environment configuration..."

if [ ! -f .env.production ]; then
    print_error ".env.production file not found!"
    echo ""
    echo "Please create .env.production from .env.production.example:"
    echo "  cp .env.production.example .env.production"
    echo "  nano .env.production  # Edit with your values"
    echo ""
    exit 1
fi

print_success "Environment configuration found"

# Load environment variables
set -a
source .env.production
set +a

# Check critical environment variables
REQUIRED_VARS=(
    "DB_PASSWORD"
    "SECRET_KEY"
    "SERVER_IP"
    "NEXT_PUBLIC_SALEOR_API_URL"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

print_success "All required environment variables are set"

# ============================================
# 3. Create Required Directories
# ============================================
print_status "Creating required directories..."

# Note: nginx/logs should be managed via Docker volumes (see docker-compose.yml)
# Only create SSL directory for certificate storage
mkdir -p nginx/ssl
mkdir -p backups

print_success "Directories created"

# ============================================
# 4. Pull & Deploy Services (Zero-Downtime)
# ============================================
print_status "Pulling latest images..."

docker compose -f docker-compose.production.yml pull

print_success "Images pulled"

print_status "Starting/updating services..."

# Deploy without stopping (rolling restart of changed services only)
# --remove-orphans: cleanup containers for removed services
# --build: rebuild services that need it (like storefront)
# This recreates only containers that have changed, minimizing downtime
docker compose -f docker-compose.production.yml up -d --remove-orphans --build

print_success "Services started/updated"
print_status "Note: Use '--force-recreate' flag to rebuild all containers, or run 'down' manually for major changes"

# ============================================
# 5. Wait for Services to be Ready
# ============================================
print_status "Waiting for services to be ready..."

# Wait for database
echo -n "Waiting for database..."
until docker compose -f docker-compose.production.yml exec -T db pg_isready -U saleor > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " Ready!"

# Wait for API to be serving requests
echo -n "Waiting for API to be ready..."
MAX_RETRIES=60
RETRY_COUNT=0
until [ $RETRY_COUNT -ge $MAX_RETRIES ]; do
    # Check if API health endpoint responds (or GraphQL endpoint for Saleor)
    if curl -f -s http://localhost:8000/graphql/ > /dev/null 2>&1; then
        echo " Ready!"
        break
    fi
    echo -n "."
    RETRY_COUNT=$((RETRY_COUNT+1))
    sleep 2
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    print_error "API failed to start - check logs with: docker compose -f docker-compose.production.yml logs api"
    exit 1
fi

print_success "All services are ready"

# ============================================
# 6. Run Database Migrations
# ============================================
print_status "Running database migrations..."

docker compose -f docker-compose.production.yml exec -T api python manage.py migrate

print_success "Database migrations completed"

# ============================================
# 7. Create Superuser (if first deployment)
# ============================================
if [ "$1" == "--first-time" ]; then
    print_status "Creating superuser account..."
    echo ""
    echo "Please enter details for the admin account:"
    docker compose -f docker-compose.production.yml exec api python manage.py createsuperuser
fi

# ============================================
# 8. Collect Static Files
# ============================================
print_status "Collecting static files..."

docker compose -f docker-compose.production.yml exec -T api python manage.py collectstatic --noinput

print_success "Static files collected"

# ============================================
# 9. Run Uganda Platform Migrations (if exist)
# ============================================
if [ -d "saleor-platform-uganda/migrations/uganda-platform" ]; then
    print_status "Running Uganda platform migrations..."

    # Copy migrations directory to db container
    docker compose -f docker-compose.production.yml cp saleor-platform-uganda/migrations/uganda-platform db:/tmp/

    # Run migrations inside the db container
    for migration in saleor-platform-uganda/migrations/uganda-platform/*.sql; do
        if [ -f "$migration" ]; then
            MIGRATION_NAME=$(basename "$migration")
            print_status "Running: $MIGRATION_NAME"
            docker compose -f docker-compose.production.yml exec -T db psql -U saleor -d saleor -f "/tmp/uganda-platform/$MIGRATION_NAME"
        fi
    done

    # Cleanup
    docker compose -f docker-compose.production.yml exec -T db rm -rf /tmp/uganda-platform

    print_success "Uganda platform migrations completed"
fi

# ============================================
# 10. Display Service Status
# ============================================
print_status "Service Status:"
echo ""
docker compose -f docker-compose.production.yml ps

# ============================================
# 11. Display Access Information
# ============================================
echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "============================================"
echo "  Access Information"
echo "============================================"
echo ""
echo "Storefront (Customer site):"
echo "  http://${SERVER_IP}"
echo ""
echo "Admin Dashboard:"
echo "  http://${SERVER_IP}/dashboard/"
echo ""
echo "GraphQL API:"
echo "  http://${SERVER_IP}/graphql/"
echo ""
echo "============================================"
echo ""

if [ "$1" == "--first-time" ]; then
    echo "Next steps:"
    echo "1. Access the admin dashboard and configure your shop"
    echo "2. Add products and categories"
    echo "3. Configure Mobile Money payment methods"
    echo "4. Test SMS notifications"
    echo "5. Set up SSL certificate (see setup-ssl.sh)"
    echo ""
fi

print_warning "IMPORTANT: Your site is currently using HTTP (not secure)"
print_warning "Run './setup-ssl.sh' to enable HTTPS with SSL certificate"
echo ""

# ============================================
# 12. Useful Commands
# ============================================
echo "Useful commands:"
echo "  View logs:        docker compose -f docker-compose.production.yml logs -f"
echo "  Restart services: docker compose -f docker-compose.production.yml restart"
echo "  Stop services:    docker compose -f docker-compose.production.yml down"
echo "  Backup database:  ./backup.sh"
echo ""

print_success "Deployment complete! 🇺🇬"
