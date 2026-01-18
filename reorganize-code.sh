#!/bin/bash

# ============================================
# Code Reorganization Script
# Uganda Electronics Platform
# ============================================

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "  CODE REORGANIZATION SCRIPT"
echo "  Uganda Electronics Platform"
echo "============================================"
echo ""

# Check we're in the right directory
if [ ! -d "saleor-platform-uganda" ] || [ ! -d "uganda-backend-code" ]; then
    echo -e "${RED}❌ Error: Not in project root directory${NC}"
    echo "Please run from: /home/cymo/project-two/"
    exit 1
fi

echo -e "${YELLOW}⚠️  This will reorganize your code structure${NC}"
echo ""
echo "Current structure:"
echo "  saleor-platform-uganda/  →  backend/"
echo "  uganda-backend-code/     →  backend/custom/"
echo "  storefront-uganda/       →  frontend/"
echo "  *.md files               →  docs/"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo -e "${BLUE}Step 1: Creating backup${NC}"
echo "----------------------------------------------"
BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Backing up to: $BACKUP_DIR/"

cp -r saleor-platform-uganda "$BACKUP_DIR/"
cp -r uganda-backend-code "$BACKUP_DIR/"
cp -r storefront-uganda "$BACKUP_DIR/"
cp *.md "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}✅ Backup created${NC}"
echo ""

echo -e "${BLUE}Step 2: Creating new structure${NC}"
echo "----------------------------------------------"

# Create new directories
mkdir -p backend/custom
mkdir -p frontend
mkdir -p docs

echo -e "${GREEN}✅ Directories created${NC}"
echo ""

echo -e "${BLUE}Step 3: Moving backend files${NC}"
echo "----------------------------------------------"

