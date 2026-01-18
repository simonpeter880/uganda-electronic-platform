# Deployment Guide - Uganda Electronics Platform to DigitalOcean

This guide walks you through deploying your Uganda Electronics Platform to a DigitalOcean Droplet.

## Prerequisites

- A DigitalOcean account
- A Droplet with Ubuntu 22.04 LTS (minimum 2GB RAM, 2 vCPUs, 50GB disk)
- SSH access to your Droplet
- (Optional) A domain name pointing to your Droplet's IP address

## Overview

Your platform consists of:
- **Saleor Backend** - GraphQL API and admin dashboard
- **PostgreSQL** - Database
- **Redis/Valkey** - Cache and message broker
- **Next.js Storefront** - Customer-facing website
- **Nginx** - Reverse proxy and load balancer

All services run in Docker containers managed by Docker Compose.

## Step 1: Prepare Your DigitalOcean Droplet

### 1.1 Create a Droplet

1. Log in to DigitalOcean
2. Click "Create" → "Droplets"
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($18/month - 2GB RAM, 2 vCPUs, 60GB SSD)
   - **Datacenter**: Choose closest to Uganda (e.g., London or Frankfurt)
   - **Authentication**: SSH key (recommended) or password
   - **Hostname**: uganda-electronics-prod

### 1.2 Configure Firewall

Allow the following ports:
- **22** (SSH)
- **80** (HTTP)
- **443** (HTTPS)

You can do this in the DigitalOcean Networking section or via UFW:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 1.3 Connect to Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

## Step 2: Install Required Software

### 2.1 Update System

```bash
apt update && apt upgrade -y
```

### 2.2 Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2.3 Install Docker Compose

Docker Compose should be included with Docker. Verify:

```bash
docker compose version
```

### 2.4 Install Git

```bash
apt install -y git
```

## Step 3: Upload Your Project

### Option A: Using Git (Recommended)

If your code is in a Git repository:

```bash
cd /opt
git clone YOUR_REPOSITORY_URL uganda-electronics
cd uganda-electronics
```

### Option B: Using SCP

From your local machine:

```bash
# Create a tarball of your project
tar -czf project.tar.gz /home/cymo/project-two

# Upload to server
scp project.tar.gz root@YOUR_DROPLET_IP:/opt/

# On the server
cd /opt
tar -xzf project.tar.gz
mv project-two uganda-electronics
cd uganda-electronics
```

### Option C: Using rsync

From your local machine:

```bash
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /home/cymo/project-two/ \
  root@YOUR_DROPLET_IP:/opt/uganda-electronics/
```

## Step 4: Configure Environment Variables

### 4.1 Create Production Environment File

```bash
cd /opt/uganda-electronics
cp .env.production.example .env.production
```

### 4.2 Edit the Environment File

```bash
nano .env.production
```

**Critical settings to update:**

```bash
# Server Configuration
SERVER_IP=YOUR_DROPLET_IP_HERE

# Example: SERVER_IP=165.227.123.45
ALLOWED_HOSTS=YOUR_DROPLET_IP_HERE,localhost,127.0.0.1,api
ALLOWED_CLIENT_HOSTS=YOUR_DROPLET_IP_HERE,localhost,127.0.0.1

# Database - Generate a strong password
DB_PASSWORD=GENERATE_STRONG_PASSWORD_HERE

# Django Secret Key - Generate a random 50+ character string
SECRET_KEY=GENERATE_RANDOM_SECRET_KEY_50_CHARS_MIN

# API URLs
NEXT_PUBLIC_SALEOR_API_URL=http://YOUR_DROPLET_IP/graphql/
NEXT_PUBLIC_STOREFRONT_URL=http://YOUR_DROPLET_IP
DASHBOARD_URL=http://YOUR_DROPLET_IP/dashboard/

# Shop Information
SHOP_NAME=Your Electronics Store Name
SHOP_PHONE=256700123456
SHOP_WHATSAPP=256700123456
SHOP_EMAIL=info@yourstore.ug
```

