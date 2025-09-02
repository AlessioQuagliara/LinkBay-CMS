### Builder stage: install deps and compile TypeScript
FROM node:18-alpine AS builder
WORKDIR /usr/src/app

# Install build deps
COPY package.json package-lock.json ./
RUN npm ci --silent

# Copy source and build
COPY tsconfig.json ./
COPY knexfile.ts ./
COPY src ./src
COPY migrations ./migrations
COPY seeds ./seeds
COPY public ./public
COPY views ./views

RUN npm run build

### Production stage: smaller image with only runtime deps and build output
FROM node:18-alpine AS runner
WORKDIR /usr/src/app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Only copy package manifests and install production deps
COPY package.json package-lock.json ./
RUN npm ci --only=production --silent

# Copy compiled app and runtime assets from builder
COPY --from=builder /usr/src/app/dist ./dist
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/views ./views
COPY --from=builder /usr/src/app/knexfile.ts ./knexfile.ts
COPY --from=builder /usr/src/app/migrations ./migrations

ENV NODE_ENV=production
ENV PORT=3000

USER appuser
EXPOSE 3000

CMD ["node", "dist/server.js"]
