# 架构概述 / Architecture Overview

## 系统架构图 / System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Industrial DevOps Platform                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Forgejo    │  │  PostgreSQL  │  │    MinIO     │         │
│  │ Git Platform │◄─┤   Database   │  │  LFS Storage │         │
│  │              │  │              │  │              │         │
│  └──────┬───────┘  └──────────────┘  └──────────────┘         │
│         │                                                       │
│         │          ┌──────────────┐  ┌──────────────┐         │
│         ├─────────►│  Keycloak    │  │   Oxidized   │         │
│         │          │  SSO/Auth    │  │ Device Backup│         │
│         │          └──────────────┘  └──────────────┘         │
│         │                                                       │
│         │          ┌──────────────┐  ┌──────────────┐         │
│         └─────────►│ Elasticsearch│  │    Trivy     │         │
│                    │ Log Analysis │  │   Security   │         │
│                    └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  PLC Devices    │   │ Network Devices │   │ Developers      │
│  (EtherNet/IP)  │   │  (SSH/Telnet)   │   │ (Git Clients)   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 核心组件 / Core Components

### 1. Forgejo - Git托管平台 / Git Hosting Platform

**选择理由 / Rationale:**
- 开源社区治理，避免商业锁定 / Open-source community governance, avoiding vendor lock-in
- Go语言编写，资源占用低 / Written in Go, low resource consumption
- 与GitHub Actions兼容的CI/CD / GitHub Actions-compatible CI/CD
- 支持外部渲染器扩展 / Supports external renderer extensions

**关键配置 / Key Configurations:**
- Git LFS启用，使用MinIO后端 / Git LFS enabled with MinIO backend
- 自定义渲染器用于PLC文件 / Custom renderers for PLC files
- Reftable后端支持高频引用 / Reftable backend for high-frequency references
- 审计日志强制开启 / Audit logging mandatorily enabled

### 2. MinIO - 对象存储 / Object Storage

**用途 / Purpose:**
- 存储Git LFS大文件（固件、CAD文件、PLC二进制） / Store Git LFS large files
- 计算与存储分离架构 / Compute-storage separation architecture
- S3兼容，易于迁移和备份 / S3-compatible, easy migration and backup

**配置要点 / Configuration Points:**
```ini
[lfs]
STORAGE_TYPE = minio
MINIO_ENDPOINT = minio:9000
MINIO_BUCKET = forgejo-lfs
```

### 3. Keycloak - 身份认证 / Identity Management

**集成方式 / Integration Method:**
- OIDC/OAuth2提供者 / OIDC/OAuth2 provider
- 支持LDAP/AD联合 / Supports LDAP/AD federation
- 多因素认证（MFA） / Multi-factor authentication
- 符合IEC 62443工业安全标准 / Compliant with IEC 62443 industrial security standards

### 4. Oxidized - 设备配置备份 / Device Configuration Backup

**支持设备类型 / Supported Device Types:**
- 网络设备（Cisco, Juniper, Arista） / Network devices
- 软PLC（CODESYS, Automation Runtime） / Soft PLCs
- 工业交换机 / Industrial switches

**工作流程 / Workflow:**
1. 定时连接设备 / Scheduled device connection
2. 提取配置 / Extract configuration
3. 检测变化 / Detect changes
4. 自动提交到Git / Auto-commit to Git

### 5. Elasticsearch + Logstash - 日志聚合 / Log Aggregation

**用途 / Purpose:**
- 集中化审计日志 / Centralized audit logs
- 合规性报告（ISO 27001） / Compliance reporting
- 安全事件监控 / Security event monitoring
- 性能分析 / Performance analysis

### 6. Trivy - 安全扫描 / Security Scanning

**扫描范围 / Scan Scope:**
- 依赖漏洞检测 / Dependency vulnerability detection
- 容器镜像安全 / Container image security
- 配置文件审查 / Configuration file review
- 供应链安全 / Supply chain security

