#!/bin/bash

# ============================================
# Sentry Setup Script for Uganda Electronics
# ============================================

set -e  # Exit on error

echo "============================================"
echo "  SENTRY SETUP FOR UGANDA ELECTRONICS"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "setup-sentry.sh" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Installing Sentry SDK for Backend${NC}"
echo "----------------------------------------------"
cd uganda-backend-code
pip install -r requirements-sentry.txt
echo -e "${GREEN}✅ Backend Sentry SDK installed${NC}"
echo ""

echo -e "${BLUE}Step 2: Installing Sentry SDK for Frontend${NC}"
echo "----------------------------------------------"
cd ../storefront-uganda
if command -v pnpm &> /dev/null; then
    echo "Using pnpm..."
    pnpm add @sentry/nextjs
else
    echo "Using npm..."
    npm install @sentry/nextjs
fi
echo -e "${GREEN}✅ Frontend Sentry SDK installed${NC}"
echo ""

cd ..

echo -e "${BLUE}Step 3: Verifying Environment Configuration${NC}"
echo "----------------------------------------------"
if [ -f ".env.development" ]; then
    if grep -q "SENTRY_DSN" .env.development; then
        echo -e "${GREEN}✅ Sentry DSN found in .env.development${NC}"
    else
        echo -e "${YELLOW}⚠️  Sentry DSN not found in .env.development${NC}"
    fi
else
    echo -e "${RED}❌ .env.development not found${NC}"
fi

if [ -f "storefront-uganda/.env.local" ]; then
    if grep -q "NEXT_PUBLIC_SENTRY_DSN" storefront-uganda/.env.local; then
        echo -e "${GREEN}✅ Frontend Sentry DSN found in .env.local${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend Sentry DSN not found in .env.local${NC}"
    fi
else
    echo -e "${RED}❌ storefront-uganda/.env.local not found${NC}"
fi
echo ""

echo -e "${BLUE}Step 4: Testing Backend Sentry Integration${NC}"
echo "----------------------------------------------"
echo "Running backend Sentry test..."
cd uganda-backend-code
python test_sentry.py
cd ..
echo ""

echo "============================================"
echo -e "${GREEN}  SENTRY SETUP COMPLETED!${NC}"
echo "============================================"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Check your Sentry dashboard:"
echo "   https://sentry.io/"
echo ""
echo "2. You should see test events from the backend test"
echo ""
echo "3. Start your services to test frontend Sentry:"
echo "   cd storefront-uganda && pnpm dev"
echo ""
echo "4. Review the Sentry documentation:"
echo "   cat SENTRY_SETUP.md"
echo ""
echo -e "${GREEN}✅ All set! Sentry is now monitoring your application.${NC}"
echo ""
