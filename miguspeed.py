import requests
import time
from urllib.parse import urlparse

def get_redirect_url(api):
    try:
        r = requests.get(api, headers={
            "Connection": "keep-alive",
            "User-Agent": "okhttp/5.3.2"
        }, timeout=10, allow_redirects=False)

        return r.headers.get("Location", "")
    except:
        return ""

def test_speed(url):
    url = url.replace("https://", "http://")

    downloaded = 0
    start = time.time()

    try:
        with requests.get(url, stream=True, headers={
            "Connection": "keep-alive",
            "User-Agent": "okhttp/5.3.2"
        }, timeout=10) as r:

            for chunk in r.iter_content(chunk_size=4096):
                downloaded += len(chunk)
                if time.time() - start >= 5:
                    break

    except:
        return 0

    duration = time.time() - start
    if duration <= 0:
        return 0

    return round(downloaded / duration / 1024, 2)

def main():
    results = []

    # 读取远程文件
    url = "https://raw.githubusercontent.com/kakaxi-1/IPTV/refs/heads/main/ipv4.txt"
    text = requests.get(url).text
    lines = text.strip().splitlines()

    for line in lines:
        name, api = line.split(",", 1)
        redirect = get_redirect_url(api)

        if not redirect:
            continue

        speed = test_speed(redirect)

        results.append({
            "name": name,
            "api": api,
            "redirect": redirect,
            "speed": speed
        })

    # 排序
    results.sort(key=lambda x: x["speed"], reverse=True)

    # 生成 MGPD.txt
    hosts = []
    for r in results:
        if r["speed"] > 0:
            u = urlparse(r["api"])
            hosts.append(f"{u.hostname}:{u.port}")

    mgpd_line = "5," + ",".join(hosts)

    with open("MGPD.txt", "w") as f:
        f.write(mgpd_line)

    print("生成 MGPD.txt：")
    print(mgpd_line)

if __name__ == "__main__":
    main()