## 数据流 / Data Flow

### 代码提交流程 / Code Commit Flow

```
Developer → Git Push → Forgejo
                        │
                        ├─→ Git LFS → MinIO (binary files)
                        │
                        ├─→ Custom Renderer → HTML visualization
                        │
                        ├─→ CI/CD Pipeline → Tests & Security Scan
                        │
                        └─→ Audit Log → Elasticsearch
```

### PLC自动备份流程 / PLC Auto-backup Flow

```
PLC Device
    │
    ├─→ libplctag Monitor → Tag Values → JSON
    │                                      │
    │                                      └─→ Git Commit
    │
    └─→ Windows Agent → SDK → .ACD → .L5X → Git Commit
```

## 安全架构 / Security Architecture

### 多层防御 / Defense in Depth

1. **网络层 / Network Layer**
   - 防火墙隔离 / Firewall isolation
   - VPN接入 / VPN access
   - VLAN分段 / VLAN segmentation

2. **认证层 / Authentication Layer**
   - SSH证书认证 / SSH certificate authentication
   - OIDC单点登录 / OIDC SSO
   - 多因素认证 / Multi-factor authentication

3. **授权层 / Authorization Layer**
   - 基于角色的访问控制（RBAC） / Role-based access control
   - 分支保护规则 / Branch protection rules
   - 代码审查强制 / Mandatory code review

4. **审计层 / Audit Layer**
   - 所有操作日志记录 / All operations logged
   - 提交签名验证 / Commit signature verification
   - 合规性报告 / Compliance reporting

5. **数据层 / Data Layer**
   - 静态加密 / Encryption at rest
   - 传输加密（TLS） / Encryption in transit
   - 定期备份 / Regular backups

## 扩展性设计 / Scalability Design

### 水平扩展 / Horizontal Scaling

- Forgejo支持多节点部署 / Forgejo supports multi-node deployment
- PostgreSQL主从复制 / PostgreSQL master-slave replication
- MinIO分布式集群 / MinIO distributed cluster
- Elasticsearch集群模式 / Elasticsearch cluster mode

### 垂直扩展 / Vertical Scaling

- 按需调整容器资源 / Adjust container resources on demand
- 数据库连接池优化 / Database connection pool optimization
- 缓存层（Redis）/ Cache layer (Redis)

## 成本分析 / Cost Analysis

### 开源vs商业 / Open Source vs Commercial

| 项目 / Item | 开源方案 / Open Source | 商业SaaS | 节省 / Savings |
|------------|----------------------|----------|---------------|
| Git托管 / Hosting | $0 | $21/user/month | ~$20k/year (100 users) |
| CI/CD | $0 | $15/user/month | ~$15k/year |
| LFS存储 / Storage | ~$100/TB/year (MinIO) | $500/TB/year | 80% |
| 数据主权 / Data Sovereignty | ✓ 完全控制 / Full control | ✗ 第三方 / 3rd party | Priceless |

## 合规性映射 / Compliance Mapping

### IEC 62443 (工业网络安全 / Industrial Cybersecurity)

- ✓ 身份认证与授权 / Authentication & Authorization
- ✓ 审计日志 / Audit logging
- ✓ 数据完整性（签名） / Data integrity (signatures)
- ✓ 访问控制 / Access control

### ISO 27001 (信息安全管理 / Information Security Management)

- ✓ 访问日志保留 / Access log retention
- ✓ 定期安全扫描 / Regular security scanning
- ✓ 事件响应流程 / Incident response process
- ✓ 数据备份与恢复 / Data backup & recovery

## 参考文档 / References

1. [Forgejo Documentation](https://forgejo.org/docs/latest/)
2. [Git LFS Specification](https://github.com/git-lfs/git-lfs/tree/main/docs)
3. [IEC 62443 Standards](https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards)
4. [Rockwell Automation L5X Format](https://literature.rockwellautomation.com/)
