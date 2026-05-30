FROM node:20-alpine AS build
WORKDIR /app

# Docker часто наследует proxy с хоста — внутри контейнера он ломает npm install
ENV HTTP_PROXY= \
    HTTPS_PROXY= \
    http_proxy= \
    https_proxy= \
    ALL_PROXY= \
    all_proxy= \
    npm_config_proxy= \
    npm_config_https_proxy=

COPY package*.json .npmrc ./
RUN npm config delete proxy 2>/dev/null || true \
 && npm config delete https-proxy 2>/dev/null || true \
 && npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
