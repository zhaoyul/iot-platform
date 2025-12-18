# Git Parser Service - Dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git gcc musl-dev

# 复制go模块文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 编译
RUN CGO_ENABLED=1 GOOS=linux go build -a -installsuffix cgo -o git-parser ./cmd/server

# 运行阶段
FROM alpine:latest

RUN apk --no-cache add ca-certificates git

WORKDIR /root/

# 从构建阶段复制二进制文件
COPY --from=builder /app/git-parser .

EXPOSE 8080

CMD ["./git-parser"]
