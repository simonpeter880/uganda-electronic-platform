#!/bin/bash
# Uganda Electronics Platform - Migration Runner
# This script runs all database migrations in order

set -e  # Exit on error

echo "========================================"
echo "Uganda Electronics Platform Migrations"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Database connection (modify these or use environment variables)
DB_USER="${DB_USER:-saleor}"
DB_NAME="${DB_NAME:-saleor}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Function to run a migration
run_migration() {
    local migration_file=$1
    local migration_name=$(basename "$migration_file")

    echo -n "Running: $migration_name ... "

    if docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$migration_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Check if we're in the saleor-platform directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Please run this script from the saleor-platform directory${NC}"
    exit 1
fi

# Check if database is running
echo "Checking database connection..."
if ! docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to database. Is it running?${NC}"
    echo "Try: docker compose up -d db"
    exit 1
fi
echo -e "${GREEN}✓ Database connection OK${NC}"
echo ""

# Backup warning
echo -e "${YELLOW}WARNING: This will modify your database!${NC}"
echo "It is recommended to backup your database first."
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Migration cancelled."
    exit 0
fi

echo ""
echo "Starting migrations..."
echo "========================================"
echo ""

# Run migrations in order
FAILED=0

run_migration "$SCRIPT_DIR/001_currency_configuration.sql" || FAILED=1
run_migration "$SCRIPT_DIR/002_uganda_districts.sql" || FAILED=1
run_migration "$SCRIPT_DIR/003_seed_uganda_districts.sql" || FAILED=1
run_migration "$SCRIPT_DIR/004_mobile_money_payments.sql" || FAILED=1
run_migration "$SCRIPT_DIR/005_uganda_delivery.sql" || FAILED=1
run_migration "$SCRIPT_DIR/006_sms_notifications.sql" || FAILED=1
run_migration "$SCRIPT_DIR/007_electronics_features.sql" || FAILED=1
run_migration "$SCRIPT_DIR/008_installment_payments.sql" || FAILED=1
run_migration "$SCRIPT_DIR/009_shop_information.sql" || FAILED=1

echo ""
echo "========================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All migrations completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart the Saleor API: docker compose restart api"
    echo "2. Update your Django models to match the new schema"
    echo "3. Configure Mobile Money API credentials"
    echo "4. Configure Africa's Talking SMS credentials"
    echo "5. Update your storefront to use the new Uganda features"
else
    echo -e "${RED}✗ Some migrations failed. Please check the errors above.${NC}"
    exit 1
fi
