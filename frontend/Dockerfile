# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package configurations securely
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the frontend for production
RUN npm run build

# Production stage - Nginx
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder phase
COPY --from=build /app/dist /usr/share/nginx/html

# Expose HTTP standard port
EXPOSE 80

# Basic health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
