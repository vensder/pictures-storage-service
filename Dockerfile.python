FROM python:3.5

MAINTAINER vensder <vensder@gmail.com>

# Standard set up Nginx
ENV NGINX_VERSION 1.9.11-1~jessie

COPY ./requirements.txt /app/requirements.txt

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
	&& echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates nginx=${NGINX_VERSION} gettext-base \
        supervisor \
	&& rm -rf /var/lib/apt/lists/* \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && rm /etc/nginx/conf.d/default.conf \
    && pip install --no-cache-dir uwsgi \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && mkdir -p /storage \
    && chown www-data:www-data /storage 

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

