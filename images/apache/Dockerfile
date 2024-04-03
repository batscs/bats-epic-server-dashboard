FROM php:8-apache
RUN docker-php-ext-install mysqli
RUN docker-php-ext-install pdo pdo_mysql
RUN a2enmod rewrite

COPY html/index.html /var/www/html/index.html
COPY html/ /var/www/html/