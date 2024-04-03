FROM php:8-apache
RUN docker-php-ext-install mysqli
RUN docker-php-ext-install pdo pdo_mysql
RUN a2enmod rewrite

COPY html/ /raw/
COPY entrypoint /

RUN chmod +x /entrypoint

CMD /entrypoint