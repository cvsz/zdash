FROM nginx:alpine
COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/zdash.conf /etc/nginx/conf.d/default.conf
