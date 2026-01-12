#!/bin/bash

# ============================================
# Database Backup Script
# ============================================
# Creates a backup of the PostgreSQL database

set -e

echo "💾 Creating database backup..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Create backups directory
mkdir -p backups

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/saleor_backup_${TIMESTAMP}.sql"

print_status "Backing up database..."

# Create backup
docker compose -f docker-compose.production.yml exec -T db pg_dump -U saleor saleor > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)

print_success "Backup created: ${BACKUP_FILE}.gz (${BACKUP_SIZE})"

# Keep only last 7 days of backups
print_status "Cleaning old backups (keeping last 7 days)..."
find backups/ -name "saleor_backup_*.sql.gz" -mtime +7 -delete

print_success "Backup complete!"
