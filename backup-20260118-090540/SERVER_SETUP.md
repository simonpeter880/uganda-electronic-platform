# Server Setup Guide - DigitalOcean Droplet

This guide will help you set up your DigitalOcean Droplet from scratch for the Uganda Electronics Platform.

## Your SSH Key

Your public SSH key is already configured:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICW9BS01QjuUdh/QlSH2+RuQHi6Qls/sH5QFZHLwZ2sr cymo@digitalocean-saleor
```

## Step 1: Create DigitalOcean Droplet

### 1.1 Login to DigitalOcean
1. Go to https://cloud.digitalocean.com/
2. Login with your credentials

### 1.2 Add Your SSH Key (If Not Already Added)

1. Click on **Settings** → **Security** → **SSH Keys**
2. Click **Add SSH Key**
3. Paste your public key:
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICW9BS01QjuUdh/QlSH2+RuQHi6Qls/sH5QFZHLwZ2sr cymo@digitalocean-saleor
   ```
4. Name it: `cymo-digitalocean-saleor`
5. Click **Add SSH Key**

### 1.3 Create Droplet

1. Click **Create** → **Droplets**
2. **Choose Region**:
   - London (LON1) or Frankfurt (FRA1) - closest to Uganda
3. **Choose Image**:
   - Distribution: **Ubuntu 22.04 LTS (x64)**
4. **Choose Size**:
   - **Basic Plan**
   - **Regular Intel**
   - **$18/month** - 2 GB RAM / 2 vCPUs / 60 GB SSD / 3 TB transfer

   > Note: You can start with $12/month (1GB RAM) but 2GB is recommended for better performance

5. **Choose Authentication Method**:
   - Select **SSH keys**
   - Check your SSH key: `cymo-digitalocean-saleor`
6. **Finalize Details**:
   - Hostname: `uganda-electronics-prod`
   - Tags: `production`, `uganda`, `ecommerce`
   - Project: Select or create project
7. Click **Create Droplet**

### 1.4 Wait for Droplet Creation

- Wait 1-2 minutes for droplet to be created
- Note your Droplet's IP address (e.g., `165.227.123.45`)

## Step 2: Initial Server Connection

### 2.1 Connect via SSH

From your local machine:

```bash
# Replace with your actual Droplet IP
ssh root@YOUR_DROPLET_IP

# Example:
# ssh root@165.227.123.45
```

You should connect successfully without a password (using your SSH key).

### 2.2 First Login - Update System

Once connected, run:

```bash
# Update package list
apt update

# Upgrade all packages
apt upgrade -y

# This may take 2-5 minutes
```

## Step 3: Install Required Software

### 3.1 Install Docker

```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run the script
sh get-docker.sh

# Verify installation
docker --version
# Should show: Docker version 24.x.x or higher

# Test Docker
docker run hello-world
```

### 3.2 Verify Docker Compose

Docker Compose is included with Docker:

```bash
docker compose version
# Should show: Docker Compose version v2.x.x
```

### 3.3 Install Additional Tools

```bash
# Install git, nano, and other essentials
apt install -y git nano curl wget htop ufw

# Install certbot (for SSL later)
apt install -y certbot
```

## Step 4: Configure Firewall

### 4.1 Set Up UFW (Uncomplicated Firewall)

```bash
# Allow SSH (important - do this first!)
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

You should see:

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

## Step 5: Create Deployment Directory

```bash
# Create directory for your application
mkdir -p /opt/uganda-electronics

# Navigate to it
cd /opt/uganda-electronics
```

## Step 6: Upload Your Project Files

You have several options to upload your project.

### Option A: Using Git (Recommended if you have GitHub repo)

If you've pushed your code to GitHub:

```bash
cd /opt/uganda-electronics

# Clone your repositories
git clone YOUR_GITHUB_USERNAME/saleor-platform-uganda.git
git clone YOUR_GITHUB_USERNAME/storefront-uganda.git

