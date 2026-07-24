import requests
import time
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

for line in lines:
    name, api = line.split(",", 1)

    print(f"正在测试：{name} ({api})")

    # Step 1：获取 redirect_url（不跟随跳转）
    try:
        resp = requests.get(api, headers={
            "Connection": "keep-alive",
            "User-Agent": "okhttp/5.3.2"
        }, timeout=10, allow_redirects=False)

        redirect = resp.headers.get("Location", "")
    except Exception as e:
        print(f"  ❌ 请求失败：{e}\n")
        continue

    if not redirect:
        print("  ❌ 无跳转地址，跳过\n")
        continue

    print(f"  跳转地址：{redirect}")

    # 强制 HTTPS → HTTP
    real_url = redirect.replace("https:", "http:")

    # Step 2：测速 5 秒
    downloaded = 0
    start_time = time.time()

    try:
        with requests.get(real_url, headers={
            "Connection": "keep-alive",
            "User-Agent": "okhttp/5.3.2"
        }, timeout=10, stream=True) as r:

            for chunk in r.iter_content(chunk_size=4096):
                if not chunk:
                    break
                downloaded += len(chunk)
                if time.time() - start_time >= 5:
                    break

    except Exception as e:
        print(f"  ❌ 拉流失败：{e}\n")
        continue

    duration = time.time() - start_time
    speed = round(downloaded / duration / 1024, 2) if duration > 0 else 0

    print(f"  拉流速度：{speed} KB/s\n")

    results.append({
        "name": name,
        "api": api,
        "redirect": real_url,
        "speed": speed
    })

# Step 3：排序
results.sort(key=lambda x: x["speed"], reverse=True)

# Step 4：输出最终结果
print("================= 测速结果（按速度排序） =================\n")

for r in results:
    print(f"{r['name']} | {r['api']} | {r['redirect']} | {r['speed']} KB/s")

# ==================== 生成 MGPD 文件 ====================

mgpd_file = "MGPD.txt"
valid_hosts = []

for r in results:
    if r["speed"] > 0:
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
