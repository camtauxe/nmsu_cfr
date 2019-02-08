FROM ubuntu:18.04

# Install dependencies
RUN apt-get update \
    && apt-get install -y python3 python3-pip apache2 apache2-utils libapache2-mod-wsgi-py3 \
    && pip3 install mysql-connector bs4

# Make Apache use apache_config.conf as its only enabled site
ADD apache_config.conf /etc/apache2/sites-available/this_site.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf \
    && ln /etc/apache2/sites-available/this_site.conf /etc/apache2/sites-enabled/this_site.conf

ADD ./content /srv/

CMD ["apachectl", "-DFOREGROUND"]
