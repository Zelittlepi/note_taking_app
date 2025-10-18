# Vercel 部署指南

这个笔记应用已经适配了 Vercel 部署，使用 Supabase PostgreSQL 作为数据库。

## 部署前准备

### 1. 确保代码已推送到 GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. 准备环境变量
在 Supabase 控制台获取数据库连接字符串：
- 进入你的 Supabase 项目
- 导航到 Settings -> Database
- 复制 Connection string (Direct connection)
- 格式类似：`postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres`

## Vercel 部署步骤

### 1. 登录 Vercel
- 访问 [vercel.com](https://vercel.com)
- 使用 GitHub 账号登录

### 2. 导入项目
- 点击 "New Project"
- 选择你的 GitHub 仓库 `note_taking_app`
- 点击 "Import"

### 3. 配置项目设置
在部署配置页面：
- **Framework Preset**: 选择 "Other" 或保持默认
- **Root Directory**: 保持默认 (/) 
- **Build and Output Settings**: 保持默认
- 点击 "Deploy" 开始部署

### 4. 配置环境变量
部署完成后，进入项目设置：
- 进入项目仪表板
- 点击 "Settings" 标签
- 点击 "Environment Variables"
- 添加以下环境变量：

| Name | Value |
|------|-------|
| `DATABASE_URL` | `postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres` |
| `OPENAI_API_KEY` | `sk-your-openai-api-key` (可选，用于翻译和补全功能) |
| `SECRET_KEY` | `your-random-secret-key` (可选) |

### 5. 重新部署
添加环境变量后：
- 进入 "Deployments" 标签
- 点击最新部署右侧的 "..." 菜单
- 选择 "Redeploy"

## 验证部署

1. **访问应用**: 使用 Vercel 提供的 URL (如 `https://your-app.vercel.app`)
2. **测试功能**:
   - 创建新笔记
   - 搜索笔记
   - 测试翻译功能 (如果配置了 OpenAI)
   - 测试自动补全功能

## 项目结构说明

```
├── api/
│   └── index.py          # Vercel 入口文件
├── src/
│   ├── models/           # 数据模型
│   ├── routes/           # API 路由
│   ├── static/           # 静态文件 (HTML/CSS/JS)
│   └── utils/            # 工具函数
├── vercel.json           # Vercel 配置
├── requirements.txt      # Python 依赖
└── .env.example         # 环境变量示例
```

## 故障排除

### 1. 数据库连接失败
- 检查 `DATABASE_URL` 是否正确
- 确保 Supabase 项目正在运行
- 验证密码和项目 ID

### 2. 静态文件 404
- 确保 `src/static/` 目录包含 `index.html`
- 检查 Vercel 构建日志

### 3. API 路由不工作
- 检查 `api/index.py` 是否正确导入所有路由
- 查看 Vercel 函数日志

### 4. 环境变量问题
- 确保所有必需的环境变量都已设置
- 重新部署以应用新的环境变量

## 本地开发

继续本地开发：
```bash
# 安装依赖
pip install -r requirements.txt

# 运行本地服务器
python src/main.py
# 或者使用 Vercel 函数格式
python api/index.py
```

## 自定义域名 (可选)

在 Vercel 项目设置中：
1. 点击 "Domains" 标签
2. 添加你的自定义域名
3. 按照说明配置 DNS 记录

## 监控和日志

- **实时日志**: Vercel 仪表板 -> Functions 标签
- **分析**: Vercel 仪表板 -> Analytics 标签
- **性能**: 查看函数执行时间和错误率