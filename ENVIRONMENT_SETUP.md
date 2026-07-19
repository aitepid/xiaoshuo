# 🔧 环境配置指南 - Agnes 智能体启动必需

## 📌 概述

Agnes 智能体系统需要以下几个关键环境变量才能正常启动。本文档详细说明了所有必需和可选的配置。

---

## 🎯 核心需求

### ✅ 必需的环境变量（Agnes 无法启动而不设置这些）

#### 1️⃣ 后端环境变量

| 变量名 | 说明 | 例值 | 优先级 |
|-------|------|------|--------|
| **ANTHROPIC_API_KEY** | Anthropic Claude API 密钥（Agnes AI 核心） | `sk-ant-...` | ⭐⭐⭐⭐⭐ **必需** |
| DJANGO_DEBUG | Django 调试模式 | `True` / `False` | ⭐⭐ 重要 |
| DJANGO_SECRET_KEY | Django 密钥 | 长随机字符串 | ⭐⭐ 重要 |
| POSTGRES_* | 数据库连接 | 见下表 | ⭐⭐⭐ 重要 |
| REDIS_* | Redis 连接 | 见下表 | ⭐⭐ 重要 |

#### 2️⃣ 前端环境变量

| 变量名 | 说明 | 例值 | 优先级 |
|-------|------|------|--------|
| VITE_API_BASE_URL | 后端 API 地址 | `http://127.0.0.1:8000/api/v1` | ⭐⭐⭐ 重要 |

---

## 📋 详细配置

### 开发环境（本地）

#### 后端 - 创建 `/workspaces/xiaoshuo/.env` 文件

```bash
# === Django 核心配置 ===
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key-change-in-production-12345
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*.ngrok.io

# === 数据库配置 ===
POSTGRES_DB=xiaoshuo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# === Redis 缓存配置 ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# === JWT 认证配置 ===
JWT_ACCESS_TOKEN_MINUTES=120
JWT_REFRESH_TOKEN_DAYS=7

# === CORS 跨域配置 ===
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# === 现有 API 配置 ===
OPENAI_COMPAT_API_KEYS=demo-writer-token

# === 🤖 Agnes 智能体配置 ===
# ⭐ 最重要：从 https://console.anthropic.com 获取 API 密钥
ANTHROPIC_API_KEY=sk-ant-abc123xyz789...

# Agnes 可选配置
AGNES_INTERVAL_MINUTES=30
AGNES_AUTO_PUBLISH=true
```

#### 前端 - 更新 `/workspaces/xiaoshuo/web/.env` 文件

```bash
# 开发环境 - 本地 API 地址
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

---

### 生产环境（Render）

#### 后端 - 在 Render Dashboard 设置环境变量

1. 访问 Render Dashboard → Services → 选择后端服务
2. 点击 "Environment" 标签
3. 添加以下环境变量：

```bash
# === Django 配置 ===
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=generate-a-long-random-secret-key-here-12345
DJANGO_ALLOWED_HOSTS=xiaoshuo-ng79.onrender.com,xiaoshuo-web.onrender.com

# === 数据库配置（通常由 Render 自动提供）===
POSTGRES_DB=xiaoshuo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=postgres-host.render.internal
POSTGRES_PORT=5432

# === Redis 配置（通常由 Render 自动提供）===
REDIS_HOST=redis-host.render.internal
REDIS_PORT=6379
REDIS_DB=0

# === CORS 跨域配置 ===
CORS_ALLOWED_ORIGINS=https://xiaoshuo-web.onrender.com

# === JWT 认证配置 ===
JWT_ACCESS_TOKEN_MINUTES=120
JWT_REFRESH_TOKEN_DAYS=7

# === 现有 API 配置 ===
OPENAI_COMPAT_API_KEYS=production-writer-token

# === 🤖 Agnes 智能体配置（必需）===
ANTHROPIC_API_KEY=sk-ant-your-production-api-key-here

# Agnes 配置
AGNES_INTERVAL_MINUTES=30
AGNES_AUTO_PUBLISH=true
```

#### 前端 - 使用 `/workspaces/xiaoshuo/web/.env.production` 文件

```bash
# 生产环境 - Render 上的后端 API 地址
VITE_API_BASE_URL=https://xiaoshuo-ng79.onrender.com/api/v1
```

---

## 🔑 获取 ANTHROPIC_API_KEY

这是 Agnes 正常工作的唯一必需的关键密钥。

### 步骤 1：创建 Anthropic 账户

1. 访问 [Anthropic 官网](https://www.anthropic.com)
2. 登录或创建账户
3. 验证电子邮件

### 步骤 2：获取 API 密钥

1. 访问 [Anthropic Console](https://console.anthropic.com)
2. 点击左侧 "API Keys"
3. 点击 "Create Key" 按钮
4. 复制生成的密钥（格式：`sk-ant-...`）

### 步骤 3：设置到环境变量

**本地开发：**
```bash
# 方式 1：写入 .env 文件
echo 'ANTHROPIC_API_KEY=sk-ant-your-key-here' >> .env

