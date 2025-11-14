# Development stage
FROM node:18-alpine as development

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install

COPY frontend/ .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]

# Build stage
FROM node:18-alpine as build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./

RUN npm ci

COPY frontend/ .

RUN npm run build

# Production stage
FROM nginx:alpine as production

COPY --from=build /app/frontend/dist /usr/share/nginx/html

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
