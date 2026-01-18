# Deployment Checklist - Uganda Electronics Platform

Use this checklist to ensure a smooth deployment to DigitalOcean.

## Pre-Deployment Preparation

### DigitalOcean Account Setup
- [ ] Create DigitalOcean account
- [ ] Add payment method
- [ ] Create SSH key pair (if not already done)

### Domain Name (Optional but Recommended)
- [ ] Purchase domain name (e.g., from Namecheap, GoDaddy, or DigitalOcean)
- [ ] Have domain registrar login credentials ready

### API Credentials (Get these ready)
- [ ] **MTN Mobile Money**
  - Sign up at https://momodeveloper.mtn.com/
  - Get sandbox API keys for testing
- [ ] **Airtel Money**
  - Contact Airtel Money Uganda for merchant account
  - Get UAT (testing) credentials
- [ ] **Africa's Talking**
  - Sign up at https://africastalking.com/
  - Get sandbox credentials ($1 free credit for testing)

## Step 1: Create Droplet

- [ ] Log in to DigitalOcean
- [ ] Create new Droplet with:
  - [ ] Ubuntu 22.04 LTS
  - [ ] 2GB RAM, 2 vCPUs, 60GB SSD ($18/month minimum)
  - [ ] Datacenter: London or Frankfurt (closest to Uganda)
  - [ ] SSH key authentication
- [ ] Note down Droplet IP address: `___________________`
- [ ] Configure firewall rules:
  - [ ] Allow port 22 (SSH)
  - [ ] Allow port 80 (HTTP)
  - [ ] Allow port 443 (HTTPS)

## Step 2: Connect to Droplet

- [ ] SSH into Droplet: `ssh root@YOUR_DROPLET_IP`
- [ ] Update system: `apt update && apt upgrade -y`
- [ ] Install Docker: `curl -fsSL https://get.docker.com | sh`
- [ ] Install Git: `apt install -y git`
- [ ] Verify Docker: `docker --version`
- [ ] Verify Docker Compose: `docker compose version`

## Step 3: Upload Project Files

Choose one method:

### Option A: Git (if using version control)
- [ ] `cd /opt`
- [ ] `git clone YOUR_REPO_URL uganda-electronics`
- [ ] `cd uganda-electronics`

### Option B: SCP from local machine
- [ ] On local: `tar -czf project.tar.gz /home/cymo/project-two`
- [ ] On local: `scp project.tar.gz root@YOUR_DROPLET_IP:/opt/`
- [ ] On server: `cd /opt && tar -xzf project.tar.gz`
- [ ] On server: `mv project-two uganda-electronics`

### Option C: rsync from local machine
- [ ] `rsync -avz --exclude 'node_modules' /home/cymo/project-two/ root@YOUR_DROPLET_IP:/opt/uganda-electronics/`

## Step 4: Configure Environment

- [ ] `cd /opt/uganda-electronics`
- [ ] `cp .env.production.example .env.production`
- [ ] `nano .env.production`
- [ ] Update the following variables:

### Server Configuration
- [ ] `SERVER_IP=YOUR_DROPLET_IP`
- [ ] `ALLOWED_HOSTS=YOUR_DROPLET_IP,localhost,127.0.0.1,api`
- [ ] `ALLOWED_CLIENT_HOSTS=YOUR_DROPLET_IP,localhost`

### Database
- [ ] Generate secure DB password: `openssl rand -base64 32`
- [ ] `DB_PASSWORD=____________________` (paste generated password)

### Django
- [ ] Generate secret key: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] `SECRET_KEY=____________________` (paste generated key)

### URLs
- [ ] `NEXT_PUBLIC_SALEOR_API_URL=http://YOUR_DROPLET_IP/graphql/`
- [ ] `NEXT_PUBLIC_STOREFRONT_URL=http://YOUR_DROPLET_IP`
- [ ] `DASHBOARD_URL=http://YOUR_DROPLET_IP/dashboard/`

