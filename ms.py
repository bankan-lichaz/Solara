import requests
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    print("  ✔ 已加入测速队列\n")

    results.append({
        "name": name,
        "api": api,
        "redirect": final_url
    })

    print()

# Step 3：多线程测速
print("开始多线程测速...\n")

speed_results = []

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {
        executor.submit(test_stream_speed, r["redirect"], 5): r
        for r in results
    }

    for future in as_completed(futures):
        r = futures[future]
        final_url = r["redirect"]
        api = r["api"]

        speed = future.result()
        print(f"测速完成：{final_url} → {speed} bytes")

        if speed > 0:
            url = urlparse(api)
            host = url.hostname
            port = url.port
            if host and port:
                speed_results.append({
                    "hostport": f"{host}:{port}",
                    "speed": speed
                })
                print("  ✔ 速度有效，加入 MGPD")
        else:
            print("  ❌ 速度为 0，跳过")

        print()

# Step 4：按速度排序（从快到慢）
speed_results.sort(key=lambda x: x["speed"], reverse=True)

# Step 5：生成 MGPD 文件
mgpd_file = "MGPD"

if speed_results:
    line = "5," + ",".join([item["hostport"] for item in speed_results])
else:
    line = ""  # 空文件

with open(mgpd_file, "w", encoding="utf-8") as f:
    f.write(line)

print(f"\nMGPD 文件已生成：{mgpd_file}")
print("内容：")
print(line if line else "（空文件）")
