# 快速开始指南 / Quick Start Guide

## 前置要求 / Prerequisites

### 系统要求 / System Requirements

- **服务器配置 / Server Configuration:**
  - CPU: 4核心 / 4 cores
  - 内存: 8GB RAM (最小4GB / minimum 4GB)
  - 磁盘: 100GB SSD
  - 操作系统: Ubuntu 22.04 LTS / CentOS 8 / Debian 11

- **软件依赖 / Software Dependencies:**
  - Docker Engine 24.0+
  - Docker Compose 2.0+
  - Git 2.40+

### 网络要求 / Network Requirements

- 端口开放 / Open Ports:
  - 3000: Forgejo Web界面 / Web Interface
  - 222: Forgejo SSH
  - 8080: Keycloak
  - 9000: MinIO API
  - 9001: MinIO Console
  - 9200: Elasticsearch

## 安装步骤 / Installation Steps

### 1. 克隆仓库 / Clone Repository

```bash
git clone https://github.com/zhaoyul/iot-platform.git
cd iot-platform
```

### 2. 生成密钥 / Generate Secrets

Forgejo需要安全的密钥。运行以下命令生成：

```bash
# 生成SECRET_KEY
openssl rand -base64 32

# 生成LFS_JWT_SECRET
openssl rand -base64 32
```

将生成的密钥更新到 `config/forgejo/app.ini`:

```ini
[security]
SECRET_KEY = <your-generated-secret-key>
LFS_JWT_SECRET = <your-generated-jwt-secret>
```

### 3. 配置数据库 / Configure Database

默认配置使用PostgreSQL。如需使用现有数据库，修改 `docker-compose.yml`:

```yaml
services:
  forgejo:
    environment:
      - FORGEJO__database__HOST=your-db-host:5432
      - FORGEJO__database__NAME=your-db-name
      - FORGEJO__database__USER=your-db-user
      - FORGEJO__database__PASSWD=your-db-password
```

### 4. 启动服务 / Start Services

```bash
# 创建必要的目录
mkdir -p data/{forgejo,postgres,minio,elasticsearch,oxidized}

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f forgejo
```

### 5. 初始化配置 / Initial Configuration

访问 `http://localhost:3000` 完成初始化：

1. 选择数据库类型: PostgreSQL
2. 创建管理员账户
3. 配置服务器域名
4. 保存配置

### 6. 配置MinIO / Configure MinIO

访问 `http://localhost:9001`:

1. 登录 (用户名: `minioadmin`, 密码: `minioadmin`)
2. 创建存储桶: `forgejo-lfs`
3. 设置访问策略为 `private`

### 7. 配置Git LFS / Configure Git LFS

在Forgejo中启用LFS:

```bash
# 在仓库中初始化LFS
git lfs install

# 跟踪大文件类型
git lfs track "*.acd"
git lfs track "*.bin"
git lfs track "*.firmware"
git lfs track "*.iso"

# 提交.gitattributes
git add .gitattributes
git commit -m "Enable Git LFS for binary files"
```

## 验证安装 / Verify Installation

### 测试Git操作 / Test Git Operations

```bash
# 克隆测试仓库
git clone http://localhost:3000/testuser/test-repo.git
cd test-repo

# 创建测试文件
echo "Test content" > test.txt
git add test.txt
git commit -m "Test commit"
git push origin main
```

### 测试LFS / Test LFS

```bash
# 创建大文件
dd if=/dev/urandom of=largefile.bin bs=1M count=10

# 添加到LFS
git lfs track "*.bin"
git add .gitattributes largefile.bin
git commit -m "Add large binary file"
git push origin main

# 验证LFS
git lfs ls-files
```

### 测试自定义渲染器 / Test Custom Renderers

创建一个简单的L5X测试文件:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="TestController" ProcessorType="1756-L71">
    <Programs>
      <Program Name="MainProgram" Type="Normal">
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
            <RLLContent>
              <Rung Number="0" Type="N">
                <Text>XIC(Start_Button)OTE(Motor_Run);</Text>
                <Comment>Start motor when button pressed</Comment>
              </Rung>
            </RLLContent>
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
```

保存为 `test.l5x` 并推送到Forgejo，查看Web界面的渲染效果。

## 常见问题 / Troubleshooting

### 问题1: 无法访问Forgejo Web界面

**解决方案:**

```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs forgejo

# 重启服务
docker-compose restart forgejo
```

### 问题2: Git LFS推送失败

**原因:** MinIO未正确配置或bucket不存在

**解决方案:**

```bash
# 进入MinIO容器
docker exec -it forgejo-minio sh

# 创建bucket
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/forgejo-lfs
mc policy set download local/forgejo-lfs
```

### 问题3: 自定义渲染器不工作

**检查清单:**

1. 确认渲染器脚本有执行权限:
   ```bash
   chmod +x renderers/render-l5x.py
   ```

2. 确认Python依赖已安装:
   ```bash
   pip install lxml
   ```

3. 测试渲染器独立运行:
   ```bash
   cat test.l5x | python renderers/render-l5x.py > output.html
   ```

4. 检查Forgejo日志中的渲染错误:
   ```bash
   docker-compose logs forgejo | grep -i render
   ```

### 问题4: 数据库连接失败

**解决方案:**

```bash
# 检查PostgreSQL容器
docker-compose ps db

# 测试数据库连接
docker exec -it forgejo-db psql -U forgejo -d forgejo -c "SELECT version();"

# 重新初始化数据库
docker-compose down
docker volume rm iot-platform_postgres-data
docker-compose up -d
```

## 下一步 / Next Steps

1. **配置SSO:** 参见 [Keycloak集成指南](./KEYCLOAK-INTEGRATION.md)
2. **设置自动化备份:** 参见 [PLC备份配置](./PLC-BACKUP.md)
3. **启用CI/CD:** 参见 [Actions配置指南](./CICD-SETUP.md)
4. **安全加固:** 参见 [安全最佳实践](./SECURITY-BEST-PRACTICES.md)

## 技术支持 / Support

- 问题反馈: [GitHub Issues](https://github.com/zhaoyul/iot-platform/issues)
- 文档: [在线文档](https://github.com/zhaoyul/iot-platform/docs)
- 社区: [Discussions](https://github.com/zhaoyul/iot-platform/discussions)
