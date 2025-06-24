# Enhanced Dockerfile for RiskOptimizer with Security Best Practices
# Multi-stage build for security and efficiency

# Build stage
FROM node:18-alpine AS builder

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Security: Set working directory
WORKDIR /app

# Security: Copy package files first for better caching
COPY package*.json ./
COPY yarn.lock* ./

# Security: Install dependencies with exact versions
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

# Security: Install security updates
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    dumb-init \
    curl \
    ca-certificates && \
    rm -rf /var/cache/apk/*

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Security: Set working directory
WORKDIR /app

# Security: Copy built application with proper ownership
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

# Security: Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/tmp && \
    chown -R nextjs:nodejs /app && \
    chmod -R 755 /app

# Security: Switch to non-root user
USER nextjs

# Security: Expose port (non-privileged)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Security: Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "dist/server.js"]

# Security labels
LABEL maintainer="devops@riskoptimizer.com" \
      version="1.0.0" \
      description="RiskOptimizer Application" \
      security.scan="enabled" \
      compliance.gdpr="true" \
      compliance.pci-dss="true" \
      compliance.sox="true"