# Or clone the entire project if it's in one repo
git clone YOUR_GITHUB_USERNAME/uganda-electronics-platform.git .
```

### Option B: Using SCP from Your Local Machine

On your **local machine** (not the server):

```bash
# Navigate to your project directory
cd /home/cymo/project-two

# First, rename directories (IMPORTANT!)
mv saleor-platform saleor-platform-uganda
mv storefront storefront-uganda

# Create tarball (excluding large directories)
tar -czf uganda-deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='storefront-uganda/.next' \
  --exclude='saleor-platform-uganda/venv' \
  --exclude='backups' \
  .

# Upload to server (replace YOUR_DROPLET_IP)
scp uganda-deploy.tar.gz root@YOUR_DROPLET_IP:/opt/uganda-electronics/

# Then on the server, extract:
cd /opt/uganda-electronics
tar -xzf uganda-deploy.tar.gz
rm uganda-deploy.tar.gz
```

### Option C: Using rsync from Your Local Machine

On your **local machine**:

```bash
cd /home/cymo/project-two

# First, rename directories (IMPORTANT!)
mv saleor-platform saleor-platform-uganda
mv storefront storefront-uganda

# Sync to server (replace YOUR_DROPLET_IP)
rsync -avz --progress \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='storefront-uganda/.next' \
  --exclude='saleor-platform-uganda/venv' \
  --exclude='backups' \
  ./ root@YOUR_DROPLET_IP:/opt/uganda-electronics/
```

## Step 7: Verify File Upload

On the **server**:

```bash
cd /opt/uganda-electronics
ls -la

# You should see:
# - saleor-platform-uganda/
# - storefront-uganda/
# - uganda-backend-code/
# - docker-compose.production.yml
# - deploy.sh
# - setup-ssl.sh
# - backup.sh
# - DEPLOYMENT_*.md
```

## Step 8: Configure Environment Variables

### 8.1 Create Production Environment File

```bash
cd /opt/uganda-electronics

# Copy the example file
cp .env.production.example .env.production

# Edit the file
nano .env.production
```

### 8.2 Essential Variables to Set

Update these critical variables in `.env.production`:

```bash
# Server IP (your actual Droplet IP)
SERVER_IP=YOUR_DROPLET_IP_HERE

# Database password (generate a secure one)
DB_PASSWORD=your_secure_db_password_here

# Django secret key (generate a secure one)
SECRET_KEY=your_secure_secret_key_here

# API URLs (use your Droplet IP)
NEXT_PUBLIC_SALEOR_API_URL=http://YOUR_DROPLET_IP/graphql/
NEXT_PUBLIC_STOREFRONT_URL=http://YOUR_DROPLET_IP
DASHBOARD_URL=http://YOUR_DROPLET_IP/dashboard/

# Shop Information
SHOP_NAME=Your Electronics Store
SHOP_PHONE=256700123456
SHOP_EMAIL=info@yourstore.ug

# Payment providers (use sandbox for now)
MTN_MOMO_ENVIRONMENT=sandbox
AIRTEL_MONEY_ENVIRONMENT=uat
AFRICAS_TALKING_ENVIRONMENT=sandbox
```

### 8.3 Generate Secure Passwords

On the server, generate secure passwords:

```bash
# Generate database password
openssl rand -base64 32

# Generate Django secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy these values into your `.env.production` file.

Save and exit (Ctrl+X, Y, Enter).

## Step 9: Make Scripts Executable

```bash
cd /opt/uganda-electronics

chmod +x deploy.sh
chmod +x setup-ssl.sh
chmod +x backup.sh
```

## Step 10: Deploy!

### 10.1 Run First Deployment

```bash
cd /opt/uganda-electronics

# Run initial deployment
./deploy.sh --first-time
```

This will:
- Pull Docker images (5-10 minutes first time)
- Build storefront
- Start all services
- Run database migrations
- Prompt you to create admin account
- Collect static files

