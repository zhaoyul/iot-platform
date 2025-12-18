FROM node:18-alpine AS builder

WORKDIR /app

# Install Java for ClojureScript compilation
RUN apk add --no-cache openjdk17

# Copy deps.edn and shadow-cljs.edn
COPY deps.edn shadow-cljs.edn ./

# Install shadow-cljs globally
RUN npm install -g shadow-cljs

# Copy source code
COPY src ./src
COPY resources ./resources

# Build ClojureScript
RUN shadow-cljs release app

# Production stage with Nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/resources/public /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
