# 🚀 Render 注册和初始化完整指南

## 问题诊断

如果前端注册失败，请按以下步骤诊断和解决：

### 1️⃣ 检查 API 连接

访问诊断工具：
- **Render 前端**: https://xiaoshuo-web.onrender.com/debug-register.html
- **本地前端**: http://127.0.0.1:5173/debug-register.html

点击「检查 API 连接」按钮，查看输出日志：
- ✓ API 连接正常 → 继续下一步
- ✗ API 连接失败 → 检查后端是否已部署

### 2️⃣ 测试注册流程

在诊断工具中：
1. 填写注册表单（邮箱和用户名会自动添加时间戳以保证唯一性）
2. 点击「测试注册」按钮
3. 查看日志输出

**常见错误解决：**

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| CORS 错误 | 跨域请求被拒绝 | 等待 Render 重新部署（已修复） |
| 网络错误 | 无法连接到后端 | 检查后端 API 地址是否正确 |
| 注册失败 (400) | 数据验证失败 | 查看错误信息中的具体字段 |
| 邮箱已存在 | 邮箱被占用 | 使用不同的邮箱地址 |

---

## 数据初始化步骤

### 步骤 1: 初始化演示小说数据

访问以下 URL 初始化数据库（仅需一次）：

```bash
# Render 生产环境
curl -X POST https://xiaoshuo-ng79.onrender.com/api/v1/categories/init-demo/

# 或在浏览器中访问
https://xiaoshuo-ng79.onrender.com/api/v1/categories/init-demo/
```

**期望响应：**
```json
{
  "status": "success",
  "message": "创建了 11 部小说，33000 章内容",
  "data": {
    "novels_created": 11,
    "chapters_created": 33000,
    "total_words": 66000000
  }
}
```

### 步骤 2: 创建作者账号

使用诊断工具中的注册表单，创建一个作者账号：

1. 访问：https://xiaoshuo-web.onrender.com/debug-register.html
2. 填写注册表单
3. 选择身份为「作者」
4. 点击「测试注册」

**也可以在前端注册页面注册：**
https://xiaoshuo-web.onrender.com/auth/register

### 步骤 3: 验证前端显示

1. 访问前端首页：https://xiaoshuo-web.onrender.com/
2. 应该看到：
   - ✓ 小说列表已加载
   - ✓ 分类导航显示 12 个分类
   - ✓ 可以按分类筛选小说
   - ✓ 可以点击小说查看详情和章节

---

## API 端点参考

| 功能 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 初始化数据 | POST | `/api/v1/categories/init-demo/` | 创建演示小说（只需一次） |
| 用户注册 | POST | `/api/v1/auth/register` | 创建新账号 |
| 用户登录 | POST | `/api/v1/auth/login` | 用户登录获取 Token |
| 查看分类 | GET | `/api/v1/categories/` | 获取所有分类 |
| 查看小说 | GET | `/api/v1/novels/` | 获取小说列表 |
| 小说详情 | GET | `/api/v1/novels/{id}/` | 获取单部小说详情 |
| 查看章节 | GET | `/api/v1/novels/{id}/chapters/` | 获取章节列表 |
| 系统诊断 | GET | `/api/diagnostics` | 诊断系统配置 |
| 健康检查 | GET | `/api/health` | 检查服务健康状态 |

---

## 环境部署说明

### Render 后端配置

**关键环境变量：**
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=xiaoshuo-ng79.onrender.com
CORS_ALLOWED_ORIGINS=https://xiaoshuo-web.onrender.com

POSTGRES_DB=xiaoshuo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432

REDIS_HOST=your-redis-host
REDIS_PORT=6379
```

### Render 前端配置

**构建命令：**
```bash
npm ci && npm run build
```

**启动命令：**
```bash
npm run preview
```

或使用静态文件服务（推荐）：
```bash
cd dist && npx serve -l 3000
```

---

## 故障排查

### 问题：前端注册页面无响应

**症状：**
- 点击注册按钮无反应
- 浏览器控制台无错误

**解决：**
1. 检查网络连接
2. 打开浏览器开发者工具（F12）
3. 在 Network 选项卡中查看请求
4. 检查请求是否被发送到正确的 API 地址

### 问题：CORS 错误

**症状：**
```
Access to XMLHttpRequest at 'https://...' from origin 'https://...'
has been blocked by CORS policy
```

**解决：**
1. 等待 Render 重新部署（已在代码中修复）
2. 检查后端 `CORS_ALLOWED_ORIGINS` 配置
3. 验证前端 URL 与 CORS 配置中的 URL 一致

### 问题：API 返回 404

**症状：**
```json
{"detail": "Not found."}
```

**解决：**
1. 检查 API 端点 URL 是否正确
2. 查看后端路由配置
3. 检查后端是否已启动

### 问题：数据库连接失败

**症状：**
- 诊断工具显示"500 Internal Server Error"
- 后端日志显示数据库连接错误

**解决：**
1. 验证数据库凭证
2. 检查数据库是否已启动
3. 在 Render Dashboard 中检查 PostgreSQL 服务状态

---

## 本地开发设置

### 1. 启动后端服务

```bash
cd /workspaces/xiaoshuo
python manage.py migrate  # 创建数据库表
python manage.py init_demo_novels  # 初始化数据
python manage.py runserver 0.0.0.0:8000
```

### 2. 启动前端开发服务器

```bash
cd web
npm install
npm run dev
```

### 3. 访问

- 前端：http://127.0.0.1:5173/
- 后端 API：http://127.0.0.1:8000/api/v1/
- 诊断工具：http://127.0.0.1:5173/debug-register.html

---

## 检查清单

部署完成前，确认以下所有项目：

- [ ] 后端 API 已部署到 Render
- [ ] 前端已部署到 Render
- [ ] CORS 配置正确（已自动配置）
- [ ] 数据库已初始化（运行 `/api/v1/categories/init-demo/`）
- [ ] 前端可正确连接到后端 API
- [ ] 用户注册流程正常
- [ ] 小说列表在前端显示
- [ ] 分类导航可正常使用
- [ ] 可点击小说查看详情

---

## 实时监控

### 查看 Render 日志

1. 登录 Render Dashboard
2. 选择对应的服务（前端或后端）
3. 点击「Logs」查看实时日志
4. 查看构建日志、部署日志、运行日志

### 常见日志信息

**后端成功启动：**
```
Starting gunicorn application server
Listening on 0.0.0.0:10000
Application startup complete
```

**前端成功构建：**
```
✓ built in 2.5s
```

---

## 联系方式

如遇问题，请查看：
- GitHub Issues: https://github.com/aitepid/xiaoshuo/issues
- 项目文档: https://github.com/aitepid/xiaoshuo