### 10.2 Create Admin Account

When prompted, enter:
- **Email**: your_admin@email.com
- **Password**: (choose a strong password and save it!)

### 10.3 Wait for Services

The deployment will take 5-10 minutes. Monitor progress in the terminal.

## Step 11: Verify Deployment

### 11.1 Check Service Status

```bash
docker compose -f docker-compose.production.yml ps
```

All services should show "Up" status.

### 11.2 Check Logs

```bash
# View all logs
docker compose -f docker-compose.production.yml logs -f

# Press Ctrl+C to stop viewing
```

### 11.3 Access Your Site

Open your browser and visit:

- **Storefront**: `http://YOUR_DROPLET_IP`
- **Admin Dashboard**: `http://YOUR_DROPLET_IP/dashboard/`
- **GraphQL API**: `http://YOUR_DROPLET_IP/graphql/`

You should see your site running! 🎉

## Step 12: Run Uganda Migrations

```bash
cd /opt/uganda-electronics/saleor-platform-uganda/migrations/uganda-platform

# Make script executable
chmod +x run_migrations.sh

# Run migrations
./run_migrations.sh
```

This will set up:
- 135 Uganda districts with delivery fees
- Mobile Money payment tables
- SMS notification system
- Electronics features (IMEI, warranty tracking)
- Installment payment system

## Quick Reference Card

Save these details for future reference:

```
===========================================
SERVER INFORMATION
===========================================
Droplet IP:        ____________________
SSH User:          root
SSH Key:           cymo@digitalocean-saleor

===========================================
ACCESS URLS
===========================================
Storefront:        http://YOUR_IP
Admin Dashboard:   http://YOUR_IP/dashboard/
GraphQL API:       http://YOUR_IP/graphql/

===========================================
ADMIN CREDENTIALS
===========================================
Email:             ____________________
Password:          ____________________

===========================================
IMPORTANT COMMANDS
===========================================
SSH Connect:       ssh root@YOUR_IP
View Logs:         docker compose -f docker-compose.production.yml logs -f
Restart Services:  docker compose -f docker-compose.production.yml restart
Backup Database:   ./backup.sh
Deploy Updates:    ./deploy.sh

===========================================
FILES LOCATION
===========================================
Project:           /opt/uganda-electronics
Environment:       /opt/uganda-electronics/.env.production
Nginx Config:      /opt/uganda-electronics/nginx/nginx.conf
Backups:           /opt/uganda-electronics/backups/
```

## Next Steps

1. ✅ Server is running with HTTP
2. Configure your shop in the admin dashboard
3. Add products and categories
4. Test Mobile Money integration (sandbox)
5. Test SMS notifications (sandbox)
6. (Optional) Set up SSL with domain name:
   ```bash
   ./setup-ssl.sh
   ```
7. Set up automated backups:
   ```bash
   crontab -e
   # Add: 0 2 * * * cd /opt/uganda-electronics && ./backup.sh >> /var/log/backup.log 2>&1
   ```

## Troubleshooting

### Can't Connect via SSH

```bash
# Verify your SSH key is correct
cat ~/.ssh/id_ed25519.pub

# Try connecting with verbose output
ssh -v root@YOUR_DROPLET_IP
```

### Services Won't Start

```bash
# Check Docker status
systemctl status docker

# Check available memory
free -h

# Check disk space
df -h
```

### Out of Memory

If you have 1GB RAM and services keep crashing:
- Upgrade to 2GB Droplet ($18/month)
- Or add swap space (temporary solution):
  ```bash
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  ```

## Security Checklist

- [x] SSH key authentication enabled
- [ ] Strong password in `.env.production`
- [ ] Firewall configured (UFW)
- [ ] Regular backups enabled
- [ ] SSL certificate installed (optional but recommended)
- [ ] System updates enabled

## Support

- Full guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- Quick reference: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

---

**Your server is ready! Happy deploying! 🇺🇬 🚀**
