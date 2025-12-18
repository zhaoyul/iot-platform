# IoT Platform - 安装与部署指南

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 20GB 可用磁盘空间

### 一键部署

```bash
# 克隆仓库
git clone https://github.com/zhaoyul/iot-platform.git
cd iot-platform

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 访问服务

部署完成后，可以通过以下地址访问各个服务：

- **Gitea (Git服务)**: http://localhost:3000
- **可视化前端**: http://localhost:8081
- **Git解析API**: http://localhost:8080
- **资产管理API**: http://localhost:8082
- **MinIO控制台**: http://localhost:9001
- **Grafana监控**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### 初始配置

#### 1. Gitea初始化

首次访问 http://localhost:3000 时，Gitea会自动完成初始化。使用以下凭据：

- 管理员用户名: `admin`
- 管理员密码: `admin123` （首次登录后请修改）

#### 2. MinIO配置

访问 http://localhost:9001 配置对象存储：

- 用户名: `minioadmin`
- 密码: `minioadmin123`

创建一个bucket用于存储大型文件：
- Bucket名称: `iot-assets`
- Access Policy: `private`

#### 3. Grafana配置

访问 http://localhost:3001：

- 用户名: `admin`
- 密码: `admin123`

首次登录会提示添加数据源，选择Prometheus：
- URL: `http://prometheus:9090`

## Kubernetes部署

### 前置要求

- Kubernetes 1.24+
- kubectl配置完成
- Helm 3.0+（可选）

### 部署步骤

```bash
# 创建命名空间
kubectl create namespace iot-platform

# 部署PostgreSQL
kubectl apply -f k8s/base/postgres.yaml -n iot-platform

# 部署Redis
kubectl apply -f k8s/base/redis.yaml -n iot-platform

# 部署Gitea
kubectl apply -f k8s/base/gitea.yaml -n iot-platform

# 部署Git解析服务
kubectl apply -f k8s/base/git-parser.yaml -n iot-platform

# 部署资产管理服务
kubectl apply -f k8s/base/asset-manager.yaml -n iot-platform

# 部署前端
kubectl apply -f k8s/base/frontend.yaml -n iot-platform

# 配置Ingress
kubectl apply -f k8s/base/ingress.yaml -n iot-platform

# 查看部署状态
kubectl get pods -n iot-platform
kubectl get svc -n iot-platform
```

### 生产环境配置

对于生产环境，使用overlay配置：

```bash
# 应用生产环境配置
kubectl apply -k k8s/overlays/prod -n iot-platform
```

生产环境包含：
- 高可用配置（3个副本）
- 持久化存储配置
- 资源限制和请求
- 网络策略
- TLS/SSL配置
- 自动扩缩容（HPA）

## 配置说明

### 环境变量

在`docker-compose.yml`中可以配置以下环境变量：

#### Gitea
```yaml
GITEA__database__DB_TYPE: postgres          # 数据库类型
GITEA__database__HOST: postgres:5432        # 数据库地址
GITEA__server__DOMAIN: localhost            # 服务域名
GITEA__server__ROOT_URL: http://localhost:3000  # 根URL
```

#### Git Parser Service
```yaml
REDIS_URL: redis://redis:6379               # Redis连接
DATABASE_URL: postgresql://...              # 数据库连接
REPO_PATH: /repositories                    # 仓库路径
```

#### Asset Manager
```yaml
DATABASE_URL: postgresql://...              # 数据库连接
REDIS_URL: redis://redis:6379               # Redis连接
STORAGE_PATH: /assets                       # 存储路径
```

### 存储配置

#### 本地存储（开发环境）

Docker Compose默认使用命名卷：

```yaml
volumes:
  gitea-data:
  postgres-data:
  redis-data:
  asset-storage:
  minio-data:
```

#### 持久化存储（生产环境）

在Kubernetes中使用PersistentVolumeClaim：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: gitea-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 100Gi
```

### 网络配置

#### Docker Compose网络

```yaml
networks:
  iot-network:
    driver: bridge