**To generate secure passwords/keys:**

```bash
# Generate DB password
openssl rand -base64 32

# Generate Django secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4.3 Add Mobile Money Credentials

When you're ready to go live, add your payment provider credentials:

```bash
# MTN Mobile Money
MTN_MOMO_API_KEY=your_key
MTN_MOMO_SUBSCRIPTION_KEY=your_key
MTN_MOMO_API_USER=your_uuid
MTN_MOMO_API_SECRET=your_secret
MTN_MOMO_ENVIRONMENT=sandbox  # Change to 'production' when ready

# Airtel Money
AIRTEL_MONEY_CLIENT_ID=your_id
AIRTEL_MONEY_CLIENT_SECRET=your_secret
AIRTEL_MONEY_ENVIRONMENT=uat  # Change to 'production' when ready

# Africa's Talking SMS
AFRICAS_TALKING_USERNAME=your_username
AFRICAS_TALKING_API_KEY=your_key
AFRICAS_TALKING_SENDER_ID=YOURSHOP
AFRICAS_TALKING_ENVIRONMENT=sandbox  # Change to 'production' when ready
```

Save and close the file (Ctrl+X, Y, Enter).

## Step 5: Deploy the Application

### 5.1 Run Initial Deployment

For the first deployment:

```bash
./deploy.sh --first-time
```

This script will:
1. Check system requirements
2. Pull Docker images
3. Build the storefront
4. Start all services
5. Run database migrations
6. Prompt you to create an admin account
7. Collect static files

**When prompted, create your admin account:**
- Email: your_admin@email.com
- Password: (choose a strong password)

### 5.2 Wait for Services to Start

The initial deployment takes 5-10 minutes. Monitor progress:

```bash
docker compose -f docker-compose.production.yml logs -f
```

Press Ctrl+C to stop viewing logs.

### 5.3 Check Service Status

```bash
docker compose -f docker-compose.production.yml ps
```

All services should show "Up" status.

## Step 6: Run Uganda Platform Migrations

Set up Uganda-specific features (districts, payment methods, etc.):

```bash
cd saleor-platform-uganda/migrations/uganda-platform

# Make the script executable
chmod +x run_migrations.sh

# Run migrations
./run_migrations.sh
```

## Step 7: Access Your Platform

### 7.1 Test Access

Open your browser and visit:

- **Storefront**: `http://YOUR_DROPLET_IP`
- **Admin Dashboard**: `http://YOUR_DROPLET_IP/dashboard/`
- **GraphQL API**: `http://YOUR_DROPLET_IP/graphql/`

### 7.2 Login to Admin Dashboard

1. Go to `http://YOUR_DROPLET_IP/dashboard/`
2. Login with the admin credentials you created
3. Configure your shop settings

## Step 8: Configure Your Shop

### 8.1 Set Up Shop Information

In the admin dashboard:

1. Go to **Configuration** → **Site Settings**
2. Update shop name and contact information
3. Set up your Uganda address

### 8.2 Create Product Categories

1. Go to **Catalog** → **Categories**
2. Create categories like:
   - Mobile Phones
   - Laptops
   - Tablets
   - Accessories
   - etc.

### 8.3 Add Your First Products

1. Go to **Catalog** → **Products**
2. Click "Create Product"
3. Add product details:
   - Name (e.g., "iPhone 14 Pro 128GB")
   - Category
   - Price (in UGX)
   - Description
   - Images
   - IMEI/Serial number tracking
   - Warranty period

### 8.4 Configure Payment Methods

1. Go to **Configuration** → **Payment Methods**
2. Set up:
   - MTN Mobile Money
   - Airtel Money
   - Cash on Delivery
   - Cash in Store

### 8.5 Set Up Uganda Districts

Districts should already be loaded from migrations. Verify:

1. Check database:
```bash
docker compose -f docker-compose.production.yml exec -T db psql -U saleor -d saleor -c "SELECT COUNT(*) FROM uganda_district;"
```

You should see 135 districts.

## Step 9: Set Up SSL (HTTPS)

