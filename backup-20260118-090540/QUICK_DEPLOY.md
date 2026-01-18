# Quick Deploy Guide - TL;DR Version

For experienced users who want to deploy quickly.

## Prerequisites
- Ubuntu 22.04 Droplet (2GB+ RAM)
- Docker & Docker Compose installed
- SSH access

## 1. Upload Project

```bash
# On your local machine
cd /home/cymo/project-two
tar -czf project.tar.gz --exclude='node_modules' --exclude='.git' .
scp project.tar.gz root@YOUR_SERVER_IP:/opt/

# On the server
cd /opt
tar -xzf project.tar.gz
mv project-two uganda-electronics
cd uganda-electronics
```

## 2. Configure Environment

```bash
cp .env.production.example .env.production
nano .env.production
```

**Essential variables to set:**
```bash
SERVER_IP=YOUR_DROPLET_IP
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
NEXT_PUBLIC_SALEOR_API_URL=http://YOUR_DROPLET_IP/graphql/
NEXT_PUBLIC_STOREFRONT_URL=http://YOUR_DROPLET_IP
DASHBOARD_URL=http://YOUR_DROPLET_IP/dashboard/
SHOP_NAME=Your Shop Name
SHOP_PHONE=256700123456
SHOP_EMAIL=info@yourshop.ug
```

## 3. Deploy

```bash
chmod +x *.sh
./deploy.sh --first-time
```

Wait 5-10 minutes. Create admin account when prompted.

## 4. Run Uganda Migrations

```bash
cd saleor-platform-uganda/migrations/uganda-platform
chmod +x run_migrations.sh
./run_migrations.sh
```

## 5. Access

- Storefront: `http://YOUR_SERVER_IP`
- Admin: `http://YOUR_SERVER_IP/dashboard/`
- GraphQL: `http://YOUR_SERVER_IP/graphql/`

## 6. (Optional) Setup SSL

If you have a domain:

```bash
# Point domain A record to server IP first!
./setup-ssl.sh
```

## 7. Setup Backups

```bash
# Add to crontab
crontab -e
# Add: 0 2 * * * cd /opt/uganda-electronics && ./backup.sh >> /var/log/backup.log 2>&1
```

## Common Commands

```bash
# View logs
docker compose -f docker-compose.production.yml logs -f

# Restart
docker compose -f docker-compose.production.yml restart

# Stop
docker compose -f docker-compose.production.yml down

# Start
docker compose -f docker-compose.production.yml up -d

# Backup
./backup.sh

# Check status
docker compose -f docker-compose.production.yml ps
```

## Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## Production Checklist

Before going live:

1. [ ] Add real products
2. [ ] Configure Mobile Money API keys (production mode)
3. [ ] Configure Africa's Talking API keys (production mode)
4. [ ] Test complete checkout flow
5. [ ] Set up SSL certificate
6. [ ] Enable automatic backups
7. [ ] Test SMS notifications

## Cost Estimate

- Droplet: $18/month
- SMS: ~$50-100/month
- Domain: ~$12/year
- **Total**: ~$75-125/month

## Need Help?

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

**Deployment time: ~30 minutes** ⏱️
