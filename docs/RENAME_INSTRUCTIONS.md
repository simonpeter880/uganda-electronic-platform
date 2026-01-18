# Directory Rename Instructions

To avoid conflicts with your existing Saleor repositories on GitHub, you need to rename the following directories:

## Required Renames

### 1. Rename Backend Directory

**Current name:** `saleor-platform`
**New name:** `saleor-platform-uganda`

```bash
cd /home/cymo/project-two
mv saleor-platform saleor-platform-uganda
```

### 2. Rename Frontend Directory

**Current name:** `storefront`
**New name:** `storefront-uganda`

```bash
cd /home/cymo/project-two
mv storefront storefront-uganda
```

## After Renaming

Once you've renamed these directories, all the deployment files are already configured to use the new names:

### Files Already Updated

- ✅ [docker-compose.production.yml](docker-compose.production.yml)
- ✅ [deploy.sh](deploy.sh)
- ✅ [README.md](README.md)
- ✅ [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- ✅ [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- ✅ [DEPLOYMENT_README.md](DEPLOYMENT_README.md)
- ✅ [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

### Expected Project Structure After Rename

```
project-two/
├── saleor-platform-uganda/       # ← Renamed from saleor-platform
│   ├── migrations/
│   │   └── uganda-platform/
│   ├── docker-compose.yml
│   └── backend.env
│
├── storefront-uganda/            # ← Renamed from storefront
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── uganda-backend-code/          # (no change)
│
├── docker-compose.production.yml # Deployment config
├── .env.production.example       # Environment template
├── deploy.sh                     # Deployment script
├── setup-ssl.sh                  # SSL setup script
├── backup.sh                     # Backup script
└── DEPLOYMENT_*.md               # Documentation
```

## Verification

After renaming, verify the structure:

```bash
cd /home/cymo/project-two
ls -la

# You should see:
# - saleor-platform-uganda/
# - storefront-uganda/
# - uganda-backend-code/
# - docker-compose.production.yml
# - deploy.sh
# - etc.
```

## GitHub Repository Names

When pushing to GitHub, you can use these repository names:

- **Backend**: `saleor-platform-uganda`
- **Frontend**: `storefront-uganda`

This keeps them separate from your existing `saleor-platform` and `storefront` repositories.

## Quick Rename Commands

Run these commands to rename both directories:

```bash
cd /home/cymo/project-two

# Rename backend
mv saleor-platform saleor-platform-uganda

# Rename frontend
mv storefront storefront-uganda

# Verify
ls -d */
```

## Ready to Deploy

After renaming, you're ready to deploy:

```bash
# Copy environment template
cp .env.production.example .env.production

# Edit with your values
nano .env.production

# Deploy
./deploy.sh --first-time
```

---

**All deployment files have been pre-configured with the new directory names!**
