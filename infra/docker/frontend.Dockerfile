FROM node:24-alpine AS build

WORKDIR /app

ARG VITE_API_BASE_URL=/
ARG VITE_WS_BASE_URL=
ARG VITE_ENABLE_MOCK_FALLBACK=false
ARG VITE_AUTH_ENABLED=false

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_WS_BASE_URL=$VITE_WS_BASE_URL \
    VITE_ENABLE_MOCK_FALLBACK=$VITE_ENABLE_MOCK_FALLBACK \
    VITE_AUTH_ENABLED=$VITE_AUTH_ENABLED

COPY frontend/package.json frontend/package-lock.json ./
COPY frontend/.npmrc ./.npmrc
RUN npm install --legacy-peer-deps --no-audit --fund=false

COPY frontend/ ./
RUN npm run build

FROM nginx:1.30.4-alpine AS runtime

COPY infra/nginx/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -q -O - http://localhost/ >/dev/null || exit 1
