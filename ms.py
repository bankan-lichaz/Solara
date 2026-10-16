import requests
from urllib.parse import urlparse
import re

print("Content-Type: text/plain; charset=utf-8")

# 读取文件
try:
    with open("2.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except:
    print("无法读取 2.txt")
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

        # 提取 host='xxx'
        host_match = re.search(r"host='([^']+)'", msg)
        # 提取 port=数字
        port_match = re.search(r"port=(\d+)", msg)
        # 提取 url: /xxxx
        url_match = re.search(r"url: ([^\s]+)", msg)

        if host_match and port_match and url_match:
            host = host_match.group(1)
            port = port_match.group(1)
            path = url_match.group(1)

            # 拼接真实流地址
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

    # final_url 与 api 相同 → 不写入 MGPD
    if final_url == api:
        print("  ⚠ final_url 与 api 相同，跳过写入 MGPD\n")
        continue

    print("  ✔ 已加入 MGPD\n")

    results.append({
        "name": name,
        "api": api,
        "redirect": final_url
    })

    print()


# Step 3：生成 MGPD 文件（无测速，无排序）
mgpd_file = "MGPD"
valid_hosts = []

for r in results:
    url = urlparse(r["api"])
    host = url.hostname
    port = url.port
    if host and port:
        valid_hosts.append(f"{host}:{port}")

# ⭐ 如果没有有效 host:port → 文件完全空白
if valid_hosts:
    line = "5," + ",".join(valid_hosts)
else:
    line = ""

with open(mgpd_file, "w", encoding="utf-8") as f:
    f.write(line)

print(f"\nMGPD 文件已生成：{mgpd_file}")
print("内容：")
print(line if line else "（空文件）")
