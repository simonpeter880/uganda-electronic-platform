# Code Reorganization Plan

## Current Structure (Confusing)

```
project-two/
├── saleor-platform/              # ❓ Unused? Root directory
├── saleor-platform-uganda/       # 🔧 Saleor Docker setup
│   ├── docker-compose.yml
│   ├── migrations/
│   └── .env files
├── uganda-backend-code/          # 📦 Custom Uganda code
│   ├── models/
│   ├── services/
│   ├── graphql/
│   ├── webhooks/
│   ├── tasks/
│   ├── tests/
│   └── admin/
└── storefront-uganda/            # 🎨 Next.js frontend
```

**Problems:**
1. ❓ Unclear what `saleor-platform-uganda` vs `uganda-backend-code` are
2. ❓ Custom code is separate from Saleor Docker setup
3. ❓ Not obvious where to add new backend features
4. ❓ Deployment confusion

---

## Recommended Structure (Clear)

### Option 1: Integrate Custom Code into Saleor Platform ✅ RECOMMENDED

```
project-two/
├── backend/                      # 🔧 Complete backend (renamed from saleor-platform-uganda)
│   ├── docker-compose.yml
│   ├── docker-compose.production.yml
│   ├── migrations/               # Database migrations
│   ├── saleor/                   # Saleor core (mounted from Docker)
│   └── custom/                   # 📦 Uganda custom code (merged from uganda-backend-code)
│       ├── __init__.py
│       ├── models/
│       │   └── uganda_models.py
│       ├── services/
│       │   ├── mobile_money.py
│       │   ├── http_client.py
│       │   └── sms_service.py
│       ├── graphql/
│       │   ├── types.py
│       │   ├── queries.py
│       │   └── mutations.py
│       ├── webhooks/
│       │   ├── mobile_money_webhooks_v2.py
│       │   └── webhook_utils.py
│       ├── tasks/
│       │   └── celery_tasks.py
│       ├── admin/
│       │   └── uganda_admin.py
│       ├── tests/
│       │   ├── unit/
│       │   ├── integration/
│       │   └── conftest.py
│       ├── sentry_config.py
│       ├── two_factor_auth.py
│       └── requirements.txt      # Custom requirements
│
├── frontend/                     # 🎨 Next.js storefront (renamed from storefront-uganda)
│   ├── src/
│   ├── e2e/
│   ├── package.json
│   └── ...
│
└── docs/                        # 📚 Documentation
    ├── SETUP_COMPLETE.md
    ├── SENTRY_SETUP.md
    ├── TWO_FACTOR_AUTH_SETUP.md
    └── ...
```

**Benefits:**
- ✅ Clear separation: `backend/` vs `frontend/`
- ✅ Custom code integrated with Saleor setup
- ✅ Easy to deploy (one backend folder)
- ✅ No confusion about structure

---

### Option 2: Keep Separate but Rename ⚠️ Alternative

```
project-two/
├── saleor-backend/              # Renamed from saleor-platform-uganda
│   ├── docker-compose.yml
│   ├── migrations/
│   └── ...
│
├── uganda-extensions/           # Renamed from uganda-backend-code
│   ├── models/
│   ├── services/
│   └── ...
│
├── frontend/                    # Renamed from storefront-uganda
│   └── ...
```

**Benefits:**
- ✅ Clearer names
- ⚠️ Still requires manual integration

---

## Recommended Implementation

**Choose Option 1** - Integrate everything into a clean structure.

### Step-by-Step Migration

1. **Create new structure:**
   ```bash
   mkdir -p backend/custom
   mkdir -p frontend
   mkdir -p docs
   ```

2. **Move Saleor platform files:**
   ```bash
   mv saleor-platform-uganda/* backend/
   ```

3. **Move custom Uganda code:**
   ```bash
   mv uganda-backend-code/* backend/custom/
   ```

4. **Move frontend:**
   ```bash
   mv storefront-uganda/* frontend/
   ```

5. **Move documentation:**
   ```bash
   mv *.md docs/
   ```

6. **Update docker-compose.yml:**
   ```yaml
   # Mount custom code into Saleor container
   volumes:
     - ./custom:/app/custom
   ```

7. **Update Saleor settings to load custom code:**
   ```python
   # In Saleor settings.py
   INSTALLED_APPS += ['custom']
   ```

---

## Final Structure (Recommended)

```
uganda-electronics-platform/
│
├── backend/                     # Complete backend system
│   ├── docker-compose.yml       # Development
│   ├── docker-compose.production.yml
│   ├── .env.example
│   ├── migrations/              # SQL migrations
│   │   ├── 001_currency_configuration.sql
│   │   ├── 002_uganda_districts.sql
│   │   └── ...
│   ├── custom/                  # Uganda-specific extensions
│   │   ├── README.md           # Custom code documentation
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── services/
│   │   ├── graphql/
│   │   ├── webhooks/
│   │   ├── tasks/
│   │   ├── admin/
│   │   ├── tests/
│   │   ├── sentry_config.py
│   │   ├── two_factor_auth.py
│   │   └── requirements.txt
│   └── common.env
│
├── frontend/                    # Next.js storefront
│   ├── src/
│   ├── e2e/
│   ├── public/
│   ├── package.json
│   ├── .env.local
│   └── README.md
│
├── docs/                        # All documentation
│   ├── README.md               # Main overview
│   ├── SETUP_COMPLETE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── SENTRY_SETUP.md
│   ├── TWO_FACTOR_AUTH_SETUP.md
│   └── IMPROVEMENTS_IMPLEMENTED.md
│
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
│
├── .gitignore
├── .env.development
└── README.md                   # Project root README
```

---

## Implementation Script

I can create an automated script to reorganize everything safely.

**Benefits:**
1. ✅ Backup created first
2. ✅ Atomic operation (all or nothing)
3. ✅ Git-aware (preserves history)
4. ✅ Updates all references automatically

---

## What This Achieves

**Before:** 😕 Confusing structure
- "Where do I add Uganda features?"
- "What's the difference between saleor-platform-uganda and uganda-backend-code?"
- "How do I deploy this?"

**After:** 😊 Crystal clear
- **Backend** = Everything backend (Saleor + custom code)
- **Frontend** = Everything frontend (Next.js)
- **Docs** = All documentation
- Custom code in `backend/custom/` folder

---

## Next Steps

**Option A - Auto Migration (Recommended):**
I'll create a migration script that does everything automatically.

**Option B - Manual Migration:**
Follow step-by-step guide.

**Option C - Keep Current Structure:**
Just add a STRUCTURE.md explaining what each folder is.

---

Which option would you prefer?