### Shop Information
- [ ] `SHOP_NAME=Your Shop Name`
- [ ] `SHOP_PHONE=256700123456`
- [ ] `SHOP_EMAIL=info@yourshop.ug`

### Payment Providers (Sandbox for Testing)
- [ ] `MTN_MOMO_API_KEY=____________________`
- [ ] `MTN_MOMO_SUBSCRIPTION_KEY=____________________`
- [ ] `AIRTEL_MONEY_CLIENT_ID=____________________`
- [ ] `AIRTEL_MONEY_CLIENT_SECRET=____________________`
- [ ] `AFRICAS_TALKING_USERNAME=____________________`
- [ ] `AFRICAS_TALKING_API_KEY=____________________`

- [ ] Save and close file (Ctrl+X, Y, Enter)

## Step 5: Initial Deployment

- [ ] Make scripts executable: `chmod +x *.sh`
- [ ] Run deployment: `./deploy.sh --first-time`
- [ ] Wait for services to start (5-10 minutes)
- [ ] Create admin account when prompted:
  - [ ] Email: `____________________`
  - [ ] Password: `____________________` (save this!)

## Step 6: Run Uganda Migrations

- [ ] `cd saleor-platform-uganda/migrations/uganda-platform`
- [ ] `chmod +x run_migrations.sh`
- [ ] `./run_migrations.sh`
- [ ] Verify districts loaded: Check for 135 districts

## Step 7: Verify Deployment

- [ ] Open browser to `http://YOUR_DROPLET_IP`
- [ ] Verify storefront loads
- [ ] Open `http://YOUR_DROPLET_IP/dashboard/`
- [ ] Login with admin credentials
- [ ] Verify dashboard loads

## Step 8: Configure Shop

### In Admin Dashboard

#### Site Settings
- [ ] Go to Configuration → Site Settings
- [ ] Update shop name
- [ ] Add contact information
- [ ] Set Uganda address

#### Create Categories
- [ ] Go to Catalog → Categories
- [ ] Create: Mobile Phones
- [ ] Create: Laptops
- [ ] Create: Tablets
- [ ] Create: Accessories
- [ ] Create: (other categories you need)

#### Add Test Product
- [ ] Go to Catalog → Products
- [ ] Create a test product
- [ ] Add name, price, description
- [ ] Upload product image
- [ ] Set IMEI/Serial number
- [ ] Publish product

#### Payment Methods
- [ ] Go to Configuration → Payment Methods
- [ ] Configure MTN Mobile Money
- [ ] Configure Airtel Money
- [ ] Configure Cash on Delivery
- [ ] Configure Cash in Store

## Step 9: Testing

### Test Storefront
- [ ] Browse to storefront
- [ ] View products
- [ ] Add product to cart
- [ ] Proceed to checkout
- [ ] Select district (verify delivery fee shows)
- [ ] Enter phone number (256 format)

### Test Mobile Money (Sandbox)
- [ ] Complete a test transaction with MTN MoMo
- [ ] Complete a test transaction with Airtel Money
- [ ] Verify transaction status updates

### Test SMS (Sandbox)
- [ ] Place a test order
- [ ] Verify order confirmation SMS received
- [ ] Check SMS log in admin

## Step 10: Set Up SSL (If You Have Domain)

### Configure DNS
- [ ] Log in to domain registrar
- [ ] Add A record pointing to Droplet IP
- [ ] Wait 15-30 minutes for DNS propagation
- [ ] Verify: `ping your-domain.com`

### Run SSL Setup
- [ ] `./setup-ssl.sh`
- [ ] Enter domain name: `____________________`
- [ ] Enter email: `____________________`
- [ ] Wait for certificate generation
- [ ] Verify HTTPS works: `https://your-domain.com`

### Update Environment for HTTPS
- [ ] Edit `.env.production`
- [ ] Change all `http://` to `https://`
- [ ] Change all `YOUR_DROPLET_IP` to `your-domain.com`
- [ ] Rebuild: `docker compose -f docker-compose.production.yml up -d --build`

## Step 11: Set Up Backups

