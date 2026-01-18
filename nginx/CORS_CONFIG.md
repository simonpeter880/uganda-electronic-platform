# Nginx Security & Configuration Guide

## Table of Contents
1. [CORS Configuration](#cors-configuration)
2. [Domain Setup](#domain-setup)
3. [WebSocket Support](#websocket-support)
4. [SSL/HTTPS Setup](#ssl-https-setup)
5. [Security Headers](#security-headers)

---

## CORS Configuration

### Security Notice

The nginx configuration uses **whitelisted origins** for CORS, not the wildcard `*`. This prevents unauthorized domains from accessing your GraphQL API with user credentials.

## How to Configure Your Domains

Edit `/nginx/nginx.conf` and update the `map $http_origin $cors_origin` block (around line 43) with your actual domains:

```nginx
map $http_origin $cors_origin {
    default "";
    # Replace these with your actual production domains
    "~^https?://(www\.)?yourdomain\.com$" $http_origin;
    "~^https?://dashboard\.yourdomain\.com$" $http_origin;

    # Development origins (remove these in production)
    "~^https?://localhost:3000$" $http_origin;
    "~^https?://localhost:9000$" $http_origin;
}
```

## Examples

### Single Domain Setup
If your storefront and dashboard are on the same domain:
```nginx
"~^https?://(www\.)?ugandaelectronics\.com$" $http_origin;
```

### Multi-Domain Setup
If you have separate domains:
```nginx
"~^https?://(www\.)?ugandaelectronics\.com$" $http_origin;       # Storefront
"~^https?://admin\.ugandaelectronics\.com$" $http_origin;         # Dashboard
```

### IP Address Setup (for testing)
```nginx
"~^https?://192\.168\.1\.100$" $http_origin;
"~^https?://your-droplet-ip$" $http_origin;
```

## After Making Changes

1. Test nginx config: `docker compose -f docker-compose.production.yml exec nginx nginx -t`
2. Reload nginx: `docker compose -f docker-compose.production.yml exec nginx nginx -s reload`

## Why This Matters

- **With `*`**: Any website can call your GraphQL API with stolen tokens
- **With whitelist**: Only your storefront and dashboard can make authenticated requests
- **Access-Control-Allow-Credentials: true**: Allows cookies/auth headers, but requires specific origins (not `*`)

## Troubleshooting CORS

If you see CORS errors in browser console:

1. Check that your origin matches exactly (http vs https, www vs non-www)
2. Verify the regex pattern includes your domain
3. Check nginx error logs: `docker compose -f docker-compose.production.yml logs nginx`

---

## Domain Setup

### Production Domain Configuration

Replace `server_name _;` in the HTTP server block (line ~80) with your actual domain:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    # ...
}
```

When enabling HTTPS, also update the SSL server block with the same domains.

---

## WebSocket Support

The configuration includes WebSocket support for GraphQL subscriptions (real-time updates):

```nginx
# In http {} block - already configured
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

# In /graphql/ location - already configured
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $connection_upgrade;
```

This allows Saleor to push real-time updates to clients (stock changes, order updates, etc.).

---

## SSL HTTPS Setup

### Step 1: Obtain SSL Certificate

Use Let's Encrypt (free) or your SSL provider:

```bash
# Install certbot
sudo apt install certbot

# Get certificate (replace with your domain)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

### Step 2: Copy Certificates to nginx/ssl/

```bash
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

### Step 3: Enable HTTPS in nginx.conf

Uncomment the HTTPS server block (around line 225) and update:
- `server_name` with your domain
- Certificate paths if needed

### Step 4: Enable HTTP to HTTPS Redirect

Uncomment the redirect server block (around line 257).

### Step 5: Test and Reload

```bash
# Test configuration
docker compose -f docker-compose.production.yml exec nginx nginx -t

# Reload nginx
docker compose -f docker-compose.production.yml exec nginx nginx -s reload
```

### HSTS Warning

**IMPORTANT**: Only enable HSTS (`Strict-Transport-Security` header) after confirming HTTPS works:
- Once enabled, browsers will refuse HTTP for the duration (1 year)
- Cannot be easily undone
- Test thoroughly before enabling

---

## Security Headers

The configuration includes modern security headers:

### Current Headers

- `X-Frame-Options: SAMEORIGIN` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer info
- `Permissions-Policy` - Restricts geolocation, microphone, camera

### Removed

- `X-XSS-Protection` - Obsolete in modern browsers, can cause issues

### Future Enhancement: Content Security Policy

Consider adding CSP once your app is stable:

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

**Warning**: CSP can break functionality if misconfigured. Test thoroughly in development first.

---

## Rate Limiting

Three rate limit zones are configured:

- `graphql_limit`: 30 req/s for GraphQL API
- `api_limit`: 10 req/s for REST API endpoints
- `login_limit`: 5 req/s for authentication (not yet applied)

### Adjusting Rates

Edit the `limit_req_zone` directives (around line 38):

```nginx
limit_req_zone $binary_remote_addr zone=graphql_limit:10m rate=30r/s;
```

Change `rate=30r/s` to your desired rate.

---

## Testing Configuration

Always test nginx config before reloading in production:

```bash
# Test syntax
docker compose -f docker-compose.production.yml exec nginx nginx -t

# If OK, reload
docker compose -f docker-compose.production.yml exec nginx nginx -s reload

# Watch logs for errors
docker compose -f docker-compose.production.yml logs -f nginx
```
