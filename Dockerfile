FROM python:3.5-slim

MAINTAINER vensder <vensder@gmail.com>

# Standard set up Nginx
# ENV NGINX_VERSION 1.9.11-1~jessie
ENV NGINX_VERSION 1.10.2-1~jessie


COPY ./requirements.txt /app/requirements.txt

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
	&& echo "deb http://nginx.org/packages/debian/ jessie nginx" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y \
        ca-certificates \
        nginx=${NGINX_VERSION} \
        gettext-base \
        supervisor \
        gcc \
        libbz2-dev \
        libc6-dev \
        libpcre3-dev \
        libssl-dev \
        make \
        pax-utils \
        zlib1g-dev \
        libmagic1 \
	&& rm -rf /var/lib/apt/lists/* \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && rm /etc/nginx/conf.d/default.conf \
    && pip install --no-cache-dir uwsgi \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && mkdir -p /storage \
    && chown www-data:www-data /storage \
    && apt-get purge -y --auto-remove  gcc \
        libbz2-dev \
        libc6-dev \
        libpcre3-dev \
        libssl-dev \
        make \
        pax-utils \
        zlib1g-dev

# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/

# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/

# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./app /app
WORKDIR /app
EXPOSE 80 443
VOLUME ["/storage"]
CMD ["/usr/bin/supervisord"]

