# 本地开发环境网络问题解决方案

## 问题诊断
你的环境无法解析 `db.vbdzzryvrsqpmdrkhvxr.supabase.co` 的DNS，这通常是由以下原因造成的：

1. **网络限制**: 公司/学校网络阻止访问外部数据库
2. **DNS设置**: 当前DNS服务器无法解析Supabase域名
3. **防火墙**: 本地防火墙阻止数据库连接
4. **代理设置**: 网络代理配置问题

## 解决方案

### 方案1: 使用本地SQLite数据库进行开发

创建一个本地开发配置，在部署到Vercel时再使用Supabase：

```python
# src/main.py 修改数据库配置部分
import os
from dotenv import load_dotenv

load_dotenv()

# 检查是否为本地开发环境
IS_LOCAL_DEV = os.getenv('LOCAL_DEV', 'false').lower() == 'true'

if IS_LOCAL_DEV:
    # 本地开发使用SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_notes.db'
    print("Using local SQLite database for development")
else:
    # 生产环境使用Supabase
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError("DATABASE_URL not set for production")
    
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    if 'sslmode=' not in db_url:
        db_url += ('&' if '?' in db_url else '?') + 'sslmode=require'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    print(f"Using Supabase database: {db_url}")
```

### 方案2: 更换DNS服务器

尝试更换为公共DNS服务器：
- Google DNS: 8.8.8.8, 8.8.4.4
- Cloudflare DNS: 1.1.1.1, 1.0.0.1

### 方案3: 使用VPN或代理

如果网络有限制，可以尝试使用VPN连接。

### 方案4: 联系网络管理员

如果在公司或学校网络，联系IT部门开放对Supabase的访问权限。

## 推荐使用方案1

对于本地开发，建议使用SQLite，生产环境使用Supabase。这样可以避免网络问题影响开发。