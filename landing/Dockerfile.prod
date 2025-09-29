# Frontend Production Dockerfile - Multi-stage build
FROM node:20-alpine AS base

# Installa dipendenze necessarie
RUN apk add --no-cache dumb-init

# Crea user non-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S linkbay -u 1001

# Stage 1: Dependencies
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production --silent && npm cache clean --force

# Stage 2: Build
FROM base AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --silent
COPY . .
RUN npm run build

# Stage 3: Production con Nginx
FROM nginx:alpine AS production

# Installa dumb-init e remove default config
RUN apk add --no-cache dumb-init && \
    rm /etc/nginx/conf.d/default.conf

# Copia configurazione nginx personalizzata
COPY nginx.conf /etc/nginx/conf.d/

# Copia build artifacts
COPY --from=build /app/dist /usr/share/nginx/html

# Crea user nginx se non esiste
RUN addgroup -g 101 -S nginx || true && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx || true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Esponi porta
EXPOSE 80

# Avvia nginx
ENTRYPOINT ["dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]