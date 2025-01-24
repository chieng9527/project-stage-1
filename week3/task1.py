import csv
import json
import urllib.request
import re
from collections import defaultdict

# URL 列表
urls = [
    "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment-1",
    "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment-2"
]

# 下載資料
def fetch_data(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# 提取行政區域
def extract_district(address):
    match = re.search(r"(中正區|萬華區|中山區|大同區|大安區|松山區|信義區|士林區|文山區|北投區|內湖區|南港區)", address)
    return match.group(1) if match else "未知"

# 提取第一張圖片的 URL
def extract_first_image(filelist):
    if filelist:
        # 匹配第一個以 .jpg 結尾的網址（不區分大小寫）
        match = re.search(r"https.*?\.jpg", filelist, re.IGNORECASE)
        return match.group(0) if match else ""
    return ""

# 解析資料
data1 = fetch_data(urls[0])["data"]["results"] if fetch_data(urls[0]) else []
data2 = fetch_data(urls[1])["data"] if fetch_data(urls[1]) else []

# 建立 SERIAL_NO 與 District 的對應關係
serial_no_to_district = {}
for item in data2:
    if "SERIAL_NO" in item and "address" in item:
        serial_no_to_district[item["SERIAL_NO"]] = extract_district(item["address"])

# 生成 spot.csv
with open("spot.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    for item in data1:
        district = serial_no_to_district.get(item["SERIAL_NO"], "未知")
        image_url = extract_first_image(item.get("filelist", ""))
        writer.writerow([
            item["stitle"],
            district,
            item["longitude"],
            item["latitude"],
            image_url
        ])

# 整理捷運站與景點名稱
mrt_to_titles = defaultdict(list)
serial_no_to_title = {item["SERIAL_NO"]: item["stitle"] for item in data1}

for item in data2:
    mrt = item.get("MRT", "")
    serial_no = item.get("SERIAL_NO", "")
    if mrt and serial_no in serial_no_to_title:
        mrt_to_titles[mrt].append(serial_no_to_title[serial_no])

# 生成 mrt.csv
with open("mrt.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    for station in sorted(mrt_to_titles.keys()):
        writer.writerow([station] + mrt_to_titles[station])

# 生成 mrt.csv
with open("mrt.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    for station in sorted(mrt_to_titles.keys()):
        writer.writerow([station] + mrt_to_titles[station])
