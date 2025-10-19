import socket
import os
from urllib.parse import urlparse

# 测试DNS解析
hostname = "db.vbdzzryvrsqpmdrkhvxr.supabase.co"
print(f"Testing DNS resolution for: {hostname}")

try:
    # 获取所有IP地址
    addr_info = socket.getaddrinfo(hostname, 5432, socket.AF_UNSPEC, socket.SOCK_STREAM)
    print("DNS解析成功:")
    for family, type, proto, canonname, sockaddr in addr_info:
        family_name = "IPv4" if family == socket.AF_INET else "IPv6"
        print(f"  {family_name}: {sockaddr[0]}")
    
    # 尝试IPv4连接
    ipv4_addresses = [info[4][0] for info in addr_info if info[0] == socket.AF_INET]
    if ipv4_addresses:
        ipv4_addr = ipv4_addresses[0]
        print(f"\n尝试连接到IPv4地址: {ipv4_addr}:5432")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((ipv4_addr, 5432))
            if result == 0:
                print("✓ IPv4连接成功")
            else:
                print(f"✗ IPv4连接失败，错误代码: {result}")
            sock.close()
        except Exception as e:
            print(f"✗ IPv4连接异常: {e}")
    
    # 尝试IPv6连接
    ipv6_addresses = [info[4][0] for info in addr_info if info[0] == socket.AF_INET6]
    if ipv6_addresses:
        ipv6_addr = ipv6_addresses[0]
        print(f"\n尝试连接到IPv6地址: {ipv6_addr}:5432")
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((ipv6_addr, 5432))
            if result == 0:
                print("✓ IPv6连接成功")
            else:
                print(f"✗ IPv6连接失败，错误代码: {result}")
            sock.close()
        except Exception as e:
            print(f"✗ IPv6连接异常: {e}")

except socket.gaierror as e:
    print(f"DNS解析失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")

# 检查环境变量
print(f"\n环境变量检查:")
db_url = os.getenv('DATABASE_URL', '未设置')
print(f"DATABASE_URL: {db_url}")

if db_url != '未设置':
    try:
        parsed = urlparse(db_url)
        print(f"解析结果:")
        print(f"  协议: {parsed.scheme}")
        print(f"  主机: {parsed.hostname}")
        print(f"  端口: {parsed.port}")
        print(f"  数据库: {parsed.path[1:] if parsed.path else 'N/A'}")
    except Exception as e:
        print(f"URL解析错误: {e}")