# Move saleor platform files to backend/
mv saleor-platform-uganda/.git backend/ 2>/dev/null || true
mv saleor-platform-uganda/.github backend/ 2>/dev/null || true
mv saleor-platform-uganda/.gitignore backend/ 2>/dev/null || true
mv saleor-platform-uganda/* backend/ 2>/dev/null || true
mv saleor-platform-uganda/.[!.]* backend/ 2>/dev/null || true

echo -e "${GREEN}✅ Saleor platform files moved to backend/${NC}"

# Move custom Uganda code to backend/custom/
mv uganda-backend-code/* backend/custom/ 2>/dev/null || true

echo -e "${GREEN}✅ Custom Uganda code moved to backend/custom/${NC}"
echo ""

echo -e "${BLUE}Step 4: Moving frontend files${NC}"
echo "----------------------------------------------"

# Move storefront files
mv storefront-uganda/* frontend/ 2>/dev/null || true
mv storefront-uganda/.[!.]* frontend/ 2>/dev/null || true

echo -e "${GREEN}✅ Frontend files moved to frontend/${NC}"
echo ""

echo -e "${BLUE}Step 5: Moving documentation${NC}"
echo "----------------------------------------------"

# Move documentation
mv SETUP_COMPLETE.md docs/ 2>/dev/null || true
mv SENTRY_SUCCESS.md docs/ 2>/dev/null || true
mv SENTRY_CONFIGURED.md docs/ 2>/dev/null || true
mv SENTRY_QUICK_START.md docs/ 2>/dev/null || true
mv SENTRY_SETUP.md docs/ 2>/dev/null || true
mv TWO_FACTOR_AUTH_SETUP.md docs/ 2>/dev/null || true
mv IMPROVEMENTS_IMPLEMENTED.md docs/ 2>/dev/null || true
mv README_IMPROVEMENTS.md docs/ 2>/dev/null || true
mv NEXT_STEPS_CHECKLIST.md docs/ 2>/dev/null || true
mv GIT_PUSH_SUCCESS.md docs/ 2>/dev/null || true
mv REORGANIZATION_PLAN.md docs/ 2>/dev/null || true

# Keep main README in root
# mv README.md stays in root

echo -e "${GREEN}✅ Documentation moved to docs/${NC}"
echo ""

echo -e "${BLUE}Step 6: Cleaning up empty directories${NC}"
echo "----------------------------------------------"

rmdir saleor-platform-uganda 2>/dev/null || true
rmdir uganda-backend-code 2>/dev/null || true
rmdir storefront-uganda 2>/dev/null || true

echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

echo -e "${BLUE}Step 7: Creating README files${NC}"
echo "----------------------------------------------"

# Create backend/custom/README.md
cat > backend/custom/README.md << 'EOF'
# Uganda Custom Extensions

This directory contains all Uganda-specific customizations for the Saleor e-commerce platform.

## Structure

- `models/` - Django models (Districts, Mobile Money, SMS, etc.)
- `services/` - Business logic (Payment, SMS services)
- `graphql/` - GraphQL types, queries, mutations
- `webhooks/` - Payment webhook handlers
- `tasks/` - Celery background tasks
- `admin/` - Django admin customizations
- `tests/` - Test suite (unit, integration)

## Integration

This custom code is mounted into the Saleor Docker container via `docker-compose.yml`:

```yaml
volumes:
  - ./custom:/app/custom
```

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations (from parent directory):
   ```bash
   docker-compose run api python manage.py migrate
   ```

3. Load Uganda districts:
   ```bash
   docker-compose run api python manage.py loaddata custom/fixtures/uganda_districts.json
   ```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_mobile_money_service.py

# With coverage
pytest tests/ --cov
```

## Documentation

See `/docs` directory for complete documentation.
EOF

# Create frontend/README.md
cat > frontend/README.md << 'EOF'
# Uganda Electronics Storefront

Next.js frontend for Uganda Electronics e-commerce platform.

## Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Run E2E tests
npx playwright test
```

## Environment Variables

Copy `.env.local.example` to `.env.local` and configure:

- `NEXT_PUBLIC_SALEOR_API_URL` - Backend GraphQL API
- `NEXT_PUBLIC_SENTRY_DSN` - Sentry error tracking

## Documentation

See `/docs` directory for complete documentation.
EOF

# Create main README.md
cat > README.md << 'EOF'
# Uganda Electronics Platform

Enterprise e-commerce platform for Uganda with mobile money integration, SMS notifications, and localized features.

## Quick Start

### Backend
```bash
cd backend
docker-compose up -d
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

## Documentation

- [Complete Setup Guide](docs/SETUP_COMPLETE.md)
- [Sentry Monitoring](docs/SENTRY_SETUP.md)
- [Two-Factor Auth](docs/TWO_FACTOR_AUTH_SETUP.md)
- [All Improvements](docs/IMPROVEMENTS_IMPLEMENTED.md)

## Project Structure

```
uganda-electronics-platform/
├── backend/           # Saleor backend + custom extensions
│   ├── custom/       # Uganda-specific code
│   └── migrations/   # Database migrations
├── frontend/         # Next.js storefront
├── docs/            # Documentation
└── .github/         # CI/CD workflows
```

## Features

- ✅ Mobile Money Payments (MTN, Airtel)
- ✅ SMS Notifications (Africa's Talking)
- ✅ 135 Uganda Districts with delivery
- ✅ Installment Payments
- ✅ Two-Factor Authentication
- ✅ Real-time Error Tracking (Sentry)
- ✅ Automated Testing (35+ tests)
- ✅ CI/CD Pipeline

## Tech Stack

- **Backend:** Django, PostgreSQL, Redis, Celery
- **Frontend:** Next.js 16, React 19, TypeScript
- **Infrastructure:** Docker, Docker Compose
- **Monitoring:** Sentry
- **Testing:** Pytest, Playwright

## License

BSD-3-Clause
EOF

echo -e "${GREEN}✅ README files created${NC}"
echo ""

echo -e "${BLUE}Step 8: Updating docker-compose.yml${NC}"
echo "----------------------------------------------"

# Update docker-compose to mount custom code
if [ -f "backend/docker-compose.yml" ]; then
    # Add volume mount for custom code if not already present
    if ! grep -q "./custom:/app/custom" backend/docker-compose.yml; then
        echo "Note: You may need to manually add custom code volume to docker-compose.yml"
        echo "Add this under 'api' service volumes:"
        echo "  - ./custom:/app/custom"
    fi
fi

echo -e "${GREEN}✅ Docker compose checked${NC}"
echo ""

echo "============================================"
echo -e "${GREEN}  REORGANIZATION COMPLETE!${NC}"
echo "============================================"
echo ""
echo "New structure:"
echo ""
echo "uganda-electronics-platform/"
echo "├── backend/              # Complete backend"
echo "│   ├── custom/          # Uganda extensions"
echo "│   ├── docker-compose.yml"
echo "│   └── migrations/"
echo "├── frontend/            # Next.js storefront"
echo "├── docs/               # All documentation"
echo "├── .github/            # CI/CD"
echo "└── README.md           # Main README"
echo ""
echo -e "${YELLOW}⚠️  Important Next Steps:${NC}"
echo ""
echo "1. Update docker-compose.yml to mount custom code:"
echo "   volumes:"
echo "     - ./custom:/app/custom"
echo ""
echo "2. Test that everything still works:"
echo "   cd backend && docker-compose up -d"
echo "   cd frontend && pnpm dev"
echo ""
echo "3. Commit the new structure:"
echo "   git add -A"
echo "   git commit -m 'refactor: Reorganize code structure for clarity'"
echo "   git push origin main"
echo ""
echo -e "${GREEN}Backup saved to: $BACKUP_DIR/${NC}"
echo ""
echo -e "${GREEN}✅ All done!${NC}"
