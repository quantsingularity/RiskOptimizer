# Dockerfile for RiskOptimizer with Security Best Practices
# Multi-stage build for security and efficiency

# ── Stage 1: Dependencies ──────────────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

# Install dependencies required for native modules
RUN apk add --no-cache libc6-compat python3 make g++

# Copy package manifests and install ALL deps (including dev for build)
COPY package*.json ./
COPY yarn.lock* ./

RUN npm ci && npm cache clean --force

# ── Stage 2: Builder ────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
RUN npm run build

# Prune dev dependencies after build
RUN npm prune --omit=dev && npm cache clean --force

# ── Stage 3: Production runner ──────────────────────────────────────────────
FROM node:20-alpine AS runner

# Install security updates and minimal runtime tools
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        dumb-init \
        curl \
        ca-certificates \
        tzdata && \
    rm -rf /var/cache/apk/* && \
    # Remove package manager to reduce attack surface
    rm -f /usr/local/bin/npm /usr/local/bin/npx

# Create non-root user with explicit IDs
RUN addgroup -g 10001 -S appgroup && \
    adduser -S appuser -u 10001 -G appgroup

WORKDIR /app

# Copy built artifacts and pruned production node_modules from builder
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./package.json

# Create required runtime directories with correct ownership
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appgroup /app && \
    chmod -R 750 /app && \
    chmod -R 770 /app/logs /app/tmp

# Drop to non-root user
USER appuser

# Expose non-privileged port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8080/health || exit 1

# Use dumb-init to handle signals properly and prevent zombie processes
ENTRYPOINT ["dumb-init", "--"]

CMD ["node", "dist/server.js"]

# OCI image labels
LABEL org.opencontainers.image.title="RiskOptimizer API" \
      org.opencontainers.image.description="RiskOptimizer backend application" \
      org.opencontainers.image.vendor="RiskOptimizer" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.source="https://github.com/riskoptimizer/riskoptimizer" \
      org.opencontainers.image.licenses="Proprietary" \
      compliance.gdpr="true" \
      compliance.pci-dss="true" \
      compliance.sox="true" \
      security.scan="enabled"
