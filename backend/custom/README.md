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
