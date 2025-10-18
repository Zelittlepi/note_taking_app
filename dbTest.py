import os
import re
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL not set in .env")
    exit(1)

print(f"Using DATABASE_URL: {db_url}")

# Extract host for DNS check
match = re.search(r'@([^:/?]+)', db_url)
host = match.group(1) if match else None

if host:
    print(f"Testing DNS resolution for host: {host}")
    try:
        ip = socket.gethostbyname(host)
        print(f"DNS resolved {host} to {ip}")
    except Exception as e:
        print(f"DNS resolution failed for {host}: {e}")
else:
    print("Could not extract host from DATABASE_URL")

# Test PostgreSQL connection
print("Testing PostgreSQL connection...")
try:
    import psycopg2
    conn = psycopg2.connect(db_url, connect_timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    print(f"PostgreSQL connection successful, SELECT 1 returned: {result}")
    cur.close()
    conn.close()
    print("Database test completed successfully!")
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")