# 小说平台全栈工程（番茄小说级）

这是一个面向 H5 / APK / iOS 的小说阅读与创作平台全栈工程，后端使用 Django 5 + DRF，前端使用 Vue 3 + Vite + Tailwind，并已接入 Capacitor、AI 挂机写作 Worker、运营级 Django Admin 与生产部署文件。

## 当前完成度

- 已完成商用级 Web 前端
- 已完成 Capacitor 原生封装基建
- 已完成 AI 自动化写作 Worker
- 已完成审核后台与敏感词过滤
- 已完成生产部署编排与 Nginx 配置

## 技术栈

- Python 3.12
- Django 5
- Django REST Framework
- JWT 鉴权（SimpleJWT）
- PostgreSQL（主库）
- Redis（缓存与消息队列）
- Celery（异步任务基础）
- Docker + docker-compose（部署与联调）
- Vue 3 + Vite + TypeScript + Tailwind
- Capacitor（Android / iOS 打包）

## 目录结构

```text
xiaoshuo/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx.conf
├── .env.example
├── .env.prod.example
├── ai_author_bot.py
├── config/
├── apps/
└── web/                # Vue 3 H5 / 原生封装前端
```

## 1. 前端与原生封装

前端已接入 Capacitor，支持打包为 Android / iOS 原生容器。

### 本地开发

```bash
cd web
npm install
npm run dev
```

### 同步到原生工程

```bash
cd web
npm run cap:sync
```

### 打开 Android / iOS 工程

```bash
cd web
npm run cap:android
npm run cap:ios
```

### 原生适配说明

- 已处理 Safe Area 刘海屏适配
- 已配置 Splash Screen 与 Status Bar
- 已保留移动端底部 TabBar

## 2. AI 自动化写书 Worker

脚本位置：[ai_author_bot.py](ai_author_bot.py)

### 能力

- 同时兼容 OpenAI 风格 API 与 Ollama 本地接口
- 状态机流转：大纲 -> 章节任务 -> 生成正文 -> 发布 -> 休眠循环
- 上下文截断与重试退避
- 本地状态持久化，可中断恢复

### 启动示例

```bash
export LLM_PROVIDER=openai
export LLM_API_KEY=your_key
export BACKEND_PUBLISH_TOKEN=demo-writer-token
python3 ai_author_bot.py
```

Ollama 模式：

```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://127.0.0.1:11434
python3 ai_author_bot.py
```

## 3. 审核后台

- 已引入现代化 Django Admin 主题（Unfold）
- 运营工作台支持小说、章节、评论的批量通过 / 批量驳回
- 保存时已加入敏感词 / 违规词正则拦截

## 4. 生产部署

### 生产环境变量

```bash
cp .env.prod.example .env.prod
```

### 前端构建

```bash
cd web
npm ci
npm run build
```

### 生产部署启动

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 常用命令

```bash
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## 5. 快速启动（本地）

1. 安装依赖

```bash
pip3 install -r requirements.txt
```

2. 启动 PostgreSQL 与 Redis（推荐 Docker）

```bash
docker compose up -d db redis
```

3. 迁移数据库

```bash
POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=xiaoshuo POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres REDIS_HOST=localhost REDIS_PORT=6379 python3 manage.py migrate
```

4. 启动开发服务

```bash
POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=xiaoshuo POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres REDIS_HOST=localhost REDIS_PORT=6379 python3 manage.py runserver 0.0.0.0:8000
```

5. 健康检查

```bash
curl http://127.0.0.1:8000/api/health
```

## 6. Docker 一键启动（完整）

1. 复制环境变量

```bash
cp .env.example .env
```

2. 启动服务

```bash
docker compose up -d --build
```

## 7. API 总览（v1）

### 系统接口

- GET /api/health
- GET /api/schema/
- GET /api/docs/

### 用户系统

- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- GET /api/v1/users/me
- PATCH /api/v1/users/me

### 内容系统

- GET /api/v1/novels
- GET /api/v1/novels/{id}
- GET /api/v1/novels/rankings
- GET /api/v1/novels/{novel_id}/chapters
- GET /api/v1/novels/{novel_id}/chapters/{id}

### 书架系统

- GET /api/v1/bookshelf
- POST /api/v1/bookshelf
- PATCH /api/v1/bookshelf/{id}
- DELETE /api/v1/bookshelf/{id}
- POST /api/v1/bookshelf/{id}/sync-progress

### 交互系统

- GET /api/v1/comments
- POST /api/v1/comments
- POST /api/v1/ratings
- GET /api/v1/urge-updates
- POST /api/v1/urge-updates

### OpenAI 兼容创作发布

- POST /api/v1/completions

说明：

- 支持 Authorization: Bearer <JWT 或静态 API Key>
- 指令通过 messages 内 system 角色内容识别：
	- ACTION: CREATE_NOVEL
	- ACTION: ADD_CHAPTER
- 通过该接口创建的小说与章节默认进入待审核状态（pending）

## 8. 验收建议流程

1. 启动开发环境或生产环境
2. 打开 H5 首页、详情页、阅读器、书架、创作中心
3. 使用 AI Worker 自动生成并发布待审核内容
4. 在 Django Admin 中审核通过小说与章节
5. 验证 APK / iOS 容器打包入口是否可正常同步与打开

## 9. 相关文档

- [web/README.md](web/README.md) - 前端与 Capacitor 说明
- [ai_author_bot.py](ai_author_bot.py) - AI 挂机写作脚本
- [docker-compose.prod.yml](docker-compose.prod.yml) - 生产编排
- [nginx.conf](nginx.conf) - Nginx 配置

## OpenAI 兼容请求示例

### 创建书籍

```bash
curl -X POST http://127.0.0.1:8000/api/v1/completions \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer demo-writer-token" \
	-d '{
		"model": "gpt-4o-mini",
		"creator_id": 1,
		"messages": [
			{"role": "system", "content": "ACTION: CREATE_NOVEL"},
			{"role": "user", "content": "{\"title\":\"星海余烬\",\"summary\":\"一场跨星系求生\",\"category\":\"科幻\"}"}
		]
	}'
```

### 添加章节

```bash
curl -X POST http://127.0.0.1:8000/api/v1/completions \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer demo-writer-token" \
	-d '{
		"model": "gpt-4o-mini",
		"creator_id": 1,
		"messages": [
			{"role": "system", "content": "ACTION: ADD_CHAPTER"},
			{"role": "user", "content": "{\"novel_id\":1,\"title\":\"第一章 雨夜来客\",\"content\":\"正文内容...\"}"}
		]
	}'
```

## 数据审核与展示规则

- 小说公开列表仅返回 review_status=approved
- 章节读取仅返回 review_status=approved 且满足发布时间条件
- OpenAI 兼容发布入口写入数据默认 pending，前台不可见

## 明早 9 点验收建议流程

1. 执行 docker compose up -d --build
2. 访问 /api/health、/api/docs/
3. 注册账号并登录拿 JWT
4. 调用 novels 列表、章节读取、书架同步接口
5. 调用 /api/v1/completions 验证 CREATE_NOVEL 与 ADD_CHAPTER
6. 在 Django Admin 中核对 pending 审核状态