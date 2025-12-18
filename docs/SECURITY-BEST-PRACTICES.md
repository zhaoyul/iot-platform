# 安全最佳实践指南 / Security Best Practices Guide

## 概述 / Overview

工业DevOps平台处理关键的PLC代码、配置和知识产权，必须实施严格的安全措施。本指南基于IEC 62443、ISO 27001和NIST网络安全框架。

## 1. 身份认证与授权 / Authentication & Authorization

### 1.1 启用SSH证书认证 / Enable SSH Certificate Authentication

**传统SSH密钥的问题:**
- 难以撤销 / Hard to revoke
- 无过期时间 / No expiration
- 难以审计 / Difficult to audit

**SSH证书解决方案:**

```bash
# 1. 生成CA密钥（仅一次）
ssh-keygen -t rsa -b 4096 -f ca-key -C "Forgejo SSH CA"

# 2. 配置Forgejo信任CA
# 在 app.ini 中:
[ssh.trusted_user_ca_keys]
- = /data/ssh/ca-key.pub

# 3. 为用户签发证书（30天有效期）
ssh-keygen -s ca-key \
  -I "user-email@company.com" \
  -n git \
  -V +30d \
  -z 1 \
  user-key.pub
```

**优势:**
- ✓ 自动过期，降低密钥泄露风险
- ✓ 可包含用户身份信息
- ✓ 集中化撤销管理

### 1.2 配置Keycloak SSO

**步骤:**

1. **创建Realm（领域）:**

```bash
# 在Keycloak管理界面
1. 访问 http://localhost:8080
2. 登录: admin / admin
3. 创建新Realm: "industrial-devops"
```

2. **配置OIDC客户端:**

```json
{
  "clientId": "forgejo",
  "enabled": true,
  "protocol": "openid-connect",
  "redirectUris": [
    "http://localhost:3000/*"
  ],
  "webOrigins": [
    "http://localhost:3000"
  ],
  "standardFlowEnabled": true,
  "implicitFlowEnabled": false,
  "directAccessGrantsEnabled": true
}
```

3. **在Forgejo中配置OIDC:**

```ini
[oauth2_client]
REGISTER_EMAIL_CONFIRM = false
OPENID_CONNECT_SCOPES = openid profile email groups
ENABLE_AUTO_REGISTRATION = true

[oauth2.keycloak]
PROVIDER = openid-connect
CLIENT_ID = forgejo
CLIENT_SECRET = <from-keycloak>
OPENID_CONNECT_AUTO_DISCOVERY_URL = http://keycloak:8080/realms/industrial-devops/.well-known/openid-configuration
```

### 1.3 启用多因素认证（MFA）

**在Keycloak中配置:**

```
1. Realm Settings → Security Defenses → Brute Force Detection
   - 启用永久锁定
   - 失败登录阈值: 5次
   - 锁定时间: 30分钟

2. Authentication → Flows
   - 复制Browser flow
   - 添加OTP Form执行器
   - 设置为Required

3. Required Actions
   - Configure OTP: 启用
```

**在Forgejo中启用:**

```ini
[service]
ENABLE_TIMETRACKING = true
DEFAULT_ENABLE_TIMETRACKING = true

[security]
LOGIN_REMEMBER_DAYS = 7
COOKIE_REMEMBER_NAME = forgejo_incredible
REVERSE_PROXY_AUTHENTICATION = false
DISABLE_GIT_HOOKS = false
```

## 2. 提交签名与验证 / Commit Signing & Verification

### 2.1 强制GPG签名

**配置分支保护:**

```bash
# 在Forgejo Web界面
Repository → Settings → Branches → Protected Branches

配置:
- Branch name pattern: main
- Require signed commits: ✓
- Block unsigned commits: ✓
- Require approval before merging: ✓
```

**开发者配置:**

