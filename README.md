# 工业DevOps平台 / Industrial DevOps Platform

> 构建基于开源生态的下一代Git集成管理平台与工业DevOps体系
>
> Building a Next-Generation Git Integration Management Platform and Industrial DevOps System Based on Open-Source Ecosystem

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)
[![Security](https://img.shields.io/badge/security-IEC%2062443-orange.svg)](docs/SECURITY-BEST-PRACTICES.md)

## 🎯 项目愿景 / Vision

打破传统Git平台的限制，构建一个专为工业自动化和物联网设计的DevOps平台。不仅管理文本代码，更深度整合PLC程序、工业协议、大型二进制资产，实现真正的"工业4.0"版本控制。

Break the limitations of traditional Git platforms and build a DevOps platform specifically designed for industrial automation and IoT. Not only managing text code, but deeply integrating PLC programs, industrial protocols, and large binary assets to achieve true "Industry 4.0" version control.

## ✨ 核心特性 / Key Features

### 🔧 工业资产管理 / Industrial Asset Management

- **PLC代码可视化**: 自动渲染Rockwell L5X梯形图、Siemens TIA Portal程序
- **二进制文件优化**: Git LFS + MinIO对象存储，完美管理固件、CAD、虚拟机镜像
- **文件锁机制**: 防止二进制文件的合并冲突
- **自动转换**: 预提交钩子自动将.ACD转换为可审查的.L5X

### 🚀 先进的CI/CD / Advanced CI/CD

- **GitHub Actions兼容**: 直接复用成千上万的现有Actions
- **语义差异分析**: 基于AST的智能diff，识别代码移动而非删除+新增
- **安全扫描集成**: Trivy漏洞扫描，OSV-Scanner供应链检查
- **多平台支持**: Linux、Windows Runner支持厂商专有SDK

### 🔐 企业级安全 / Enterprise Security

- **SSH证书认证**: 自动过期，集中化管理
- **OIDC/OAuth2 SSO**: Keycloak集成，支持LDAP/AD和MFA
- **提交签名强制**: GPG/SSH签名，确保代码完整性
- **审计日志**: Elasticsearch聚合，符合ISO 27001和IEC 62443

### 🌐 自动化生态 / Automation Ecosystem

- **Oxidized备份**: 自动备份网络设备和软PLC配置
- **libplctag集成**: 直接读写PLC标签，实现"配置即代码"
- **Windows代理**: 利用Studio 5000、TIA Portal SDK自动上传PLC程序

### 📊 数据主权 / Data Sovereignty

- **完全自托管**: 数据永不出境，完全控制
- **开源治理**: 基于Forgejo（非营利社区），无供应商锁定
- **轻量级架构**: Go语言编写，512MB内存即可运行
- **成本优势**: 对比商业SaaS，节省80%+成本

## 🏗️ 系统架构 / System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Industrial DevOps Platform                      │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Forgejo  │  │PostgreSQL│  │  MinIO   │  │ Keycloak │       │
│  │   Git    │◄─┤ Database │  │   LFS    │  │  SSO/MFA │       │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │                                                          │
│       │        ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│       ├───────►│Oxidized  │  │Elastic-  │  │  Trivy   │       │
│       │        │ Network  │  │  search  │  │ Security │       │
│       │        │  Backup  │  │   Logs   │  │  Scanner │       │
│       │        └──────────┘  └──────────┘  └──────────┘       │
│       │                                                          │
│       └─────► Custom Renderers (L5X, ST, GraphViz...)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │ PLC/SCADA │       │  Network  │       │Developers │
    │  Devices  │       │  Devices  │       │  & Teams  │
    └───────────┘       └───────────┘       └───────────┘
```

详细架构说明: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.0+
- 最小4GB RAM，推荐8GB

### 5分钟部署 / 5-Minute Deployment

```bash
# 1. 克隆仓库
git clone https://github.com/zhaoyul/iot-platform.git
cd iot-platform

# 2. 生成安全密钥
openssl rand -base64 32  # 复制并更新到 config/forgejo/app.ini

# 3. 启动所有服务
docker-compose up -d

# 4. 访问平台
# Forgejo: http://localhost:3000
# MinIO: http://localhost:9001
# Keycloak: http://localhost:8080
```

详细安装指南: [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md)

## 📚 文档 / Documentation

- **[架构概述](docs/ARCHITECTURE.md)** - 系统架构、组件说明、数据流
- **[快速开始](docs/GETTING-STARTED.md)** - 安装配置、验证测试、故障排除
- **[自定义渲染器](docs/CUSTOM-RENDERERS.md)** - 开发工业文件格式渲染器
- **[安全最佳实践](docs/SECURITY-BEST-PRACTICES.md)** - IEC 62443、ISO 27001合规指南

## 🔌 支持的工业格式 / Supported Industrial Formats

| 格式 | 厂商 | 功能 | 状态 |
|-----|------|-----|------|
| `.l5x` | Rockwell Automation | 梯形图可视化 | ✅ |
| `.acd` | Rockwell Automation | 二进制识别 | ✅ |
| `.st`, `.scl` | IEC 61131-3 | 结构化文本语法高亮 | ✅ |
| `.apj`, `.ap15` | Siemens TIA Portal | 计划支持 | 🔄 |
| `.pro` | CODESYS | 计划支持 | 🔄 |
| `.ipynb` | Jupyter Notebook | 数据分析报告 | ✅ |
| `.dot` | GraphViz | 流程图可视化 | 📋 |

## 🛠️ 主要组件 / Major Components

### 核心平台 / Core Platform

- **[Forgejo](https://forgejo.org/)** - 开源Git托管（社区治理）
- **[PostgreSQL](https://www.postgresql.org/)** - 高性能数据库
- **[MinIO](https://min.io/)** - S3兼容对象存储（Git LFS）

### 安全与认证 / Security & Auth

- **[Keycloak](https://www.keycloak.org/)** - 企业级SSO/OIDC提供者
- **[Trivy](https://trivy.dev/)** - 容器和依赖漏洞扫描

### 自动化与监控 / Automation & Monitoring

- **[Oxidized](https://github.com/ytti/oxidized)** - 网络设备配置备份
- **[Elasticsearch](https://www.elastic.co/)** - 审计日志聚合
- **[Logstash](https://www.elastic.co/logstash)** - 日志处理管道

### 工业协议库 / Industrial Protocol Libraries

- **[libplctag](https://github.com/libplctag/libplctag)** - EtherNet/IP、Modbus通信
- **[pylogix](https://github.com/dmroeder/pylogix)** - Python Allen-Bradley驱动
- **l5x (Python)** - Rockwell L5X文件解析器

## 🔐 安全性 / Security

本平台实施多层防御策略，符合工业网络安全标准:

- ✅ **IEC 62443-3-3**: 工业自动化控制系统安全
- ✅ **ISO/IEC 27001**: 信息安全管理体系
- ✅ **NIST CSF**: 网络安全框架
- ✅ **OWASP**: 安全编码实践

关键安全特性:
- 强制MFA（多因素认证）
- SSH证书认证（自动过期）
- 提交GPG/SSH签名验证
- 实时审计日志
- 自动漏洞扫描
- 网络隔离（VLAN）
- 数据加密（传输+静态）

详见: [docs/SECURITY-BEST-PRACTICES.md](docs/SECURITY-BEST-PRACTICES.md)

## 🎨 自定义渲染器示例 / Custom Renderer Examples

### L5X梯形图渲染 / L5X Ladder Logic

```python
# 自动将Rockwell L5X文件渲染为交互式HTML
python renderers/render-l5x.py < program.l5x > output.html
```

**特性:**
- 程序结构树形展示
- Rung级注释显示
- 标签（Tags）列表
- 可折叠程序/例程

### 结构化文本渲染 / Structured Text

```python
# IEC 61131-3 ST代码语法高亮
python renderers/render-st.py < function.st > output.html
```

**特性:**
- 关键字高亮
- 数据类型识别
- 注释样式化
- 行号显示

## 📊 成本对比 / Cost Comparison

| 项目 | 开源方案 | GitHub Enterprise | GitLab Premium |
|-----|---------|-------------------|---------------|
| 100用户/年 | **$0** | ~$25,000 | ~$20,000 |
| LFS存储 1TB | ~$100 | ~$5,000 | ~$3,000 |
| CI/CD | $0 | 包含 | 包含 |
| 数据主权 | ✅ 完全 | ❌ 云端 | ❌ 云端 |
| 定制化 | ✅ 无限 | ⚠️ 有限 | ⚠️ 有限 |
| **总计** | **~$100** | **~$30,000** | **~$23,000** |

**节省成本**: **99%+** 🎉

## 🤝 贡献 / Contributing

我们欢迎所有形式的贡献！

- 🐛 报告Bug: [GitHub Issues](https://github.com/zhaoyul/iot-platform/issues)
- 💡 功能建议: [Discussions](https://github.com/zhaoyul/iot-platform/discussions)
- 📝 改进文档
- 🔧 提交代码

## 📄 许可证 / License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢 / Acknowledgments

本项目基于以下优秀的开源项目:

- [Forgejo](https://forgejo.org/) - 社区驱动的Git平台
- [Gitea](https://gitea.io/) - 轻量级Git服务
- [Go-Git](https://github.com/go-git/go-git) - 纯Go语言Git实现
- [Keycloak](https://www.keycloak.org/) - 开源身份认证
- 以及所有其他依赖项的维护者

## 📞 联系方式 / Contact

- 项目主页: https://github.com/zhaoyul/iot-platform
- 问题反馈: https://github.com/zhaoyul/iot-platform/issues
- 邮件: (待添加)

---

**⚠️ 免责声明**: 本项目用于教育和研究目的。在生产环境部署前，请进行充分的安全评估和测试。工业控制系统的任何修改都应遵循相关安全标准和最佳实践。

**🌟 如果这个项目对您有帮助，请给我们一个Star！**