**Important:** This step requires a domain name!

### 9.1 Point Your Domain to the Droplet

In your domain registrar (e.g., Namecheap, GoDaddy):

1. Add an A record:
   - Host: @ (or your-shop)
   - Value: YOUR_DROPLET_IP
   - TTL: 300 (5 minutes)

2. Wait 5-30 minutes for DNS propagation

3. Verify DNS is working:
```bash
ping your-domain.com
```

### 9.2 Run SSL Setup Script

```bash
./setup-ssl.sh
```

Follow the prompts:
- Enter your domain name
- Enter your email address

The script will:
1. Install certbot
2. Obtain an SSL certificate from Let's Encrypt
3. Update nginx configuration for HTTPS
4. Set up automatic certificate renewal
5. Restart all services

### 9.3 Verify HTTPS Works

Visit `https://your-domain.com` in your browser. You should see a secure padlock icon.

## Step 10: Set Up Backups

### 10.1 Manual Backup

Create a backup anytime:

```bash
./backup.sh
```

Backups are stored in `/opt/uganda-electronics/backups/`

### 10.2 Automatic Daily Backups

Set up a cron job:

```bash
crontab -e
```

Add this line to run backups daily at 2 AM:

```bash
0 2 * * * cd /opt/uganda-electronics && ./backup.sh >> /var/log/backup.log 2>&1
```

### 10.3 Download Backups to Local Machine

From your local machine:

```bash
scp root@YOUR_DROPLET_IP:/opt/uganda-electronics/backups/*.gz ./local-backups/
```

### 10.4 Restore from Backup

If you need to restore:

```bash
# Stop services
docker compose -f docker-compose.production.yml down

# Start only database
docker compose -f docker-compose.production.yml up -d db

# Restore backup
gunzip -c backups/saleor_backup_TIMESTAMP.sql.gz | \
  docker compose -f docker-compose.production.yml exec -T db psql -U saleor -d saleor

# Start all services
docker compose -f docker-compose.production.yml up -d
```

## Step 11: Monitoring and Maintenance

### 11.1 View Logs

```bash
# All services
docker compose -f docker-compose.production.yml logs -f

# Specific service
docker compose -f docker-compose.production.yml logs -f api
docker compose -f docker-compose.production.yml logs -f storefront
docker compose -f docker-compose.production.yml logs -f nginx
```

### 11.2 Restart Services

```bash
# Restart all
docker compose -f docker-compose.production.yml restart

# Restart specific service
docker compose -f docker-compose.production.yml restart api
```

### 11.3 Check Resource Usage

```bash
# CPU and memory
htop

# Disk usage
df -h

# Docker container stats
docker stats
```

### 11.4 Update Application

When you make changes to your code:

```bash
# Pull latest code (if using git)
git pull

# Rebuild and restart
docker compose -f docker-compose.production.yml up -d --build

# Run any new migrations
docker compose -f docker-compose.production.yml exec api python manage.py migrate
```

## Common Issues and Solutions

### Issue: Services Won't Start

**Check logs:**
```bash
docker compose -f docker-compose.production.yml logs
```

**Common causes:**
- Insufficient memory (upgrade to 4GB Droplet)
- Port conflicts (check if something else uses port 80)
- Environment variables missing

### Issue: Can't Access Website

**Check:**
1. Firewall allows port 80/443
2. Nginx is running: `docker compose -f docker-compose.production.yml ps nginx`
3. DNS is configured correctly (if using domain)

### Issue: Database Connection Errors

**Check database is running:**
```bash
docker compose -f docker-compose.production.yml ps db
```

**Check database logs:**
```bash
docker compose -f docker-compose.production.yml logs db
```

### Issue: Out of Disk Space

**Check disk usage:**
```bash
df -h
```

**Clean up Docker:**
```bash
docker system prune -a
```

**Clean up old logs:**
```bash
cd nginx/logs
rm *.log.1 *.log.2
```

## Security Best Practices

### 1. Change Default SSH Port

