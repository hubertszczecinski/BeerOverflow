#!/bin/bash

# Quick test script for SSL configuration

echo "=== Testing BeerOverflow SSL Configuration ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Run: cp .env.example .env"
    exit 1
fi

# Load environment
source .env

echo "Configuration:"
echo "  Deployment Mode: $DEPLOYMENT_MODE"
echo "  Domain: $DOMAIN_NAME"
echo "  HTTP Port: ${HTTP_PORT:-8080}"
echo "  HTTPS Port: ${HTTPS_PORT:-8443}"
echo ""

# Test based on mode
if [ "$DEPLOYMENT_MODE" = "production" ]; then
    echo "Testing Production Configuration..."
    echo ""

    # Test DNS
    echo "1. Checking DNS for $DOMAIN_NAME..."
    if command -v nslookup &> /dev/null; then
        nslookup $DOMAIN_NAME
    elif command -v dig &> /dev/null; then
        dig $DOMAIN_NAME +short
    else
        echo "   ⚠️  Install nslookup or dig to test DNS"
    fi
    echo ""

    # Test HTTP
    echo "2. Testing HTTP (should redirect to HTTPS)..."
    curl -I http://$DOMAIN_NAME 2>&1 | head -n 5
    echo ""

    # Test HTTPS
    echo "3. Testing HTTPS..."
    curl -I https://$DOMAIN_NAME 2>&1 | head -n 5
    echo ""

    # Check certificate
    echo "4. Checking SSL certificate..."
    if docker-compose ps frontend | grep -q "Up"; then
        docker-compose exec frontend sh -c "
            if [ -f /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem ]; then
                echo '✅ Let'\''s Encrypt certificate found'
                openssl x509 -in /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem -noout -dates
            else
                echo '⚠️  Using self-signed certificate'
                echo '   Run certbot to get Let'\''s Encrypt certificate'
            fi
        "
    else
        echo "   ⚠️  Frontend container not running"
    fi

else
    echo "Testing Development Configuration..."
    echo ""

    # Test HTTP
    echo "1. Testing HTTP (localhost:${HTTP_PORT:-8080})..."
    curl -I http://localhost:${HTTP_PORT:-8080} 2>&1 | head -n 5
    echo ""

    # Test HTTPS
    echo "2. Testing HTTPS (localhost:${HTTPS_PORT:-8443})..."
    curl -k -I https://localhost:${HTTPS_PORT:-8443} 2>&1 | head -n 5
    echo ""

    # Check self-signed certificate
    echo "3. Checking self-signed certificate..."
    if docker-compose ps frontend | grep -q "Up"; then
        docker-compose exec frontend sh -c "
            if [ -f /etc/nginx/ssl/localhost.crt ]; then
                echo '✅ Self-signed certificate found'
                openssl x509 -in /etc/nginx/ssl/localhost.crt -noout -dates
            else
                echo '❌ Certificate not found'
            fi
        "
    else
        echo "   ⚠️  Frontend container not running"
    fi

    echo ""
    echo "To access the app:"
    echo "  HTTP:  http://localhost:${HTTP_PORT:-8080}"
    echo "  HTTPS: https://localhost:${HTTPS_PORT:-8443} (accept security warning)"
fi

echo ""
echo "=== Test Complete ==="

