# ⚡ Agnes 环境配置速查表

## 🎯 核心 - 三个必需的变量

### 后端配置（.env）

```bash
# 1️⃣ Agnes AI 核心密钥 ⭐⭐⭐⭐⭐ 最重要
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 2️⃣ 基础 Django 配置 ⭐⭐
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key

# 3️⃣ 数据库和 Redis（本地）⭐⭐
POSTGRES_DB=xiaoshuo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 前端配置（web/.env）

```bash
# 1️⃣ API 地址 ⭐⭐
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

---

## 🚀 一分钟快速启动

### 第 1 步：获取 API 密钥（5 分钟）

```bash
# 1. 访问 https://console.anthropic.com
# 2. 点击 "API Keys"
# 3. 点击 "Create Key"
# 4. 复制密钥（格式: sk-ant-...）
```

### 第 2 步：配置环境（1 分钟）

```bash
# 创建 .env 文件
cat > .env << 'EOF'
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=dev-secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

POSTGRES_DB=xiaoshuo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

ANTHROPIC_API_KEY=sk-ant-your-key-here
AGNES_INTERVAL_MINUTES=30
EOF

# 前端配置已经在 web/.env 中
```

### 第 3 步：启动 Agnes（1 分钟）

```bash
python manage.py start_agnes --now
```

---

## 📊 配置对照表

| 环境 | 配置位置 | ANTHROPIC_API_KEY | VITE_API_BASE_URL |
|------|--------|------------------|------------------|
| 本地开发 | `.env` | sk-ant-... | http://127.0.0.1:8000/api/v1 |
| 本地前端 | `web/.env` | - | http://127.0.0.1:8000/api/v1 |
| Render 后端 | Dashboard → Environment | sk-ant-... | - |
| Render 前端 | `web/.env.production` | - | https://xiaoshuo-ng79.onrender.com/api/v1 |

---

## ✅ 验证配置

```bash
# 1. 检查环境变量
echo $ANTHROPIC_API_KEY
# 应该输出: sk-ant-...

# 2. 检查 Agnes 可以初始化
python manage.py shell << 'EOF'
from apps.ai_content_generator import AIContentGenerator
gen = AIContentGenerator()
print("✓ Agnes 已准备就绪")
EOF

# 3. 检查 API 连接
curl http://127.0.0.1:8000/api/v1/agnes/status/
# 应该返回 JSON 响应
```

---

## 🎯 变量说明

### ANTHROPIC_API_KEY ⭐⭐⭐⭐⭐

- **用途**：Claude AI 模型的认证密钥
- **来源**：https://console.anthropic.com/api_keys
- **格式**：`sk-ant-` 开头的长字符串
- **必需**：是
- **有效期**：无限制
- **成本**：按 token 计费

### DJANGO_DEBUG

- **用途**：Django 调试模式
- **值**：`True`（开发） / `False`（生产）
- **必需**：是
- **影响**：影响错误页面和静态文件服务

### DJANGO_SECRET_KEY

- **用途**：Django 密钥，用于 CSRF、session 等
- **值**：长随机字符串
- **必需**：是
- **生成**：`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### VITE_API_BASE_URL

- **用途**：前端调用后端 API 的基础 URL
- **值**：后端 API 完整 URL
- **必需**：否（有自动检测）
- **自动检测**：
  - 本地：`http://127.0.0.1:8000/api/v1`
  - Render：自动识别 Render 域名

### POSTGRES_* 和 REDIS_*

- **用途**：数据库和缓存连接
- **必需**：是
- **默认值**：见 `.env.example`

---

## 🔒 安全检查清单

- [ ] ANTHROPIC_API_KEY 已设置并有效
- [ ] .env 文件在 .gitignore 中
- [ ] 生产环境使用不同的 SECRET_KEY
- [ ] 生产环境 DJANGO_DEBUG=False
- [ ] 定期检查 API 使用量和成本
- [ ] 备份好 API 密钥

---

## 🐛 快速排查

| 问题 | 原因 | 解决 |
|------|------|------|
| Agnes 无法启动 | ANTHROPIC_API_KEY 未设置 | `export ANTHROPIC_API_KEY=sk-ant-...` |
| 前端看不到 API | VITE_API_BASE_URL 错误 | 检查 `web/.env` 配置 |
| API 返回 401 | JWT Token 无效 | 重新登录 |
| 生成小说失败 | API 配额不足 | 检查 Anthropic 账户余额 |
| 定时任务不运行 | 进程未启动 | `python manage.py start_agnes` |

---

## 📌 重要命令速查

```bash
# 启动 Agnes 并立即执行一次
python manage.py start_agnes --now

# 启动定时任务
python manage.py start_agnes --interval 30

# 查看状态
curl http://127.0.0.1:8000/api/v1/agnes/status/

# 手动触发生成
curl -X POST http://127.0.0.1:8000/api/v1/agnes/generate-novel/

# 检查配置
python manage.py shell -c "import os; print(f'API_KEY={'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}')"
```

---

## 📚 详细文档

- [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - 完整环保置指南
- [AGNES_GUIDE.md](AGNES_GUIDE.md) - Agnes 使用手册
- [QUICK_START.md](QUICK_START.md) - 快速开始

---

**现在您拥有启动 Agnes 所需的一切！🚀**
