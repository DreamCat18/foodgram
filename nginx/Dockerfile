FROM nginx:1.25.4-alpine

COPY docs/ /usr/share/nginx/html/redoc/

COPY openapi-schema.yml /usr/share/nginx/html/redoc/

COPY nginx.conf /etc/nginx/conf.d/default.conf
