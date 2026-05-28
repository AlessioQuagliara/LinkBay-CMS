FROM php:8.4-fpm-alpine

# Install system dependencies
RUN apk add --no-cache \
    linux-headers \
    git \
    curl \
    libpng-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    libzip-dev \
    zip \
    unzip \
    oniguruma-dev \
    postgresql-dev \
    icu-dev \
    supervisor

# Install PHP extensions
RUN docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install \
        pdo \
        pdo_pgsql \
        pgsql \
        mbstring \
        exif \
        pcntl \
        bcmath \
        gd \
        zip \
        intl \
        opcache

# Install Redis extension (requires build deps on Alpine)
RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && apk del .build-deps

# Create supervisor log directory (Alpine doesn't create it automatically)
RUN mkdir -p /var/log/supervisor

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Copy PHP config first (context root = project root)
COPY docker/php/php.ini /usr/local/etc/php/conf.d/custom.ini
COPY docker/php/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set working directory to where Laravel lives
WORKDIR /var/www

# Copy Laravel application (backend/ subfolder)
COPY backend/ .

# Install PHP dependencies (production)
RUN composer install --no-dev --optimize-autoloader --no-interaction --ignore-platform-req=php*

# Set permissions
RUN chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache && \
    chmod -R 775 /var/www/storage /var/www/bootstrap/cache

EXPOSE 9000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
