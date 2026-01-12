#!/bin/bash

# ============================================
# SSL Setup Script with Let's Encrypt
# ============================================
# This script sets up HTTPS with free SSL certificates from Let's Encrypt
# Run this AFTER your initial deployment is complete
# Only works if you have a domain name pointing to your server

set -e

echo "🔒 Setting up SSL with Let's Encrypt..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================
# Check Prerequisites
# ============================================
print_status "Checking prerequisites..."

# Check if .env.production exists
if [ ! -f .env.production ]; then
    print_error ".env.production not found!"
    exit 1
fi

# Load environment
set -a
source .env.production
set +a

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_status "Installing certbot..."

    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y certbot
    else
        print_error "Cannot install certbot automatically. Please install manually."
        exit 1
    fi

    print_success "Certbot installed"
fi

# ============================================
# Get Domain Name
# ============================================
echo ""
echo "============================================"
echo "  SSL Certificate Setup"
echo "============================================"
echo ""
echo "IMPORTANT: Before proceeding, make sure:"
echo "1. You have a domain name (e.g., myshop.ug)"
echo "2. Your domain's DNS A record points to: ${SERVER_IP}"
echo "3. Port 80 is open in your firewall"
echo ""

read -p "Enter your domain name (e.g., myshop.ug): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    print_error "Domain name is required!"
    exit 1
fi

# Ask for email
read -p "Enter your email address (for SSL certificate notifications): " EMAIL

if [ -z "$EMAIL" ]; then
    print_error "Email is required!"
    exit 1
fi

print_status "Using domain: $DOMAIN_NAME"
print_status "Email: $EMAIL"

# ============================================
# Stop nginx temporarily
# ============================================
print_status "Stopping nginx temporarily..."

docker compose -f docker-compose.production.yml stop nginx

# ============================================
# Obtain SSL Certificate
# ============================================
print_status "Obtaining SSL certificate from Let's Encrypt..."

# Use certbot standalone mode
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN_NAME" \
    --preferred-challenges http

if [ $? -ne 0 ]; then
    print_error "Failed to obtain SSL certificate!"
    print_error "Please check:"
    print_error "1. Domain DNS is properly configured"
    print_error "2. Port 80 is accessible from the internet"
    print_error "3. No other service is using port 80"

    # Restart nginx
    docker compose -f docker-compose.production.yml start nginx
    exit 1
fi

print_success "SSL certificate obtained successfully!"

# ============================================
# Copy Certificates
# ============================================
print_status "Copying certificates to nginx directory..."

sudo cp /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem nginx/ssl/

# Set proper permissions
sudo chown $USER:$USER nginx/ssl/*.pem
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem

print_success "Certificates copied"

# ============================================
# Update Nginx Configuration
# ============================================
print_status "Updating nginx configuration for HTTPS..."

cat > nginx/nginx-ssl.conf << EOF
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=graphql_limit:10m rate=30r/s;

    # Upstream servers
    upstream saleor_api {
        server api:8000;
    }

    upstream saleor_dashboard {
        server dashboard:80;
    }

    upstream storefront {
        server storefront:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name $DOMAIN_NAME;

        # Allow Let's Encrypt challenges
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://\$server_name\$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN_NAME;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Storefront (Main website)
        location / {
            proxy_pass http://storefront;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # GraphQL API
        location /graphql/ {
            limit_req zone=graphql_limit burst=20 nodelay;

            proxy_pass http://saleor_api;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;

            # CORS headers
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

            if (\$request_method = 'OPTIONS') {
                add_header 'Access-Control-Max-Age' 1728000;
                add_header 'Content-Type' 'text/plain; charset=utf-8';
                add_header 'Content-Length' 0;
                return 204;
            }
        }

        # Saleor API endpoints
        location /api/ {
            limit_req zone=api_limit burst=10 nodelay;

            proxy_pass http://saleor_api;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Admin Dashboard
        location /dashboard/ {
            proxy_pass http://saleor_dashboard/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Media files
        location /media/ {
            proxy_pass http://saleor_api/media/;
            proxy_set_header Host \$host;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Static files
        location /static/ {
            proxy_pass http://saleor_api/static/;
            proxy_set_header Host \$host;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health/ {
            proxy_pass http://saleor_api/health/;
            access_log off;
        }

        # Next.js static files
        location /_next/static/ {
            proxy_pass http://storefront;
            expires 365d;
            add_header Cache-Control "public, immutable";
        }

        # Block access to sensitive files
        location ~ /\\. {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
EOF

# Backup old config
cp nginx/nginx.conf nginx/nginx.conf.backup

# Replace with SSL config
cp nginx/nginx-ssl.conf nginx/nginx.conf

print_success "Nginx configuration updated"

# ============================================
# Update Environment Variables
# ============================================
print_status "Updating environment variables for HTTPS..."

# Update .env.production
sed -i "s|http://${SERVER_IP}|https://${DOMAIN_NAME}|g" .env.production
sed -i "s|http://${DOMAIN_NAME}|https://${DOMAIN_NAME}|g" .env.production

print_success "Environment variables updated"

# ============================================
# Restart Services
# ============================================
print_status "Restarting services with HTTPS enabled..."

docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml up -d --build

print_success "Services restarted"

# ============================================
# Set Up Auto-Renewal
# ============================================
print_status "Setting up automatic certificate renewal..."

# Create renewal script
cat > /tmp/renew-cert.sh << EOF
#!/bin/bash
# SSL Certificate Renewal Script

# Stop nginx
cd $(pwd)
docker compose -f docker-compose.production.yml stop nginx

# Renew certificate
certbot renew --standalone

# Copy new certificates
cp /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem nginx/ssl/
chown $USER:$USER nginx/ssl/*.pem
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem

# Restart nginx
docker compose -f docker-compose.production.yml start nginx
EOF

sudo mv /tmp/renew-cert.sh /etc/cron.monthly/renew-cert
sudo chmod +x /etc/cron.monthly/renew-cert

print_success "Auto-renewal configured"

# ============================================
# Display Results
# ============================================
echo ""
print_success "🎉 SSL setup completed successfully!"
echo ""
echo "============================================"
echo "  Your Site is Now Secured with HTTPS"
echo "============================================"
echo ""
echo "Storefront:       https://${DOMAIN_NAME}"
echo "Admin Dashboard:  https://${DOMAIN_NAME}/dashboard/"
echo "GraphQL API:      https://${DOMAIN_NAME}/graphql/"
echo ""
echo "SSL Certificate:"
echo "  - Issued by: Let's Encrypt"
echo "  - Valid for: 90 days"
echo "  - Auto-renewal: Enabled (monthly check)"
echo ""
print_warning "IMPORTANT: Update your .env.production file to use HTTPS URLs"
print_warning "Then rebuild the storefront:"
print_warning "  docker compose -f docker-compose.production.yml up -d --build storefront"
echo ""
print_success "SSL setup complete! 🔒"
