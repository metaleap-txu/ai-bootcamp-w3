# Frontend Dockerfile for Database Query Tool
# Development environment with Vite dev server and HMR

# =============================================================================
# Stage 1: Development
# =============================================================================
FROM --platform=linux/amd64 node:20-slim AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

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

# Start Vite dev server
# --host 0.0.0.0: Bind to all interfaces (required for Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
