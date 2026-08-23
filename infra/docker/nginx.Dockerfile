FROM nginx:1.30.4-alpine

COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/zdash.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O - http://localhost/gateway-health >/dev/null || exit 1
