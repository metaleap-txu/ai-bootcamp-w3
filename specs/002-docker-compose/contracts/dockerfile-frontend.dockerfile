# Frontend Dockerfile Contract
#
# Purpose: Dockerfile for React + Vite frontend with HMR support
# Target: Development environment (future: production stage)
# Base Image: node:20-slim
# Platform: linux/amd64 (M1/M2 compatible)

# =============================================================================
# Stage 1: Development
# Purpose: Development environment with Vite dev server and HMR
# =============================================================================
FROM --platform=linux/amd64 node:20-slim AS development

WORKDIR /app

# Copy package files first (layer caching optimization)
COPY package*.json ./

# Install dependencies
# npm ci: Clean install from package-lock.json (faster, more reliable than npm install)
RUN npm ci

# Copy configuration files
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.node.json ./
COPY postcss.config.js ./
COPY index.html ./

# Source code will be mounted as volume at runtime (HMR)
# Volume mount: ./frontend/src:/app/src
# Volume mount (named): frontend_node_modules:/app/node_modules

# Expose Vite dev server port
EXPOSE 5173

# Health check (optional, for monitoring)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:5173', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Start Vite dev server
# --host 0.0.0.0: Bind to all interfaces (required for Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# =============================================================================
# Stage 2: Production (Future - out of scope for this feature)
# Purpose: Multi-stage build with nginx serving static files
# =============================================================================
# FROM development AS builder
# COPY src ./src
# RUN npm run build
#
# FROM nginx:alpine AS production
# COPY --from=builder /app/dist /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Build Command (from repository root):
#   docker build -t db-query-tool-frontend:dev --target development ./frontend
#
# Run Command (standalone, without compose):
#   docker run -p 5173:5173 \
#     -v $(pwd)/frontend/src:/app/src \
#     -v frontend_node_modules:/app/node_modules \
#     -e VITE_API_URL=http://localhost:8000 \
#     db-query-tool-frontend:dev
# =============================================================================
