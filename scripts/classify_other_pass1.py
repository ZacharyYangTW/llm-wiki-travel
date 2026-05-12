#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pass 1: 分類 wiki/其他 的 130 個檔案
"""

import os
import sys
import csv
import io
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\other_files_all.csv"

# 使用相同的國家/城市範圍定義（Pass 1 基礎版本）
COUNTRY_RANGES = {
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '日本': {'lng': (130, 146), 'lat': (30, 46)},
    '中國': {'lng': (73, 135), 'lat': (18, 54)},
    '泰國': {'lng': (97, 106), 'lat': (5, 21)},
    '越南': {'lng': (102, 110), 'lat': (8, 24)},
    '柬埔寨': {'lng': (102, 108), 'lat': (10, 15)},
    '馬來西亞': {'lng': (100, 119), 'lat': (1, 7)},
    '新加坡': {'lng': (103.5, 104.5), 'lat': (1, 2)},
    '印尼': {'lng': (95, 141), 'lat': (-11, 6)},
    '菲律賓': {'lng': (117, 127), 'lat': (5, 19)},
    '韓國': {'lng': (124, 132), 'lat': (33, 43)},
    '香港': {'lng': (113.8, 114.4), 'lat': (22.2, 22.6)},
    '澳門': {'lng': (113.5, 113.6), 'lat': (22.1, 22.2)},
    '美國': {'lng': (-125, -66), 'lat': (25, 50)},
    '加拿大': {'lng': (-141, -52), 'lat': (42, 84)},
    '墨西哥': {'lng': (-117, -86), 'lat': (14, 33)},
    '秘魯': {'lng': (-82, -68), 'lat': (-18, 0)},
    '智利': {'lng': (-77, -66), 'lat': (-56, -17)},
    '澳洲': {'lng': (113, 155), 'lat': (-47, -10)},
    '荷蘭': {'lng': (3, 7), 'lat': (50, 54)},
    '比利時': {'lng': (2, 6), 'lat': (49, 52)},
    '法國': {'lng': (-8, 8), 'lat': (42, 51)},
    '西班牙': {'lng': (-10, 4), 'lat': (36, 44)},
}

CITY_CENTERS = {
    '泰國': {'曼谷': (100.5018, 13.7563), '芭達雅': (100.8847, 12.9272)},
    '日本': {'東京': (139.6917, 35.6895), '大阪': (135.5023, 34.6937)},
    '中國': {'北京': (116.4074, 39.9042), '廣州': (113.2644, 23.1291)},
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def classify_by_coordinate(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None, None

    # 判斷國家
    country = None
    for c, ranges in COUNTRY_RANGES.items():
        lng_min, lng_max = ranges['lng']
        lat_min, lat_max = ranges['lat']
        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
            country = c
            break

    if not country:
        return None, None

    # 判斷城市
    city = None
    if country in CITY_CENTERS:
        cities = CITY_CENTERS[country]
        min_dist = float('inf')
        for city_name, (c_lng, c_lat) in cities.items():
            dist = euclidean_distance(lat, lng, c_lat, c_lng)
            if dist < min_dist:
                min_dist = dist
                city = city_name

    return country, city

print("=" * 70, flush=True)
print("🗺️  Pass 1: 分類 wiki/其他 檔案", flush=True)
print("=" * 70, flush=True)

rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

total = len(rows)
print(f"📊 讀取 {total} 個檔案\n", flush=True)

success_count = 0
fail_count = 0

for i, row in enumerate(rows, 1):
    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    country, city = classify_by_coordinate(lat, lng)

    if country:
        row['城市'] = city or ''
        row['國家'] = country
        success_count += 1
    else:
        fail_count += 1

    if i % 50 == 0 or i == 1:
        print(f"[{i:3d}/{total}] 進度: {i/total*100:5.1f}% | 成功: {success_count} | 失敗: {fail_count}", flush=True)

# 寫回 CSV
print("\n💾 寫入 CSV...", flush=True)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家', '原始路徑'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 70, flush=True)
print(f"✅ Pass 1 完成！", flush=True)
print(f"  成功分類: {success_count} 個 ({success_count*100//total}%)", flush=True)
print(f"  無法分類: {fail_count} 個 ({fail_count*100//total}%)", flush=True)
print("=" * 70, flush=True)
