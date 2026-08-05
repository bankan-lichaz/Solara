import requests
from urllib.parse import urlparse
import re

print("Content-Type: text/plain; charset=utf-8")

# 读取文件
try:
    with open("3.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except:
    print("无法读取 3.txt")
    exit()

results = []

HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "okhttp/5.3.2"
}

def get_final_url(api):
    """
    自动跟随跳转，如果跳转失败，则从异常信息中提取 host + port + path 拼接真实流地址
    """
    try:
        resp = requests.get(api, headers=HEADERS, timeout=10, allow_redirects=True)
        return resp.url

    except Exception as e:
        msg = str(e)

        host_match = re.search(r"host='([^']+)'", msg)
        port_match = re.search(r"port=(\d+)", msg)
        url_match = re.search(r"url: ([^\s]+)", msg)

        if host_match and port_match and url_match:
            host = host_match.group(1)
            port = port_match.group(1)
            path = url_match.group(1)
            final_url = f"http://{host}:{port}{path}"
            print(f"  ⚠ 跳转失败，但已提取真实流地址：{final_url}")
            return final_url

        print(f"  ❌ 跳转失败且无法提取真实流地址：{e}")
        return None


print("================= 开始处理 =================\n")

for line in lines:
    name, api = line.split(",", 1)
    print(f"正在处理：{name} ({api})")

    final_url = get_final_url(api)
    if not final_url:
        print("  ❌ 无法获取真实流地址\n")
        continue

    print(f"  最终流地址：{final_url}")

    results.append({
        "name": name,
        "final": final_url
    })

    print()


# ⭐ 生成 MGZS 文件：name, final_url
mgzs_file = "MGZS"

with open(mgzs_file, "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"{r['name']},{r['final']}\n")

print(f"\nMGZS 文件已生成：{mgzs_file}")
