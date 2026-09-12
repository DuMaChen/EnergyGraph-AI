ARG MOODLE_BASE_IMAGE=php:8.3-apache-bookworm
FROM ${MOODLE_BASE_IMAGE}

ARG MOODLE_BRANCH=MOODLE_405_STABLE

ENV DEBIAN_FRONTEND=noninteractive

ARG REUSE_MOODLE_IMAGE=0

RUN if [ "$REUSE_MOODLE_IMAGE" != "1" ]; then \
        echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4; \
        apt-get update; \
        apt-get install -y --no-install-recommends \
            git \
            libfreetype6-dev \
            libjpeg62-turbo-dev \
            libpng-dev \
            libicu-dev \
            libxml2-dev \
            libzip-dev \
            libonig-dev \
            default-mysql-client \
            unzip; \
        docker-php-ext-configure gd --with-freetype --with-jpeg; \
        docker-php-ext-install -j"$(nproc)" \
            gd intl mysqli opcache soap xml zip mbstring; \
        a2enmod rewrite headers expires remoteip; \
        rm -rf /var/lib/apt/lists/*; \
    fi

RUN if [ "$REUSE_MOODLE_IMAGE" != "1" ]; then \
        git clone --depth 1 --branch "${MOODLE_BRANCH}" https://github.com/moodle/moodle.git /var/www/html; \
        chown -R www-data:www-data /var/www/html; \
    fi

COPY php.ini /usr/local/etc/php/conf.d/moodle.ini
COPY docker-entrypoint.sh /usr/local/bin/moodle-entrypoint
COPY seed-course.php /usr/local/bin/moodle-seed-course.php
COPY local/course_agent /var/www/html/local/course_agent
RUN chmod +x /usr/local/bin/moodle-entrypoint

WORKDIR /var/www/html
ENTRYPOINT ["moodle-entrypoint"]
CMD ["apache2-foreground"]
