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
