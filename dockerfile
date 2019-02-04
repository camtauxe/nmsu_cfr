FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y apache2 apache2-utils libapache2-mod-wsgi-py3
RUN apt-get install -y python3 python3-pip
RUN pip3 install mysql-connector bs4

ADD apache_config.conf /etc/apache2/sites-available/this_site.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN ln /etc/apache2/sites-available/this_site.conf /etc/apache2/sites-enabled/this_site.conf

ADD ./static /srv/
ADD ./python/ /srv/

CMD ["apachectl", "-DFOREGROUND"]
