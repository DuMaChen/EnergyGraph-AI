FROM php:8.3-apache-bookworm

ARG MOODLE_BRANCH=MOODLE_405_STABLE

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        libicu-dev \
        libxml2-dev \
        libzip-dev \
        libonig-dev \
        default-mysql-client \
        unzip \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" \
        gd intl mysqli opcache soap xml zip mbstring \
    && a2enmod rewrite headers expires remoteip \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch "${MOODLE_BRANCH}" https://github.com/moodle/moodle.git /var/www/html \
    && chown -R www-data:www-data /var/www/html

COPY php.ini /usr/local/etc/php/conf.d/moodle.ini
COPY docker-entrypoint.sh /usr/local/bin/moodle-entrypoint
COPY seed-course.php /usr/local/bin/moodle-seed-course.php
RUN mkdir -p /var/www/html/local/course_agent \
    && chmod +x /usr/local/bin/moodle-entrypoint
COPY agent-session.php /var/www/html/local/course_agent/session.php
COPY resource.php /var/www/html/local/course_agent/resource.php
COPY grade-sync.php /var/www/html/local/course_agent/grade-sync.php

WORKDIR /var/www/html
ENTRYPOINT ["moodle-entrypoint"]
CMD ["apache2-foreground"]
