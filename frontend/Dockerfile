FROM node:lts-alpine AS build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:stable-alpine

# Install OpenSSL for generating self-signed certificates
RUN apk add --no-cache openssl

# Copy nginx template configuration
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template

# Copy the entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copy built files
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose both HTTP and HTTPS
EXPOSE 80 443

# Use custom entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
