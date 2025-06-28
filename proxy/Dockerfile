FROM nginx:alpine

RUN mkdir -p /vol/static/swapped \
    && mkdir -p /vol/www \
    && chmod 755 /vol/static \
    && chown -R nginx:nginx /vol

RUN touch /etc/nginx/conf.d/default.conf \
    && chown nginx:nginx /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