```bash
# 生成GPG密钥
gpg --full-generate-key
# 选择: RSA and RSA, 4096 bits

# 列出密钥
gpg --list-secret-keys --keyid-format LONG

# 导出公钥
gpg --armor --export <KEY_ID>

# 配置Git使用GPG
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
git config --global tag.gpgsign true
```

### 2.2 SSH提交签名（Git 2.34+）

```bash
# 生成SSH签名密钥
ssh-keygen -t ed25519 -C "your-email@company.com" -f ~/.ssh/git_signing_key

# 配置Git
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/git_signing_key.pub
git config --global commit.gpgsign true

# 添加允许的签名者
echo "$(git config --get user.email) $(cat ~/.ssh/git_signing_key.pub)" >> ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```

## 3. 网络安全 / Network Security

### 3.1 启用TLS/SSL

**生成自签名证书（测试用）:**

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/forgejo.key \
  -out /etc/ssl/certs/forgejo.crt \
  -subj "/CN=forgejo.company.local"
```

**配置Nginx反向代理:**

```nginx
server {
    listen 443 ssl http2;
    server_name git.company.local;

    ssl_certificate /etc/ssl/certs/forgejo.crt;
    ssl_certificate_key /etc/ssl/private/forgejo.key;
    
    # 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 其他安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**更新docker-compose.yml:**

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/nginx/ssl:/etc/ssl:ro
    depends_on:
      - forgejo
```

### 3.2 防火墙配置

```bash
# UFW配置（Ubuntu）
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp     # SSH
ufw allow 443/tcp    # HTTPS
ufw allow 222/tcp    # Forgejo SSH
ufw enable

# 限制SSH访问（仅内网）
ufw delete allow 22/tcp
ufw allow from 192.168.0.0/16 to any port 22

# 限制Git SSH（仅开发者子网）
ufw delete allow 222/tcp
ufw allow from 10.0.0.0/8 to any port 222
```

### 3.3 网络隔离（VLAN）

```yaml
# docker-compose.yml 网络隔离
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 无外网访问

services:
  forgejo:
    networks:
      - frontend
      - backend
  
  db:
    networks:
      - backend  # 数据库仅后端可访问
  
  nginx:
    networks:
      - frontend  # 仅前端网络
```

## 4. 数据保护 / Data Protection

### 4.1 加密存储

**启用数据库加密（PostgreSQL）:**

```bash
# 使用pgcrypto扩展
docker exec -it forgejo-db psql -U forgejo -d forgejo

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密敏感字段
ALTER TABLE users ADD COLUMN email_encrypted BYTEA;
UPDATE users SET email_encrypted = pgp_sym_encrypt(email, 'encryption-key');
```

**Git仓库加密（git-crypt）:**

```bash
# 在敏感仓库中
cd /path/to/sensitive-repo

# 初始化git-crypt
git-crypt init

# 配置加密文件
cat > .gitattributes << EOF
*.key filter=git-crypt diff=git-crypt
*.secret filter=git-crypt diff=git-crypt
config/*.env filter=git-crypt diff=git-crypt
EOF

# 添加GPG用户
git-crypt add-gpg-user <GPG_KEY_ID>

# 提交
git add .gitattributes
git commit -m "Enable git-crypt"
```

### 4.2 备份与恢复

**自动化备份脚本:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/forgejo-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份数据库
docker exec forgejo-db pg_dump -U forgejo forgejo | gzip > "$BACKUP_DIR/database.sql.gz"

# 备份Git仓库
rsync -avz --delete ./data/forgejo/git/repositories/ "$BACKUP_DIR/repositories/"

# 备份配置
cp -r ./config "$BACKUP_DIR/"

# 备份LFS（MinIO）
docker exec forgejo-minio mc mirror local/forgejo-lfs "$BACKUP_DIR/lfs/"

# 加密备份
tar czf - "$BACKUP_DIR" | gpg --symmetric --cipher-algo AES256 > "$BACKUP_DIR.tar.gz.gpg"

# 上传到远程
rclone copy "$BACKUP_DIR.tar.gz.gpg" remote:backups/

# 清理本地备份（保留7天）
find /backup -type d -mtime +7 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
```

**添加到crontab:**

```bash
# 每天凌晨2点备份
0 2 * * * /opt/iot-platform/scripts/backup.sh >> /var/log/forgejo-backup.log 2>&1
```

## 5. 审计与监控 / Auditing & Monitoring

### 5.1 配置审计日志

**Forgejo审计配置:**

```ini
[log]
MODE = console, file
LEVEL = Info
ROOT_PATH = /data/gitea/log

[log.file]
LOG_ROTATE = true
MAX_SIZE_SHIFT = 28
DAILY_ROTATE = true
MAX_DAYS = 90

[audit]
ENABLE = true

[git]
VERBOSE_PUSH = true
VERBOSE_PUSH_DELAY = 5s
```

**日志聚合到Elasticsearch:**

```python
# scripts/log-shipper.py
import os
import json
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

def ship_logs():
    log_file = '/data/gitea/log/gitea.log'
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                es.index(index='forgejo-logs', document=log_entry)
            except:
                pass

if __name__ == '__main__':
    ship_logs()
```

### 5.2 安全事件监控

**配置告警规则:**

```yaml
# config/alerts.yml
groups:
  - name: security
    rules:
      - alert: UnauthorizedAccessAttempt
        expr: rate(forgejo_auth_failures[5m]) > 5
        for: 5m
        annotations:
          summary: "Multiple failed login attempts detected"
      
      - alert: LargeFileUpload
        expr: forgejo_lfs_upload_bytes > 1073741824  # 1GB
        annotations:
          summary: "Large file uploaded to LFS"
      
      - alert: SuspiciousGitOperation
        expr: rate(forgejo_git_push_errors[5m]) > 10
        annotations:
          summary: "Unusual Git push error rate"
```

### 5.3 实时监控仪表板

使用Grafana可视化:

```yaml
# config/grafana/dashboards/security.json
{
  "dashboard": {
    "title": "Security Monitoring",
    "panels": [
      {
        "title": "Failed Login Attempts",
        "type": "graph",
        "datasource": "Elasticsearch",
        "targets": [{
          "query": "event:login_failed"
        }]
      },
      {
        "title": "Git Operations",
        "type": "graph",
        "targets": [{
          "query": "event:git_push OR event:git_pull"
        }]
      }
    ]
  }
}
```

## 6. 漏洞管理 / Vulnerability Management

### 6.1 依赖扫描

**集成Trivy到CI/CD:**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
          exit-code: 1  # 发现漏洞时失败
```

### 6.2 定期安全审计

**创建审计检查清单:**

```markdown
## 月度安全审计清单

- [ ] 审查用户访问权限
- [ ] 检查未使用的SSH密钥
- [ ] 审核最近90天的Git操作
- [ ] 验证所有提交已签名
- [ ] 检查异常登录时间和位置
- [ ] 更新依赖到最新安全版本
- [ ] 验证备份完整性
- [ ] 测试恢复流程
- [ ] 审查防火墙规则
- [ ] 检查SSL证书过期时间
```

## 7. 事件响应 / Incident Response

### 7.1 账户泄露响应流程

```bash
#!/bin/bash
# scripts/account-breach-response.sh

USER_EMAIL=$1

echo "Initiating breach response for $USER_EMAIL"

# 1. 立即禁用账户
docker exec forgejo forgejo admin user disable --username "$USER_EMAIL"

# 2. 撤销所有活动会话
docker exec forgejo forgejo admin auth delete-session --username "$USER_EMAIL"

# 3. 撤销SSH密钥
docker exec forgejo forgejo admin user key list --username "$USER_EMAIL" | \
  awk '{print $1}' | xargs -I {} forgejo admin user key delete --id {}

# 4. 记录事件
echo "$(date): Account breach response executed for $USER_EMAIL" >> /var/log/security-incidents.log

# 5. 通知安全团队
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -d "channel=#security" \
  -d "text=SECURITY ALERT: Account breach response for $USER_EMAIL"

echo "Response completed. User must reset password to regain access."
```

### 7.2 数据泄露响应

```bash
#!/bin/bash
# scripts/data-leak-response.sh

REPO_NAME=$1

# 1. 立即归档仓库
curl -X PATCH "http://localhost:3000/api/v1/repos/$REPO_NAME" \
  -H "Authorization: token $ADMIN_TOKEN" \
  -d '{"archived": true}'

# 2. 导出访问日志
docker exec forgejo forgejo admin repo logs "$REPO_NAME" > \
  "/tmp/repo-${REPO_NAME}-access-$(date +%s).log"

# 3. 创建取证快照
rsync -avz "./data/forgejo/git/repositories/$REPO_NAME.git" \
  "/forensics/$(date +%Y%m%d)/"

# 4. 通知受影响用户
# ... 发送邮件通知

echo "Data leak response completed for $REPO_NAME"
```

## 8. 合规性 / Compliance

### 8.1 IEC 62443合规映射

| 要求 | 实现方式 |
|-----|---------|
| FR 1: 识别与认证控制 | Keycloak SSO + MFA |
| FR 2: 使用控制 | RBAC权限 + 分支保护 |
| FR 3: 系统完整性 | 提交签名 + 文件完整性检查 |
| FR 4: 数据机密性 | TLS加密 + git-crypt |
| FR 5: 受限数据流 | 防火墙 + 网络隔离 |
| FR 6: 及时响应事件 | 实时监控 + 告警 |
| FR 7: 资源可用性 | 备份恢复 + 高可用部署 |

### 8.2 ISO 27001合规

**生成审计报告:**

```python
# scripts/compliance-report.py
from datetime import datetime, timedelta
import json

def generate_iso27001_report():
    report = {
        "report_date": datetime.now().isoformat(),
        "period": "Last 90 days",
        "sections": {
            "access_control": {
                "total_users": count_users(),
                "mfa_enabled": count_mfa_users(),
                "inactive_accounts": find_inactive_accounts(90)
            },
            "audit_logging": {
                "total_events": count_audit_events(90),
                "security_events": count_security_events(90),
                "log_retention_days": 90
            },
            "vulnerability_management": {
                "last_scan": get_last_scan_date(),
                "critical_vulns": count_vulnerabilities("CRITICAL"),
                "high_vulns": count_vulnerabilities("HIGH")
            },
            "backup_recovery": {
                "last_backup": get_last_backup_date(),
                "backup_success_rate": calculate_backup_success_rate(30),
                "recovery_test_date": get_last_recovery_test()
            }
        }
    }
    
    with open(f"compliance-report-{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return report
```

## 9. 安全配置检查清单 / Security Configuration Checklist

### 部署前检查 / Pre-deployment Checklist

- [ ] 修改所有默认密码
- [ ] 生成唯一的SECRET_KEY和JWT_SECRET
- [ ] 启用HTTPS/TLS
- [ ] 配置防火墙规则
- [ ] 启用审计日志
- [ ] 配置日志聚合
- [ ] 设置备份计划
- [ ] 测试恢复流程
- [ ] 配置SSO/OIDC
- [ ] 启用MFA
- [ ] 配置分支保护
- [ ] 强制提交签名
- [ ] 配置漏洞扫描
- [ ] 设置安全告警
- [ ] 创建事件响应计划
- [ ] 培训用户安全意识

### 运营中检查 / Operational Checklist

- [ ] 每日审查安全日志
- [ ] 每周扫描漏洞
- [ ] 每月安全审计
- [ ] 季度渗透测试
- [ ] 年度灾难恢复演练

## 10. 参考资源 / References

- [IEC 62443-3-3: System Security Requirements](https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards)
- [ISO/IEC 27001:2013](https://www.iso.org/standard/54534.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Git Security Best Practices](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