# 方式 2：export 到当前 shell
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 方式 3：写入 .bashrc 或 .zshrc 永久保存
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

**Render 生产环境：**
1. Render Dashboard → Services → Backend Service
2. Environment 标签
3. 添加变量 `ANTHROPIC_API_KEY`
4. 粘贴密钥值
5. 保存并重启服务

---

## ✅ 验证配置

### 本地验证

```bash
# 1. 检查 ANTHROPIC_API_KEY 是否设置
echo $ANTHROPIC_API_KEY
# 输出应该显示 sk-ant-...

# 2. 验证后端可以加载配置
python manage.py shell << 'EOF'
import os
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print(f"✓ ANTHROPIC_API_KEY 已设置: {api_key[:10]}...")
else:
    print("✗ ANTHROPIC_API_KEY 未设置")
EOF

# 3. 验证 Agnes 模块可以初始化
python manage.py shell << 'EOF'
from apps.ai_content_generator import AIContentGenerator
try:
    gen = AIContentGenerator()
    print("✓ AIContentGenerator 已初始化")
except ValueError as e:
    print(f"✗ 错误: {e}")
EOF

# 4. 测试 API 连接
curl http://127.0.0.1:8000/api/v1/agnes/status/
# 应该返回成功的 JSON 响应
```

### 生产环境验证

```bash
# 1. 检查 Render 环境变量
# 在 Render Dashboard 中查看 Environment 标签确认所有变量都已设置

# 2. 查看 Render 构建日志
# 确保没有 "ANTHROPIC_API_KEY 未设置" 的错误

# 3. 测试生产 API
curl https://xiaoshuo-ng79.onrender.com/api/v1/agnes/status/
# 应该返回成功的 JSON 响应
```

---

## 🚀 启动 Agnes

验证配置后，执行以下命令启动 Agnes：

### 本地开发

```bash
# 方式 1：立即执行一次任务
python manage.py start_agnes --now

# 方式 2：启动定时任务（每 30 分钟）
python manage.py start_agnes --interval 30

# 方式 3：立即执行并启动定时任务
python manage.py start_agnes --now --interval 30
```

### Render 生产环境

1. **第一次启动** - 在 Render 中执行初始化命令

2. **持续运行** - 两种选择：
   - 选项 A：使用后台工作进程
   - 选项 B：使用 Cron Job（Render 中的 Cron 服务）

---

## 📊 环境变量完整参考表

### 后端变量

| 变量 | 默认值 | 说明 | 必需 |
|------|--------|------|------|
| DJANGO_DEBUG | True | 调试模式 | ✓ |
| DJANGO_SECRET_KEY | dev-secret | Django 密钥 | ✓ |
| DJANGO_ALLOWED_HOSTS | * | 允许的主机 | ✓ |
| CORS_ALLOWED_ORIGINS | - | 跨域源 | ✓ |
| POSTGRES_DB | xiaoshuo | 数据库名 | ✓ |
| POSTGRES_USER | postgres | 数据库用户 | ✓ |
| POSTGRES_PASSWORD | postgres | 数据库密码 | ✓ |
| POSTGRES_HOST | localhost | 数据库主机 | ✓ |
| POSTGRES_PORT | 5432 | 数据库端口 | ✓ |
| REDIS_HOST | localhost | Redis 主机 | ✓ |
| REDIS_PORT | 6379 | Redis 端口 | ✓ |
| REDIS_DB | 0 | Redis 数据库 | ✓ |
| JWT_ACCESS_TOKEN_MINUTES | 120 | Token 有效期 | ○ |
| JWT_REFRESH_TOKEN_DAYS | 7 | 刷新 Token 有效期 | ○ |
| OPENAI_COMPAT_API_KEYS | - | API 兼容密钥 | ○ |
| **ANTHROPIC_API_KEY** | - | Claude API 密钥 | **⭐ 必需** |
| AGNES_INTERVAL_MINUTES | 30 | Agnes 执行间隔 | ○ |
| AGNES_AUTO_PUBLISH | true | 自动发布生成的小说 | ○ |

