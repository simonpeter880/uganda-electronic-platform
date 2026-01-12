# Pre-Deployment Checklist

Complete this checklist **BEFORE** uploading to your server.

## ✅ Local Machine Preparation

### 1. Rename Directories (CRITICAL!)

**You MUST rename these directories before uploading:**

- [ ] Rename `saleor-platform` → `saleor-platform-uganda`
  ```bash
  cd /home/cymo/project-two
  mv saleor-platform saleor-platform-uganda
  ```

- [ ] Rename `storefront` → `storefront-uganda`
  ```bash
  cd /home/cymo/project-two
  mv storefront storefront-uganda
  ```

- [ ] Verify directory structure:
  ```bash
  ls -d */
  # Should see:
  # - saleor-platform-uganda/
  # - storefront-uganda/
  # - uganda-backend-code/
  ```

### 2. Verify Deployment Files Exist

- [ ] `docker-compose.production.yml` exists
- [ ] `deploy.sh` exists and is executable
- [ ] `setup-ssl.sh` exists and is executable
- [ ] `backup.sh` exists and is executable
- [ ] `.env.production.example` exists
- [ ] `nginx/nginx.conf` exists
- [ ] All `DEPLOYMENT_*.md` files exist

### 3. API Credentials Ready

Have these credentials prepared (can be sandbox for testing):

**MTN Mobile Money:**
- [ ] MTN_MOMO_API_KEY
- [ ] MTN_MOMO_SUBSCRIPTION_KEY
- [ ] MTN_MOMO_API_USER
- [ ] MTN_MOMO_API_SECRET
- [ ] Sign up at: https://momodeveloper.mtn.com/

**Airtel Money:**
- [ ] AIRTEL_MONEY_CLIENT_ID
- [ ] AIRTEL_MONEY_CLIENT_SECRET
- [ ] Contact: Airtel Money Uganda

**Africa's Talking SMS:**
- [ ] AFRICAS_TALKING_USERNAME
- [ ] AFRICAS_TALKING_API_KEY
- [ ] AFRICAS_TALKING_SENDER_ID
- [ ] Sign up at: https://africastalking.com/

> **Note**: You can start with sandbox/test credentials and switch to production later.

## ✅ DigitalOcean Account

### 4. DigitalOcean Setup

- [ ] DigitalOcean account created
- [ ] Payment method added
- [ ] SSH key added to DigitalOcean account
  - Your key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICW9BS01QjuUdh/QlSH2+RuQHi6Qls/sH5QFZHLwZ2sr`
  - Name it: `cymo-digitalocean-saleor`

### 5. Droplet Creation

- [ ] Droplet created
  - Region: London or Frankfurt
  - Image: Ubuntu 22.04 LTS
  - Size: $18/month (2GB RAM, 2 vCPUs)
  - Authentication: SSH key selected
  - Hostname: `uganda-electronics-prod`

- [ ] Droplet IP noted: `___________________`

### 6. Firewall Configuration

- [ ] Port 22 (SSH) allowed
- [ ] Port 80 (HTTP) allowed
- [ ] Port 443 (HTTPS) allowed

## ✅ Domain Name (Optional)

### 7. Domain Setup (If Using Custom Domain)

- [ ] Domain name purchased: `___________________`
- [ ] Domain registrar login credentials saved
- [ ] DNS A record ready to point to Droplet IP

> **Note**: You can deploy without a domain and add it later. SSL requires a domain.

## ✅ Server Initial Setup

### 8. SSH Connection

- [ ] Can connect via SSH: `ssh root@YOUR_DROPLET_IP`
- [ ] System updated: `apt update && apt upgrade -y`

### 9. Software Installation

- [ ] Docker installed: `curl -fsSL https://get.docker.com | sh`
- [ ] Docker Compose verified: `docker compose version`
- [ ] Git installed: `apt install -y git`
- [ ] UFW firewall configured

### 10. Project Directory

- [ ] Directory created: `/opt/uganda-electronics`
- [ ] Project files uploaded to server

## ✅ Configuration Files

### 11. Environment Variables

- [ ] `.env.production` file created on server
- [ ] `SERVER_IP` set to your Droplet IP
- [ ] `DB_PASSWORD` set (generated securely)
- [ ] `SECRET_KEY` set (generated securely)
- [ ] `NEXT_PUBLIC_SALEOR_API_URL` set
- [ ] `NEXT_PUBLIC_STOREFRONT_URL` set
- [ ] `DASHBOARD_URL` set
- [ ] Shop information filled in
- [ ] API credentials added (sandbox/production)

### 12. Scripts Executable

On server:
```bash
cd /opt/uganda-electronics
chmod +x *.sh
```

- [ ] `deploy.sh` is executable
- [ ] `setup-ssl.sh` is executable
- [ ] `backup.sh` is executable

## ✅ Pre-Deployment Test

### 13. Final Verification

- [ ] All directories renamed correctly
- [ ] All files uploaded to server
- [ ] `.env.production` configured
- [ ] Can access server via SSH
- [ ] Docker is running: `docker ps`
- [ ] Firewall is configured: `ufw status`

## 🚀 Ready to Deploy!

If all items above are checked, you're ready to deploy:

```bash
ssh root@YOUR_DROPLET_IP
cd /opt/uganda-electronics
./deploy.sh --first-time
```

## 📋 Quick Command Reference

### On Local Machine (Before Upload)

```bash
# Navigate to project
cd /home/cymo/project-two

# Rename directories (CRITICAL!)
mv saleor-platform saleor-platform-uganda
mv storefront storefront-uganda

# Create tarball for upload
tar -czf uganda-deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='storefront-uganda/.next' \
  --exclude='saleor-platform-uganda/venv' \
  .

# Upload to server
scp uganda-deploy.tar.gz root@YOUR_DROPLET_IP:/opt/uganda-electronics/
```

### On Server (Initial Setup)

```bash
# Connect
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install tools
apt install -y git nano curl wget htop ufw certbot

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create directory
mkdir -p /opt/uganda-electronics
cd /opt/uganda-electronics

# Extract uploaded files (if using tarball)
tar -xzf uganda-deploy.tar.gz
rm uganda-deploy.tar.gz

# Configure environment
cp .env.production.example .env.production
nano .env.production

# Make scripts executable
chmod +x *.sh

# Deploy
./deploy.sh --first-time
```

## ⚠️ Important Reminders

1. **MUST rename directories** from `saleor-platform`/`storefront` to `saleor-platform-uganda`/`storefront-uganda`
2. **NEVER commit** `.env.production` to git
3. **Generate secure passwords** for DB_PASSWORD and SECRET_KEY
4. **Save your admin credentials** when creating the superuser
5. **Start with sandbox/test APIs** before switching to production

## 🆘 Need Help?

- Detailed guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Server setup: [SERVER_SETUP.md](SERVER_SETUP.md)
- Step-by-step: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- Quick reference: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

## 📊 Deployment Timeline

- **Server setup**: 10-15 minutes
- **File upload**: 5-10 minutes (depending on connection)
- **Configuration**: 10 minutes
- **First deployment**: 10-15 minutes
- **Testing**: 10 minutes

**Total time**: ~1 hour for first deployment

---

**Once all items are checked, proceed with deployment! 🇺🇬 🚀**
