# Deployment Files Overview

This directory contains everything you need to deploy your Uganda Electronics Platform to DigitalOcean.

## 📁 Deployment Files Created

### Configuration Files

#### [docker-compose.production.yml](docker-compose.production.yml) (3.6K)
Production Docker Compose configuration that orchestrates all services:
- PostgreSQL database
- Redis cache
- Saleor API backend
- Celery worker
- Saleor dashboard
- Next.js storefront
- Nginx reverse proxy

**Features:**
- Health checks for all services
- Automatic restart policies
- Persistent data volumes
- Internal networking
- Production-ready settings

#### [.env.production.example](.env.production.example) (3.3K)
Template for production environment variables with detailed comments.

**Includes:**
- Server configuration
- Database credentials
- Django settings
- Mobile Money API keys (MTN, Airtel)
- SMS API keys (Africa's Talking)
- Shop information
- Email configuration
- Security settings

**Usage:**
```bash
cp .env.production.example .env.production
nano .env.production  # Fill in your values
```

#### [nginx/nginx.conf](nginx/nginx.conf) (4.5K)
Nginx reverse proxy configuration.

**Features:**
- Routes traffic to correct services
- Rate limiting for API endpoints
- Gzip compression
- Security headers
- Static file caching
- CORS configuration for GraphQL
- Health check endpoint
- SSL configuration (commented out by default)

### Deployment Scripts

#### [deploy.sh](deploy.sh) (8.6K) ⭐
**Main deployment script** - Deploy or update your application.

**What it does:**
1. Checks system requirements (Docker, memory, disk)
2. Validates environment configuration
3. Creates necessary directories
4. Pulls Docker images
5. Builds storefront
6. Starts all services
7. Waits for services to be ready
8. Runs database migrations
9. Creates superuser (first-time only)
10. Collects static files
11. Runs Uganda platform migrations
12. Displays access information

**Usage:**
```bash
# First deployment
./deploy.sh --first-time

# Subsequent deployments/updates
./deploy.sh
```

**Requirements:**
- Docker and Docker Compose installed
- `.env.production` file configured
- Minimum 2GB RAM, 10GB disk space

#### [setup-ssl.sh](setup-ssl.sh) (13K)
Sets up HTTPS with free SSL certificates from Let's Encrypt.

**What it does:**
1. Installs certbot if needed
2. Stops nginx temporarily
3. Obtains SSL certificate
4. Copies certificates to nginx
5. Updates nginx config for HTTPS
6. Updates environment variables
7. Rebuilds and restarts services
8. Sets up automatic renewal (monthly)

**Usage:**
```bash
./setup-ssl.sh
```

**Requirements:**
- Domain name pointing to server
- Port 80 accessible
- Initial deployment completed

#### [backup.sh](backup.sh) (1.1K)
Creates database backups with compression.

**What it does:**
1. Creates timestamped backup of PostgreSQL database
2. Compresses backup with gzip
3. Stores in `backups/` directory
4. Automatically deletes backups older than 7 days

**Usage:**
```bash
# Manual backup
./backup.sh

# Automated daily backups (add to crontab)
0 2 * * * cd /opt/uganda-electronics && ./backup.sh >> /var/log/backup.log 2>&1
```

### Documentation

#### [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) (15K) 📖
**Comprehensive deployment documentation** with step-by-step instructions.

**Covers:**
- DigitalOcean Droplet setup
- Software installation
- Project upload methods
- Environment configuration
- Initial deployment
- Uganda platform migrations
- Shop configuration
- SSL setup with domain
- Backup configuration
- Monitoring and maintenance
- Troubleshooting common issues
- Security best practices
- Performance optimization
- Cost estimates

**Best for:** First-time deployers, detailed reference

#### [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) (9.9K) ✅
**Interactive checklist** for deployment process.

**Includes:**
- Pre-deployment preparation
- Step-by-step tasks with checkboxes
- Configuration templates to fill in
- Testing procedures
- Go-live preparation
- Post-launch tasks
- Quick reference section

**Best for:** Following deployment step-by-step, ensuring nothing is missed

#### [QUICK_DEPLOY.md](QUICK_DEPLOY.md) (2.7K) ⚡
**TL;DR version** for experienced users.

**Contains:**
- Essential commands only
- Minimal explanations
- Quick reference commands
- Cost estimates

**Best for:** Experienced DevOps users, quick deployments

#### [.gitignore](.gitignore)
Prevents sensitive files from being committed to version control.

**Excludes:**
- Environment files (`.env*`)
- Backups (`backups/`, `*.sql`)
- Logs (`nginx/logs/`, `*.log`)
- SSL certificates
- Docker volumes
- Node modules
- Build artifacts

## 🚀 Quick Start

### New to deployment?
1. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) fully
2. Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) step-by-step
3. Use scripts as directed in the guides