### 前端变量

| 变量 | 默认值 | 说明 | 必需 |
|------|--------|------|------|
| VITE_API_BASE_URL | http://127.0.0.1:8000/api/v1 | API 地址 | ○ |

---

## 🐛 常见问题

### Q1：启动 Agnes 时报错 "ANTHROPIC_API_KEY 未设置"

**原因**：环境变量未正确设置

**解决**：
```bash
# 检查是否设置
echo $ANTHROPIC_API_KEY

# 如果为空，立即设置
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 验证设置
echo $ANTHROPIC_API_KEY
```

### Q2：本地开发能运行，但 Render 上无法生成小说

**原因**：Render 上的 ANTHROPIC_API_KEY 未设置

**解决**：
1. Render Dashboard → Services → Backend
2. Environment 标签
3. 检查 ANTHROPIC_API_KEY 是否存在
4. 如果不存在，添加后重启服务

### Q3：前端无法连接到后端 API

**原因**：VITE_API_BASE_URL 配置不正确

**解决**：
```bash
# 本地开发
echo 'VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1' > web/.env

# Render 生产
echo 'VITE_API_BASE_URL=https://xiaoshuo-ng79.onrender.com/api/v1' > web/.env.production
```

### Q4：如何更改 Agnes 的执行间隔（不是 30 分钟）

**解决**：
```bash
# 方式 1：启动时指定
python manage.py start_agnes --interval 60

# 方式 2：设置环境变量
export AGNES_INTERVAL_MINUTES=60
python manage.py start_agnes

# 方式 3：在 .env 中设置
echo 'AGNES_INTERVAL_MINUTES=60' >> .env
```

### Q5：需要备用 API 密钥

**解决**：
1. 在 Anthropic Console 创建第二个密钥
2. 更新环境变量
3. 重启 Agnes 服务

---

## 🔒 安全建议

### ⚠️ 不要做这些事

- ❌ 不要在代码中硬编码 API 密钥
- ❌ 不要将 .env 文件提交到 Git
- ❌ 不要在公开的地方分享你的 API 密钥
- ❌ 不要在日志中打印完整的 API 密钥

### ✅ 安全实践

- ✓ 使用 .env 文件管理敏感信息
- ✓ 定期轮换 API 密钥
- ✓ 使用强密码和复杂的 SECRET_KEY
- ✓ 在生产环境使用密钥管理服务
- ✓ 监控 API 使用情况和账单

---

## 📝 .gitignore 检查

确保 .gitignore 包含以下条目以保护敏感信息：

```bash
# .gitignore

# 环境变量文件
.env
.env.local
.env.*.local
.env.prod

# 不包括示例文件
# .env.example
# .env.prod.example
```

---

## 📞 故障排查流程

如果 Agnes 无法启动，按以下步骤排查：

1. **检查 ANTHROPIC_API_KEY**
   ```bash
   echo $ANTHROPIC_API_KEY
   # 应该输出 sk-ant-...
   ```

2. **检查其他关键变量**
   ```bash
   python manage.py shell -c "
   import os
   print(f'DEBUG={os.getenv(\"DJANGO_DEBUG\")}')
   print(f'DB={os.getenv(\"POSTGRES_DB\")}')
   print(f'ANTHROPIC_API_KEY={'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}')"
   ```

3. **检查数据库连接**
   ```bash
   python manage.py dbshell
   # 应该能进入 PostgreSQL
   ```

4. **检查 Agnes 模块**
   ```bash
   python manage.py shell -c "
   from apps.agnes_agent import get_agnes_agent
   agent = get_agnes_agent()
   print('✓ Agnes 已初始化')"
   ```

5. **查看详细日志**
   ```bash
   python manage.py start_agnes --now 2>&1 | head -50
   ```

---

## 🎉 配置完成检查清单

- [ ] ANTHROPIC_API_KEY 已获取并设置
- [ ] .env 文件已创建并配置
- [ ] VITE_API_BASE_URL 已配置
- [ ] 数据库配置正确
- [ ] Redis 配置正确
- [ ] 本地验证通过
- [ ] 能成功启动 Agnes（`python manage.py start_agnes --now`）
- [ ] Render 环境变量已设置（生产环境）
- [ ] 生产环境验证通过

---

**现在您已经准备好启动 Agnes 了！🚀**

```bash
# 最后一步：启动 Agnes
python manage.py start_agnes --now
```
