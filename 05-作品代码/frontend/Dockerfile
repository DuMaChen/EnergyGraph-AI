FROM node:22-alpine AS build

ARG NPM_REGISTRY=https://registry.npmjs.org/
RUN npm config set registry "${NPM_REGISTRY}" \
    && npm config get registry

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_BASE_PATH=/learn/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}
RUN npm run build

FROM nginx:1.27.5-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# Source files may arrive with restrictive host permissions (e.g. 600); the
# nginx worker runs as an unprivileged user, so ensure every artifact under
# the document root is world-readable and every directory traversable.
RUN chmod -R a+rX /usr/share/nginx/html
