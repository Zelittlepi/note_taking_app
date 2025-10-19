# 网络问题解决方案

## 问题总结
你的开发环境遇到了以下网络问题：
1. 无法连接到Supabase数据库（DNS解析失败）
2. 无法从PyPI安装Python包（SSL连接问题）

这通常是因为网络环境限制（公司/学校防火墙、代理设置等）。

## 解决方案

### 方案1: 使用本地SQLite开发（推荐）

我已经为你创建了 `local_dev_server.py`，这是一个纯本地的开发服务器：

1. **安装基础依赖**（如果还没有Flask）:
   ```bash
   pip install flask flask-cors
   ```

2. **运行本地服务器**:
   ```bash
   python local_dev_server.py
   ```

3. **特点**:
   - 使用SQLite数据库（无需网络连接）
   - 包含所有CRUD功能
   - 简化版翻译和补全（显示占位符）
   - 自动创建数据库表

### 方案2: 配置网络环境

如果需要使用完整功能：

1. **配置代理**（如果在公司网络）:
   ```bash
   pip install --proxy http://proxy-server:port package-name
   ```

2. **更换DNS服务器**:
   - Windows: 控制面板 -> 网络设置 -> 更改适配器设置
   - 设置DNS为 8.8.8.8 和 8.8.4.4

3. **联系网络管理员**开放以下域名访问权限:
   - *.supabase.co (Supabase数据库)
   - pypi.org (Python包安装)

### 方案3: 部署到Vercel测试

即使本地有网络问题，你仍然可以：

1. **推送代码到GitHub**:
   ```bash
   git add .
   git commit -m "Add local dev support"
   git push origin main
   ```

2. **在Vercel部署**:
   - Vercel的服务器没有你本地的网络限制
   - 可以正常连接到Supabase
   - 部署后测试完整功能

## 推荐工作流程

1. **本地开发**: 使用 `local_dev_server.py` 进行基本功能开发
2. **功能测试**: 推送到GitHub，在Vercel部署测试完整功能
3. **生产部署**: 配置好环境变量后正式发布

## 快速开始本地开发

```bash
# 1. 确保有基础Flask
python -c "import flask" 2>/dev/null || echo "需要安装: pip install flask flask-cors"

# 2. 运行本地服务器
python local_dev_server.py

# 3. 访问 http://localhost:5001
```

这样你就可以在不解决网络问题的情况下继续开发了！