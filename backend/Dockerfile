FROM clojure:temurin-21-tools-deps-alpine AS builder

WORKDIR /app

# Copy deps.edn and download dependencies
COPY deps.edn ./
RUN clojure -P -X:uberjar

# Copy source code
COPY src ./src
COPY resources ./resources

# Build uberjar
RUN clojure -X:uberjar

# Runtime stage
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy the uberjar from builder
COPY --from=builder /app/target/iot-platform.jar ./

EXPOSE 8080

CMD ["java", "-jar", "iot-platform.jar"]
