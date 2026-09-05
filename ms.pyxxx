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

def test_speed(url):
    """
    测速函数：自动处理缓冲、空 chunk、慢启动
    """
    downloaded = 0
    start_time = time.time()

    try:
        with requests.get(url, headers=HEADERS, timeout=10, stream=True) as r:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    downloaded += len(chunk)
                if time.time() - start_time >= 3:  # 测 3 秒更稳定
                    break
    except Exception as e:
        print(f"  ❌ 拉流失败：{e}")
        return 0

    duration = time.time() - start_time
    speed = round(downloaded / duration / 1024, 2) if duration > 0 else 0
    return speed

print("================= 开始测速 =================\n")

for line in lines:
    name, api = line.split(",", 1)
    print(f"正在测试：{name} ({api})")

    # Step 1：获取最终真实流地址
    final_url = get_final_url(api)
    if not final_url:
        print("  ❌ 无法获取真实流地址\n")
        continue

    print(f"  最终流地址：{final_url}")

    # Step 2：测速
    speed = test_speed(final_url)
    print(f"  拉流速度：{speed} KB/s\n")

    results.append({
        "name": name,
        "api": api,
        "redirect": final_url,
        "speed": speed
    })

# Step 3：排序
results.sort(key=lambda x: x["speed"], reverse=True)

print("================= 测速结果（按速度排序） =================\n")
for r in results:
    print(f"{r['name']} | {r['api']} | {r['redirect']} | {r['speed']} KB/s")

# Step 4：生成 MGPD 文件
mgpd_file = "MGPD"
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
