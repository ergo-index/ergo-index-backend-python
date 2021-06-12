FROM nginx:1.15.7-alpine

# Expose the nginx port for the container.
EXPOSE 8081

# Remove html files for default nginx website.
RUN rm -rf /usr/share/nginx/html/*

# Use our nginx config file.
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
