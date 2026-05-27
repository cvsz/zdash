FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
COPY frontend/.npmrc ./.npmrc
RUN npm install --legacy-peer-deps --no-audit --fund=false

COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -q -O - http://localhost/ >/dev/null || exit 1
