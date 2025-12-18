# IoT Platform - 下一代Git集成管理平台与工业DevOps体系

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](docker-compose.yml)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](k8s/)
[![Clojure](https://img.shields.io/badge/Clojure-1.11-blue.svg)](https://clojure.org/)

## 概述

IoT Platform 是一个基于 **Clojure/ClojureScript** 生态构建的下一代Git集成管理平台，专为工业DevOps场景设计。采用函数式编程范式，实现了传统代码、PLC程序、EDA设计文件、固件等多种资产的统一管理，为追求数据主权、成本控制及高度定制化的组织提供完整的解决方案。

### 技术栈

- **后端**: Clojure + Ring + Reitit + next.jdbc + clj-jgit
- **前端**: ClojureScript + Reagent + Re-frame + Shadow-cljs
- **数据库**: PostgreSQL + Redis
- **Git服务**: Gitea
- **监控**: Prometheus + Grafana

### 核心特性

🚀 **统一资产管理**
- 支持传统代码、PLC程序、EDA设计文件、固件等多种资产类型
- 基于Git的版本控制，支持大型二进制文件（Git LFS）
- 函数式数据处理，不可变数据结构保证一致性

🔍 **深度代码分析**
- Clojure函数式解析引擎
- 依赖关系可视化
- PLC梯形图渲染（SVG/Canvas）
- EDA原理图差异对比

🏭 **工业自动化支持**
- PLC程序解析（IEC 61131-3标准）
- 网络设备配置管理（Oxidized集成）
- 自动化CI/CD流水线（core.async）
- 设备配置版本追踪

📊 **强大的可视化**
- Reagent交互式组件
- SVG原生图形渲染
- 实时状态管理（Re-frame）
- 监控仪表板（Grafana）

🔒 **企业级安全**
- JWT认证（buddy库）
- 细粒度权限控制（RBAC）
- 完整的审计日志
- 数据主权保障

⚡ **函数式架构优势**
- 不可变数据结构，并发安全
- 纯函数，易于测试
- REPL驱动开发
- 前后端代码共享

## 快速开始

### 使用Docker Compose部署（推荐用于开发和测试）

```bash
# 克隆仓库
git clone https://github.com/zhaoyul/iot-platform.git
cd iot-platform

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 访问服务
# Gitea: http://localhost:3000
# 可视化前端: http://localhost:8081
# Grafana: http://localhost:3001
```

### 使用Kubernetes部署（推荐用于生产环境）

```bash
# 创建命名空间
kubectl create namespace iot-platform

# 部署所有组件
kubectl apply -k k8s/base -n iot-platform

# 查看部署状态
kubectl get pods -n iot-platform
```

详细的安装和配置说明，请参阅 [安装指南](docs/INSTALLATION.md)。

## 架构设计

本平台采用分层微服务架构：

```
┌─────────────────────────────────────────────┐
│          可视化层 (Visualization)           │
│   React Flow | JointJS | Grafana | D3.js   │
├─────────────────────────────────────────────┤
│          业务逻辑层 (Business Logic)         │
│   Asset Manager | Git Parser | Automation   │
├─────────────────────────────────────────────┤
│          Git核心层 (Git Core)               │
│   Gitea/Forgejo | Libgit2 | Go-Git         │
├─────────────────────────────────────────────┤
│          数据层 (Data Layer)                │
│   PostgreSQL | Redis | MinIO | Git LFS     │
└─────────────────────────────────────────────┘
```

### 主要组件

- **Gitea/Forgejo**: 轻量级Git服务核心
- **Git Parser Service**: 基于Go-Git的代码解析引擎
- **Asset Manager**: Python FastAPI实现的资产管理服务
- **Visualization Frontend**: React + TypeScript前端应用
- **Oxidized**: 网络设备配置自动备份
- **MinIO**: S3兼容的对象存储
- **PostgreSQL**: 关系型数据库
- **Redis**: 缓存和任务队列

完整的架构文档请参阅 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 核心功能

### 1. Git管理与版本控制

```bash
# 创建仓库
git clone http://localhost:3000/your-repo.git
cd your-repo

# 提交代码
git add .
git commit -m "Add PLC control logic"
git push origin main
```

### 2. PLC程序管理

支持多种PLC编程语言：
- Structured Text (ST)
- Ladder Diagram (LD)
- Function Block Diagram (FBD)
- Instruction List (IL)
- Sequential Function Chart (SFC)

示例：[motor_control.st](examples/plc/motor_control.st)

### 3. EDA设计文件管理

支持的EDA工具：
- KiCad
- Altium Designer
- Eagle
- OrCAD

### 4. 自动化CI/CD

```yaml
# .gitea/workflows/plc-ci.yml
name: PLC Program CI
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate PLC Programs
        run: python scripts/plc/validate_plc.py --path plc/
```

### 5. 可视化分析

- 依赖关系图
- PLC梯形图渲染
- 提交历史可视化
- 系统架构图

## API文档

平台提供RESTful API供第三方集成：

```bash
# 获取提交信息
curl http://localhost:8080/api/v1/repos/my-project/commits/abc123

# 上传PLC程序
curl -X POST http://localhost:8082/api/v1/assets/upload \
  -F "file=@motor_control.st" \
  -F "asset_type=plc"

# 分析代码差异
curl "http://localhost:8080/api/v1/repos/my-project/diff?from=abc&to=def"
```

完整的API文档请参阅 [API.md](docs/API.md)。

## 示例项目

- [PLC程序示例](examples/plc/) - 电机控制和温度控制器
- [EDA设计示例](examples/eda/) - KiCad原理图和PCB
- [二进制固件示例](examples/binary/) - 设备固件和引导加载程序

## 监控与运维

### Prometheus指标

访问 http://localhost:9090 查看系统指标：

- 请求率和错误率
- 响应时间分布
- 资源使用情况
- Git操作统计

### Grafana仪表板

访问 http://localhost:3001 查看可视化仪表板：

- 系统概览
- Git服务性能
- 资产管理统计
- 数据库性能

默认登录凭据：
- 用户名: `admin`
- 密码: `admin123`

## 开发指南

### 本地开发环境

```bash
# 启动后端服务
cd services/git-parser
go run cmd/server/main.go

# 启动资产管理服务
cd services/asset-manager
pip install -r requirements.txt
uvicorn main:app --reload

# 启动前端
cd frontend
npm install
npm start
```

### 运行测试

```bash
# Go服务测试
cd services/git-parser
go test ./...

# Python服务测试
cd services/asset-manager
pytest

# 前端测试
cd frontend
npm test
```

## 安全性

### 数据主权

- 完全私有化部署，数据不离开企业边界
- 支持离线运行
- 无外部依赖的商业服务

### 访问控制

- 基于角色的访问控制（RBAC）
- 多因素认证支持
- API密钥和JWT令牌

### 审计

- 完整的操作日志
- 用户行为追踪
- 异常检测和告警

## 性能优化

- **缓存策略**: 多层缓存（浏览器、CDN、Redis、应用）
- **数据库优化**: 索引优化、查询缓存、连接池
- **异步处理**: Celery任务队列处理耗时操作
- **水平扩展**: Kubernetes自动扩缩容

## 贡献指南

我们欢迎所有形式的贡献！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

详细的贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 路线图

### v1.0 (当前)
- [x] Git核心功能
- [x] PLC程序管理
- [x] EDA设计文件支持
- [x] 基础可视化
- [x] Docker部署

### v1.1 (计划中)
- [ ] AI辅助代码审查
- [ ] 高级PLC仿真
- [ ] 3D PCB预览
- [ ] 移动端应用
- [ ] 更多EDA工具支持

### v2.0 (规划中)
- [ ] 分布式Git集群
- [ ] 实时协作编辑
- [ ] 边缘设备集成
- [ ] 机器学习异常检测

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

本项目基于以下优秀的开源项目构建：

- [Gitea](https://gitea.io/) - Git服务
- [Go-Git](https://github.com/go-git/go-git) - Git解析库
- [React Flow](https://reactflow.dev/) - 流程图库
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web框架
- [PostgreSQL](https://www.postgresql.org/) - 数据库
- [Redis](https://redis.io/) - 缓存
- [MinIO](https://min.io/) - 对象存储

## 支持与联系

- 📖 文档: [docs/](docs/)
- 🐛 问题跟踪: [GitHub Issues](https://github.com/zhaoyul/iot-platform/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/zhaoyul/iot-platform/discussions)
- 📧 邮件: support@iot-platform.com

---

**构建更智能的工业DevOps未来** 🚀
