#!/bin/sh
set -e

# Default values
DEPLOYMENT_MODE=${DEPLOYMENT_MODE:-development}
DOMAIN_NAME=${DOMAIN_NAME:-localhost}

echo "=== Nginx Configuration ==="
echo "Deployment Mode: $DEPLOYMENT_MODE"
echo "Domain Name: $DOMAIN_NAME"
echo "=========================="

# Set server name
export NGINX_SERVER_NAME=$DOMAIN_NAME

# SSL certificate paths
SSL_DIR="/etc/nginx/ssl"
CERTBOT_DIR="/etc/letsencrypt/live/$DOMAIN_NAME"

mkdir -p $SSL_DIR
mkdir -p /var/www/certbot

# Configure SSL based on deployment mode
if [ "$DEPLOYMENT_MODE" = "production" ]; then
    echo "Configuring for PRODUCTION mode..."

    # Check if Let's Encrypt certificates exist
    if [ -f "$CERTBOT_DIR/fullchain.pem" ] && [ -f "$CERTBOT_DIR/privkey.pem" ]; then
        echo "Using Let's Encrypt certificates"
        export SSL_CERTIFICATE="$CERTBOT_DIR/fullchain.pem"
        export SSL_CERTIFICATE_KEY="$CERTBOT_DIR/privkey.pem"
    else
        echo "WARNING: Let's Encrypt certificates not found at $CERTBOT_DIR"
        echo "Generating temporary self-signed certificate..."
        echo "Please run certbot to get a valid SSL certificate"

        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout $SSL_DIR/selfsigned.key \
            -out $SSL_DIR/selfsigned.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN_NAME"

        export SSL_CERTIFICATE="$SSL_DIR/selfsigned.crt"
        export SSL_CERTIFICATE_KEY="$SSL_DIR/selfsigned.key"
    fi

    # In production, redirect HTTP to HTTPS
    export HTTP_REDIRECT="return 301 https://\$server_name\$request_uri;"

    # Enable HTTPS server in production
    export HTTPS_SERVER_CONFIG="server {
    listen 443 ssl http2;
    server_name \$NGINX_SERVER_NAME;

    ssl_certificate $SSL_CERTIFICATE;
    ssl_certificate_key $SSL_CERTIFICATE_KEY;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}"

else
    echo "Configuring for DEVELOPMENT mode..."
    echo "Development uses HTTP only (no SSL)"

    # Use dummy certificate paths (won't be used in dev)
    export SSL_CERTIFICATE="$SSL_DIR/dummy.crt"
    export SSL_CERTIFICATE_KEY="$SSL_DIR/dummy.key"

    # In development, don't redirect (allow HTTP)
    export HTTP_REDIRECT="# Development mode - HTTP only, HTTPS server disabled"

    # Disable HTTPS server in development
    export HTTPS_SERVER_CONFIG="# HTTPS server disabled in development mode"
fi

echo "SSL Certificate: $SSL_CERTIFICATE"
echo "SSL Key: $SSL_CERTIFICATE_KEY"

# Generate nginx config from template
echo "Generating nginx configuration..."
envsubst '${NGINX_SERVER_NAME} ${SSL_CERTIFICATE} ${SSL_CERTIFICATE_KEY} ${HTTP_REDIRECT} ${HTTPS_SERVER_CONFIG}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

echo "Nginx configuration generated successfully!"
cat /etc/nginx/conf.d/default.conf

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Start nginx
echo "Starting nginx..."
exec nginx -g 'daemon off;'

