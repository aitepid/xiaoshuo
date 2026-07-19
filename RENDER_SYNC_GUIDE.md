# 🚀 Render 数据库同步指南

由于本地开发环境和 Render 生产环境使用不同的数据库实例，生成的小说数据需要额外步骤来同步到 Render。

## 方式 1：API 端点初始化（推荐）⭐

**无需 SSH 访问，直接通过 HTTP 请求初始化**

### 本地测试
```bash
curl -X POST http://127.0.0.1:8000/api/v1/categories/init-demo/
```

### Render 生产环境
在任何 HTTP 客户端（如 Postman、curl、JavaScript fetch）中：

```bash
curl -X POST https://xiaoshuo-api.onrender.com/api/v1/categories/init-demo/
```

**响应示例：**
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

### 使用 JavaScript 初始化
```javascript
fetch('https://xiaoshuo-api.onrender.com/api/v1/categories/init-demo/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log('✅ 数据初始化完成!', data))
.catch(err => console.error('❌ 初始化失败:', err))
```

## 方式 2：Django 管理命令

如果有 Render 的 SSH 访问权限：

### 通过 Render Shell 执行
```bash
# 在 Render Dashboard 中打开 Shell
python manage.py init_demo_novels --chapters 3000
```

## 方式 3：批量导出导入

### 1. 本地导出
```bash
python manage.py dumpdata novels bookshelf interactions users --indent 2 > data_export.json
```

### 2. 上传到 Render
```bash
# 将文件复制到 Render（需要 Render 上有适当的接收端点）
scp data_export.json user@render-server:/app/
```

### 3. Render 导入
```bash
python manage.py loaddata data_export.json
```

## 方式 4：数据库直接连接

### 获取 Render 数据库凭证
1. 登录 Render Dashboard
2. 找到 PostgreSQL 服务
3. 复制连接字符串

### 使用 psql 连接
```bash
psql "postgresql://user:password@host:5432/xiaoshuo"
```

## 数据同步后验证

### 查看创建的小说
```bash
curl https://xiaoshuo-api.onrender.com/api/v1/novels/
```

### 检查分类
```bash
curl https://xiaoshuo-api.onrender.com/api/v1/categories/
```

### 前端验证
访问 https://xiaoshuo-web.onrender.com/ 并检查：
- ✅ 首页是否显示小说列表
- ✅ 分类导航是否显示全部分类
- ✅ 可否筛选不同分类的小说
- ✅ 可否点击查看小说章节

## 常见问题

### Q: 为什么本地有数据但 Render 前端看不到？
**A:** 本地和 Render 使用不同的数据库实例。本地数据存储在本地 PostgreSQL，Render 有独立的数据库。需要使用上述方法将数据同步到 Render。

### Q: 初始化 API 需要认证吗？
**A:** 不需要。为了演示方便，此端点允许匿名访问。生产环境中应添加 API 密钥认证。

### Q: 能否多次调用初始化端点？
**A:** 可以。端点使用 `get_or_create()` 逻辑，多次调用不会重复创建已存在的小说。

### Q: 初始化需要多长时间？
**A:** 创建 33,000 章的内容通常需要 2-5 分钟，具体取决于 Render 的服务器性能。

### Q: 如何查看初始化进度？
**A:** 可以在 Render Dashboard 中查看日志：
- Backend 日志会显示创建进度
- 或查询数据库中已创建的章节数

```bash
# 在 Render Shell 中检查
python manage.py shell
```

```python
from apps.novels.models import Novel, Chapter
# 查看小说数量
print(f"小说: {Novel.objects.filter(author__username='comedian_author').count()}")
# 查看章节数量
print(f"章节: {Chapter.objects.filter(novel__author__username='comedian_author').count()}")
```

## 脚本参考

### 本地同步脚本
```bash
# 方式 1: 管理命令
python manage.py init_demo_novels --chapters 3000

# 方式 2: Python 脚本
python sync_local_to_db.py

# 方式 3: Django Shell
python manage.py shell < sync_local_to_db.py
```

## 下一步

数据同步完成后：

1. **验证 API** - 检查 `/api/v1/novels/` 返回数据
2. **测试前端** - 访问 https://xiaoshuo-web.onrender.com/
3. **清理本地** - 可选：`rm -f data_export.json novels_data.json`
4. **监控日志** - Render Dashboard 中监控错误日志

## 相关资源

- [Render 文档 - PostgreSQL](https://render.com/docs/postgresql)
- [Render 文档 - Shell Access](https://render.com/docs/shell-access)
- [Django 管理命令](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)
