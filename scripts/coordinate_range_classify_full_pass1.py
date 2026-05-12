#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一輪：座標範圍判斷分類 (全部 3585 個)
快速掃描，記錄結果以便分析問題
"""

import os
import sys
import csv
import io
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"

# 定義國家的經緯度範圍
COUNTRY_RANGES = {
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '日本': {'lng': (130, 145), 'lat': (30, 45)},
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
    '阿根廷': {'lng': (-76, -53), 'lat': (-56, -21)},
    '巴西': {'lng': (-74, -35), 'lat': (-34, 5)},
    '紐西蘭': {'lng': (166, 179), 'lat': (-47, -34)},
    '澳洲': {'lng': (113, 155), 'lat': (-47, -10)},
    '埃及': {'lng': (25, 36), 'lat': (22, 32)},
    '荷蘭': {'lng': (3, 7), 'lat': (50, 54)},
    '比利時': {'lng': (2, 6), 'lat': (49, 52)},
    '法國': {'lng': (-8, 8), 'lat': (42, 51)},
    '西班牙': {'lng': (-10, 4), 'lat': (36, 44)},
    '義大利': {'lng': (6, 20), 'lat': (37, 47)},
    '奧地利': {'lng': (9, 17), 'lat': (47, 49)},
    '瑞士': {'lng': (5, 11), 'lat': (45, 48)},
    '捷克': {'lng': (12, 19), 'lat': (48, 51)},
    '匈牙利': {'lng': (16, 23), 'lat': (46, 49)},
    '葡萄牙': {'lng': (-9, -6), 'lat': (37, 42)},
    '英國': {'lng': (-8, 2), 'lat': (50, 59)},
}

# 主要城市中心坐標
CITY_CENTERS = {
    '台灣': {
        '台北市': (121.5654, 25.0330),
        '新北市': (121.4657, 24.9871),
        '基隆市': (121.7081, 25.1283),
        '桃園市': (121.3010, 24.9936),
        '新竹市': (120.9647, 24.8138),
        '苗栗縣': (120.8200, 24.5602),
        '台中市': (120.6736, 24.1477),
        '彰化縣': (120.5387, 23.9936),
        '南投縣': (120.6780, 23.8241),
        '雲林縣': (120.3900, 23.7200),
        '嘉義市': (120.4294, 23.4801),
        '台南市': (120.2270, 22.9998),
        '高雄市': (120.3133, 22.6273),
        '屏東縣': (120.4903, 22.5519),
        '宜蘭縣': (121.7195, 24.6969),
        '花蓮縣': (121.6011, 23.9871),
        '台東縣': (121.1441, 22.7972),
    },
    '日本': {
        '東京': (139.6917, 35.6895),
        '大阪': (135.5023, 34.6937),
        '名古屋': (136.9066, 35.1815),
        '福岡': (130.4017, 33.5904),
        '札幌': (141.3469, 43.0642),
        '京都': (135.7681, 35.0116),
        '神戶': (135.1955, 34.6901),
        '廣島': (132.4522, 34.3853),
        '那覇': (127.6809, 26.2125),  # 沖繩
    },
    '中國': {
        '北京': (116.4074, 39.9042),
        '上海': (121.4737, 31.2304),
        '廣州': (113.2644, 23.1291),
        '深圳': (114.0579, 22.5431),
        '成都': (104.0660, 30.5728),
        '杭州': (120.1551, 30.2875),
        '南京': (118.7969, 32.0603),
        '武漢': (114.3055, 30.5928),
        '西安': (108.9398, 34.3416),
        '蘇州': (120.5954, 31.2989),
        '長沙': (112.9388, 28.2282),
        '重慶': (106.5516, 29.5630),
    },
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    """計算歐幾里得距離"""
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def classify_by_coordinate(lat, lng):
    """根據座標判斷國家和城市"""
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None, None

    # 先判斷國家
    country = None
    for c, ranges in COUNTRY_RANGES.items():
        lng_min, lng_max = ranges['lng']
        lat_min, lat_max = ranges['lat']
        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
            country = c
            break

    if not country:
        return None, None

    # 再判斷城市
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
print("🗺️  第一輪：座標範圍判斷 (全部)", flush=True)
print("=" * 70, flush=True)

# 讀取所有檔案
rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

total = len(rows)
print(f"📊 讀取 {total} 個檔案\n", flush=True)

success_count = 0
fail_count = 0
updated_rows = []

for i, row in enumerate(rows, 1):
    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    # 根據座標判斷
    country, city = classify_by_coordinate(lat, lng)

    if country:
        row['城市'] = city or ''
        row['國家'] = country
        success_count += 1
    else:
        fail_count += 1

    updated_rows.append(row)

    # 每 100 個顯示進度
    if i % 100 == 0 or i == 1:
        print(f"[{i:4d}/{total}] 進度: {i/total*100:5.1f}% | 成功: {success_count} | 失敗: {fail_count}", flush=True)

# 寫回 CSV
print("\n💾 寫入 CSV...", flush=True)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
    writer.writeheader()
    writer.writerows(updated_rows)

print("\n" + "=" * 70, flush=True)
print(f"✅ 第一輪完成！", flush=True)
print(f"  成功分類: {success_count} 個", flush=True)
print(f"  無法分類: {fail_count} 個", flush=True)
print("=" * 70, flush=True)
