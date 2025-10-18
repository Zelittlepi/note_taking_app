import os
import re
import sys
import socket
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# =====================
# 1. Load .env file
# =====================

# 尝试从项目根目录的 .env 加载（可选，可根据需要启用）
# root_env_path = Path(__file__).resolve().parents[1] / '.env'
# if root_env_path.exists():
#     load_dotenv(root_env_path)

# 优先从当前目录的 .env 加载
load_dotenv()

# =====================
# 2. 从环境变量获取数据库连接信息（支持多种方式）
# =====================

def get_database_url() -> str:
    # 方式 1：直接使用 DATABASE_URL（推荐，比如从 .env 中加载）
    db_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    if db_url:
        return db_url

    # 方式 2：手动拼接（备用，如果上面都没设置，尝试从 DB_* 环境变量构建）
    user = os.getenv('DB_USER')
    pwd = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    name = os.getenv('DB_NAME')

    if user and pwd and host and name:
        port_part = f":{port}" if port else ""
        return f"postgresql://{user}:{pwd}@{host}{port_part}/{name}"

    return None

def normalize_db_url(raw_url: str) -> str:
    """确保 URL 是 postgresql:// 协议，并带有 sslmode=require"""
    if raw_url.startswith('postgres://'):
        raw_url = raw_url.replace('postgres://', 'postgresql://', 1)
    if 'sslmode=' not in raw_url:
        separator = '&' if '?' in raw_url else '?'
        raw_url = f"{raw_url}{separator}sslmode=require"
    return raw_url

# =====================
# 3. DNS 解析检查
# =====================

def check_dns(host: str):
    print(f"🔍 正在检查 DNS 解析 for host: {host}")
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ DNS 解析成功: {host} → {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS 解析失败 for {host}: {e}")
        return False

# =====================
# 4. 数据库连接测试
# =====================

def test_db_connection(db_url: str):
    print("\n🚀 开始测试 PostgreSQL 数据库连接...")
    try:
        # 设置连接超时为 5 秒
        conn = psycopg2.connect(db_url, connect_timeout=5)
        cur = conn.cursor()

        # 执行一个简单查询以验证连接
        cur.execute("SELECT 1;")
        print("✅ 数据库连接成功，SELECT 1 返回:", cur.fetchone())

        # 可选：获取 PostgreSQL 版本
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print("🐘 PostgreSQL 版本:", version)

        # 可选：列出 public schema 下的表（最多前50个）
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name 
            LIMIT 50;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print("📄 Public 表（最多50个）:", tables)

        # 可选：如果你有 note 表，尝试查询行数
        if 'note' in tables:
            try:
                cur.execute("SELECT COUNT(*) AS cnt FROM note;")
                count = cur.fetchone()[0]
                print("📝 note 表的行数:", count)
            except Exception as e:
                print("⚠️ 无法查询 note 表:", e)

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("❌ 数据库连接失败:", e)
        return False

# =====================
# 5. 主函数
# =====================

def main():
    # 获取原始数据库连接字符串
    raw_url = get_database_url()
    if not raw_url:
        print("❌ 错误：未找到有效的 DATABASE_URL 或 DB_* 环境变量。", file=sys.stderr)
        print("   请确保在 .env 文件中设置了 DATABASE_URL，或者设置了 DB_USER / DB_PASSWORD / DB_HOST / DB_NAME", file=sys.stderr)
        sys.exit(1)

    # 标准化 URL（比如 postgres:// → postgresql://，添加 sslmode=require）
    db_url = normalize_db_url(raw_url)
    print(f"🔗 使用数据库连接字符串: {db_url}")

    # 解析主机名用于 DNS 检查
    parsed = urlparse(db_url)
    host = parsed.hostname
    if not host:
        print("❌ 错误：无法从连接字符串中解析出主机名（host）。请检查 DATABASE_URL 格式。", file=sys.stderr)
        sys.exit(1)

    # Step 1: 检查 DNS 是否可解析
    dns_ok = check_dns(host)
    if not dns_ok:
        print("⚠️  警告：DNS 解析失败，数据库连接可能仍然会失败，但继续尝试...", file=sys.stderr)

    # Step 2: 尝试连接数据库
    success = test_db_connection(db_url)
    if success:
        print("✅ 数据库测试通过！")
    else:
        print("❌ 数据库测试未通过，请检查连接参数、网络、防火墙、Supabase 权限等。", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()