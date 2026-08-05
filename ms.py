import requests
from urllib.parse import urlparse
import time

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
    """自动跟随跳转，永远返回最终真实流地址"""
    try:
        resp = requests.get(api, headers=HEADERS, timeout=10, allow_redirects=True)
        return resp.url
    except Exception as e:
        print(f"  ❌ 跳转失败：{e}")
        return None

def test_stream_speed(url, duration=5):
    """
    拉流测速：持续 duration 秒，统计收到的字节数
    返回字节数（>0 表示有效）
    """
    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=5)
        start = time.time()
        total_bytes = 0

        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                total_bytes += len(chunk)
            if time.time() - start >= duration:
                break

        return total_bytes

    except Exception as e:
        print(f"  ❌ 拉流失败：{e}")
        return 0

print("================= 开始处理 =================\n")

for line in lines:
    name, api = line.split(",", 1)
    print(f"正在处理：{name} ({api})")

    final_url = get_final_url(api)
    if not final_url:
        print("  ❌ 无法获取真实流地址\n")
        continue

    print(f"  最终流地址：{final_url}")

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
    final_url = r["redirect"]

    print(f"测速：{final_url}")
    speed = test_stream_speed(final_url, duration=5)

    print(f"  拉流字节数：{speed}")

    if speed > 0:
        url = urlparse(r["api"])
        host = url.hostname
        port = url.port
        if host and port:
            valid_hosts.append(f"{host}:{port}")
            print("  ✔ 速度有效，写入 MGPD")
    else:
        print("  ❌ 速度为 0，跳过")

    print()

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