### Manual Backup Test
- [ ] Run: `./backup.sh`
- [ ] Verify backup created in `backups/` folder

### Automatic Daily Backups
- [ ] `crontab -e`
- [ ] Add line: `0 2 * * * cd /opt/uganda-electronics && ./backup.sh >> /var/log/backup.log 2>&1`
- [ ] Save and exit

### Download Backup Locally (from your local machine)
- [ ] `scp root@YOUR_DROPLET_IP:/opt/uganda-electronics/backups/*.gz ./local-backups/`

## Step 12: Security Hardening

- [ ] Change SSH port (optional but recommended)
- [ ] Disable password authentication
- [ ] Set up fail2ban: `apt install -y fail2ban`
- [ ] Enable automatic security updates
- [ ] Set up UFW firewall properly

## Step 13: Monitoring

- [ ] Bookmark server IP/domain
- [ ] Set up uptime monitoring (optional - UptimeRobot, etc.)
- [ ] Save all credentials securely
- [ ] Document any customizations made

## Step 14: Go Live Preparation

### Switch to Production APIs
- [ ] Contact MTN Mobile Money for production credentials
- [ ] Contact Airtel Money for production credentials
- [ ] Upgrade Africa's Talking account
- [ ] Update `.env.production`:
  - [ ] `MTN_MOMO_ENVIRONMENT=production`
  - [ ] `AIRTEL_MONEY_ENVIRONMENT=production`
  - [ ] `AFRICAS_TALKING_ENVIRONMENT=production`
- [ ] Restart services

### Final Checks
- [ ] Upload all products with real data
- [ ] Set accurate prices in UGX
- [ ] Configure all Uganda districts delivery fees
- [ ] Add product images
- [ ] Write product descriptions
- [ ] Set up warranty periods
- [ ] Test full checkout flow end-to-end
- [ ] Test mobile money with small real transaction
- [ ] Verify SMS notifications work
- [ ] Test order tracking

### Marketing
- [ ] Add Google Analytics (optional)
- [ ] Set up Facebook Pixel (optional)
- [ ] Create social media accounts
- [ ] Prepare launch announcement

## Step 15: Launch! 🚀

- [ ] Announce on social media
- [ ] Share website with friends/family
- [ ] Monitor first orders closely
- [ ] Respond to customer questions quickly
- [ ] Keep monitoring logs for errors

## Post-Launch

### Daily Tasks
- [ ] Check for new orders
- [ ] Monitor system health
- [ ] Respond to customer inquiries

### Weekly Tasks
- [ ] Review sales reports
- [ ] Check error logs
- [ ] Download backups to local machine
- [ ] Monitor disk space usage

### Monthly Tasks
- [ ] System updates: `apt update && apt upgrade`
- [ ] Review costs and optimize
- [ ] Test backup restoration
- [ ] Update products/prices as needed

## Quick Reference

### Server IP Address
```
____________________
```

### Domain Name
```
____________________
```

### Admin Email
```
____________________
```

### Important URLs
- Storefront: `http://YOUR_SERVER_OR_DOMAIN`
- Dashboard: `http://YOUR_SERVER_OR_DOMAIN/dashboard/`
- GraphQL: `http://YOUR_SERVER_OR_DOMAIN/graphql/`

### Important Commands
```bash
# View logs
docker compose -f docker-compose.production.yml logs -f

# Restart services
docker compose -f docker-compose.production.yml restart

# Backup database
./backup.sh

# Update deployment
./deploy.sh
```

## Troubleshooting

If something goes wrong:

1. Check logs: `docker compose -f docker-compose.production.yml logs -f`
2. Check service status: `docker compose -f docker-compose.production.yml ps`
3. Check disk space: `df -h`
4. Check memory: `free -h`
5. Restart services: `docker compose -f docker-compose.production.yml restart`

## Support Resources

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment documentation
- [README.md](README.md) - Platform overview
- Saleor Docs: https://docs.saleor.io/
- DigitalOcean Community: https://www.digitalocean.com/community

---

**Good luck with your deployment! 🇺🇬 🚀**