Edit `/etc/ssh/sshd_config`:
```bash
Port 2222  # Change from 22
```

Restart SSH:
```bash
systemctl restart sshd
```

Update firewall:
```bash
ufw allow 2222/tcp
ufw delete allow 22/tcp
```

### 2. Set Up SSH Key Authentication

Disable password authentication in `/etc/ssh/sshd_config`:
```bash
PasswordAuthentication no
```

### 3. Keep System Updated

```bash
apt update && apt upgrade -y
```

Set up automatic updates:
```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 4. Monitor Failed Login Attempts

Install fail2ban:
```bash
apt install -y fail2ban
systemctl enable fail2ban
```

### 5. Regular Backups

- Daily automated backups (set up in Step 10)
- Weekly download backups to local machine
- Monthly test backup restoration

## Performance Optimization

### 1. Enable Redis Caching

Already configured in the production docker-compose!

### 2. Use DigitalOcean Spaces for Media

Edit `.env.production`:
```bash
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com
```

### 3. Enable CDN

Use DigitalOcean's CDN for static files and images.

### 4. Upgrade Droplet If Needed

If experiencing slow performance:
- Upgrade to 4GB RAM ($36/month)
- Add monitoring to identify bottlenecks

## Scaling Considerations

When your business grows:

1. **Separate Database**: Move PostgreSQL to managed DigitalOcean Database
2. **Load Balancer**: Add multiple API servers behind a load balancer
3. **CDN**: Use CDN for static assets and images
4. **Monitoring**: Add Sentry for error tracking
5. **Analytics**: Add Plausible or Google Analytics

## Cost Estimates

### Monthly Operating Costs

- **Droplet (2GB)**: $18/month
- **Domain**: $12/year (~$1/month)
- **SSL Certificate**: Free (Let's Encrypt)
- **Africa's Talking SMS**: ~$50-100/month (1000-2000 SMS)
- **MTN/Airtel transaction fees**: 1-2% of transactions
- **Backups/Spaces**: $5/month (optional)

**Total**: ~$75-125/month

### Recommended Starting Setup

1. Start with $18 Droplet (2GB RAM)
2. Monitor performance for first month
3. Upgrade to $36 Droplet (4GB RAM) if needed
4. Add managed database ($15/month) when scaling

## Getting Help

### Resources

- **Saleor Docs**: https://docs.saleor.io/
- **DigitalOcean Docs**: https://docs.digitalocean.com/
- **Docker Docs**: https://docs.docker.com/
- **Next.js Docs**: https://nextjs.org/docs

### Useful Commands Reference

```bash
# Deploy/Update
./deploy.sh

# Setup SSL
./setup-ssl.sh

# Backup database
./backup.sh

# View logs
docker compose -f docker-compose.production.yml logs -f [service]

# Restart services
docker compose -f docker-compose.production.yml restart

# Stop everything
docker compose -f docker-compose.production.yml down

# Start everything
docker compose -f docker-compose.production.yml up -d

# Access database
docker compose -f docker-compose.production.yml exec db psql -U saleor -d saleor

# Access API shell
docker compose -f docker-compose.production.yml exec api python manage.py shell

# Create superuser
docker compose -f docker-compose.production.yml exec api python manage.py createsuperuser
```

## Next Steps After Deployment

1. ✅ Configure shop information
2. ✅ Add product categories
3. ✅ Upload your products with images
4. ✅ Test Mobile Money integration (sandbox mode)
5. ✅ Test SMS notifications (sandbox mode)
6. ✅ Configure delivery fees for districts
7. ✅ Test complete checkout flow
8. ✅ Set up Google Analytics (optional)
9. ✅ Switch payment providers to production mode
10. ✅ Launch and start selling! 🎉

## Congratulations! 🇺🇬

Your Uganda Electronics Platform is now live and ready to serve customers!

**Remember:**
- Monitor your logs regularly
- Keep daily backups
- Update your system monthly
- Test payment flows frequently
- Keep your API credentials secure

Good luck with your electronics business in Uganda! 🚀
