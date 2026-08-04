import requests
from urllib.parse import urlparse

print("Content-Type: text/plain; charset=utf-8")

# 读取文件
try:
    with open("2.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except:
    print("无法读取 2.txt")
    exit()

results = []

# 通用请求头
HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "okhttp/5.3.2"
}

def get_final_url(api):
    """
    自动跟随跳转，永远返回最终真实流地址
    """
    try:
        resp = requests.get(api, headers=HEADERS, timeout=10, allow_redirects=True)
        return resp.url
    except Exception as e:
        print(f"  ❌ 跳转失败：{e}")
        return None

print("================= 开始处理 =================\n")

for line in lines:
    name, api = line.split(",", 1)
    print(f"正在处理：{name} ({api})")

    # Step 1：获取最终真实流地址
    final_url = get_final_url(api)
    if not final_url:
        print("  ❌ 无法获取真实流地址\n")
        continue

    print(f"  最终流地址：{final_url}")

    # Step 2：过滤：最终流地址等于测试流地址的不要写入 MGPD
    if final_url == api:
        print("  ⚠ final_url 与 api 相同，跳过写入 MGPD\n")
        print()
        continue

    print("  ✔ 已加入 MGPD\n")

    results.append({
        "name": name,
        "api": api,
        "redirect": final_url
    })

    print()

# Step 3：生成 MGPD 文件
mgpd_file = "MGPD"
valid_hosts = []

for r in results:
    url = urlparse(r["api"])
    host = url.hostname
    port = url.port
    if host and port:
        valid_hosts.append(f"{host}:{port}")

line = "5," + ",".join(valid_hosts)

with open(mgpd_file, "w", encoding="utf-8") as f:
    f.write(line)

print(f"\nMGPD 文件已生成：{mgpd_file}")
print("内容：")
print(line)