```

#### Kubernetes网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: iot-platform-netpol
spec:
  podSelector:
    matchLabels:
      app: gitea
  policyTypes:
  - Ingress
  - Egress
```

## 备份与恢复

### 数据库备份

```bash
# PostgreSQL备份
docker-compose exec postgres pg_dump -U gitea gitea > backup.sql

# 恢复
docker-compose exec -T postgres psql -U gitea gitea < backup.sql
```

### Git仓库备份

```bash
# 备份所有仓库
docker-compose exec gitea tar czf /tmp/repos-backup.tar.gz /data/git/repositories

# 复制到宿主机
docker cp iot-gitea:/tmp/repos-backup.tar.gz ./repos-backup.tar.gz
```

### MinIO对象存储备份

使用MinIO Client (mc)：

```bash
# 安装mc
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# 配置
mc alias set iot-minio http://localhost:9000 minioadmin minioadmin123

# 备份
mc mirror iot-minio/iot-assets ./minio-backup/
```

## 监控与日志

### Prometheus监控指标

访问 http://localhost:9090 查看监控指标：

- 系统指标：CPU、内存、磁盘
- 服务指标：请求率、错误率、延迟
- 业务指标：仓库数量、提交数、资产数

### Grafana仪表板

预配置的仪表板包括：

1. **系统概览** - 整体系统健康状况
2. **Git服务** - Gitea性能和使用情况
3. **资产管理** - 资产存储和处理统计
4. **数据库性能** - PostgreSQL查询和连接
5. **缓存性能** - Redis命中率和内存使用

### 日志收集

查看服务日志：

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f gitea
docker-compose logs -f git-parser
docker-compose logs -f asset-manager
```

在Kubernetes中：

```bash
# 查看Pod日志
kubectl logs -f deployment/gitea -n iot-platform

# 查看最近的事件
kubectl get events -n iot-platform --sort-by='.lastTimestamp'
```

## 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 检查服务状态
docker-compose ps

# 查看详细日志
docker-compose logs [service-name]

# 重启服务
docker-compose restart [service-name]
```

#### 2. 数据库连接失败

确保PostgreSQL已启动并可访问：

```bash
# 测试连接
docker-compose exec postgres psql -U gitea -d gitea -c "SELECT 1;"
```

#### 3. Redis连接问题

```bash
# 测试Redis连接
docker-compose exec redis redis-cli ping
```

#### 4. 磁盘空间不足

```bash
# 清理未使用的Docker资源
docker system prune -a

# 清理旧的镜像
docker image prune -a
```

### 性能优化

#### 1. PostgreSQL优化

编辑`postgresql.conf`：

```conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
max_connections = 100
```

#### 2. Redis优化

```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### 3. Gitea优化

在Gitea配置中：

```ini
[repository]
ROOT = /data/git/repositories
DEFAULT_BRANCH = main
DISABLE_HTTP_GIT = false

[cache]
ENABLED = true
ADAPTER = redis
HOST = redis://redis:6379/0

[queue]
TYPE = redis
CONN_STR = redis://redis:6379/1
```

## 安全加固

### 1. 更改默认密码

所有服务的默认密码应该在生产环境中更改。

### 2. 启用HTTPS

使用Let's Encrypt配置SSL：

```bash
# 安装certbot
apt-get install certbot

# 获取证书
certbot certonly --standalone -d git.yourdomain.com
```

### 3. 配置防火墙

```bash
# Ubuntu UFW
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 4. 定期更新

```bash
# 更新Docker镜像
docker-compose pull
docker-compose up -d

# 更新系统
apt-get update && apt-get upgrade
```

## 扩展与定制

### 添加自定义插件

在`services/`目录下创建新的服务目录，参考现有服务的结构。

### 集成第三方工具

通过修改`docker-compose.yml`添加新服务。

### 自定义前端

修改`frontend/src/`目录下的React组件。

## 支持与社区

- 文档: [ARCHITECTURE.md](ARCHITECTURE.md)
- 问题跟踪: GitHub Issues
- 贡献指南: [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。