### Experienced with Docker/deployments?
1. Skim [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
2. Configure `.env.production`
3. Run `./deploy.sh --first-time`
4. (Optional) Run `./setup-ssl.sh` for HTTPS

## 📋 Deployment Flow

```
1. Create DigitalOcean Droplet
   ↓
2. Install Docker & Docker Compose
   ↓
3. Upload project files
   ↓
4. Configure .env.production
   ↓
5. Run ./deploy.sh --first-time
   ↓
6. Run Uganda migrations
   ↓
7. Access site and configure shop
   ↓
8. (Optional) Setup SSL with ./setup-ssl.sh
   ↓
9. Setup backups with ./backup.sh
   ↓
10. Go live! 🎉
```

## 🔑 Key Features

### Production-Ready
- ✅ Health checks
- ✅ Automatic restarts
- ✅ Persistent data storage
- ✅ Resource limits
- ✅ Security headers
- ✅ Rate limiting
- ✅ Gzip compression

### Easy Management
- ✅ One-command deployment
- ✅ Automated SSL setup
- ✅ Automated backups
- ✅ Simple log viewing
- ✅ Easy service restarts

### Secure by Default
- ✅ Environment variable isolation
- ✅ Firewall configuration
- ✅ SSL/HTTPS support
- ✅ Security headers
- ✅ Sensitive file exclusion

## 🛠️ Common Tasks

### Deploy/Update Application
```bash
./deploy.sh
```

### View Logs
```bash
docker compose -f docker-compose.production.yml logs -f [service]
```

### Restart Services
```bash
docker compose -f docker-compose.production.yml restart
```

### Backup Database
```bash
./backup.sh
```

### Setup SSL
```bash
./setup-ssl.sh
```

### Access Database
```bash
docker compose -f docker-compose.production.yml exec db psql -U saleor -d saleor
```

### Create Superuser
```bash
docker compose -f docker-compose.production.yml exec api python manage.py createsuperuser
```

## 📊 Architecture

```
Internet
   ↓
Nginx (Port 80/443)
   ├─→ Next.js Storefront (Port 3000)
   ├─→ Saleor API (Port 8000)
   │    ├─→ PostgreSQL (Port 5432)
   │    └─→ Redis (Port 6379)
   ├─→ Saleor Dashboard (Port 80)
   └─→ Static/Media Files
```

## 💰 Cost Breakdown

### Required
- **Droplet (2GB)**: $18/month
- **Domain** (optional): $12/year

### Usage-Based
- **SMS**: ~$50-100/month (1000-2000 messages)
- **Mobile Money fees**: 1-2% of transactions

### Optional
- **Managed Database**: $15/month
- **Spaces (Object Storage)**: $5/month
- **Monitoring**: $5-10/month

**Estimated Total**: $75-150/month

## 🔒 Security Checklist

- [ ] Strong passwords in `.env.production`
- [ ] `.env.production` not committed to git
- [ ] Firewall configured (ports 22, 80, 443 only)
- [ ] SSL certificate installed
- [ ] Regular backups enabled
- [ ] System updates enabled
- [ ] SSH key authentication (password disabled)
- [ ] Non-default SSH port (recommended)
- [ ] Fail2ban installed

## 📞 Support

### Documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Checklist
- [README.md](README.md) - Platform overview

### External Resources
- [DigitalOcean Docs](https://docs.digitalocean.com/)
- [Saleor Docs](https://docs.saleor.io/)
- [Docker Docs](https://docs.docker.com/)

### Troubleshooting
See the "Common Issues and Solutions" section in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🎯 Next Steps

1. Choose your deployment path:
   - **First time?** → [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
   - **Want checklist?** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
   - **Experienced?** → [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

2. Follow the guide step-by-step

3. Deploy your platform

4. Configure your shop

5. Go live! 🚀

## 📝 Version Info

- **Platform**: Uganda Electronics E-Commerce
- **Backend**: Saleor 3.22
- **Frontend**: Next.js 16
- **Database**: PostgreSQL 15
- **Cache**: Redis/Valkey 8.1
- **Proxy**: Nginx (Alpine)
- **Container**: Docker Compose v3.8

---

**Ready to deploy? Pick a guide above and let's get started! 🇺🇬**
