FROM nginx:1.27

RUN apt-get update && apt-get upgrade -y && apt-get install -y openssl && \
    mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -out /etc/nginx/ssl/pmv.crt -keyout \
    /etc/nginx/ssl/pmv.key -subj "/C=ES/ST=Malaga/L=Malaga/O=42/OU=42 Malaga/CN=fgomez-d.42.fr/UID=fgomez-d"

COPY conf/nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]