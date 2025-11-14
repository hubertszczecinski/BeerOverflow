# --- Build Stage ---
# Use an official Node.js LTS image for the build environment
FROM node:lts-alpine as build-stage

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Installa project dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the app for production
RUN npm run build

# --- Production Stage ---
# Use a lightweight Nginx image to serve the static files
FROM nginx:stable-alpine

# Copy the custom Nginx configuration
# This will be created in the next file.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built static files from the build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# The default Nginx command will run and serve files
CMD ["nginx", "-g", "daemon off;"]