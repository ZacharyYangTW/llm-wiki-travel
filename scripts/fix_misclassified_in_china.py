#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
偵測和修復在中國目錄裡但實際上來自其他國家的檔案
根據坐標移動到正確的國家/城市目錄
"""

import os
import sys
import re
import shutil
import math
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
WIKI_CHINA = os.path.join(WIKI_BASE, "中國")
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 國家地理範圍（用於初步判斷）
COUNTRY_RANGES = {
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '日本': {'lng': (122, 146), 'lat': (24, 46)},  # 包括沖繩
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
    '印度': {'lng': (68, 97), 'lat': (8, 37)},
    '埃及': {'lng': (24, 37), 'lat': (22, 32)},
    '奧地利': {'lng': (9, 17), 'lat': (47, 49)},
    '捷克': {'lng': (12, 19), 'lat': (48, 51)},
}

# 主要城市中心（用於距離判斷）
CITY_CENTERS = {
    '日本': {
        '東京': (139.6917, 35.6895),
        '大阪': (135.5023, 34.6937),
        '京都': (135.7681, 35.0116),
        '沖繩': (127.6809, 26.2125),
        '長崎': (129.8707, 32.7513),
        '福岡': (130.4017, 33.5904),
    },
    '韓國': {
        '首爾': (126.9780, 37.5665),
        '釜山': (129.0756, 35.1595),
        '大邱': (128.5626, 35.8714),
        '濟州': (126.5227, 33.5133),
        '仁川': (126.7345, 37.4563),
        '大田': (127.4240, 36.3504),
    },
    '泰國': {
        '曼谷': (100.5018, 13.7563),
        '清萊': (100.7932, 20.2749),
        '清邁': (98.9853, 18.7883),
    },
    '越南': {
        '河內': (105.8517, 21.0285),
        '胡志明市': (106.6669, 10.7769),
        '沙壩': (103.8343, 22.3402),
    },
    '印度': {
        '德里': (77.1025, 28.6139),
        '孟買': (72.8479, 19.0760),
        '班加羅爾': (77.5946, 12.9716),
    },
    '台灣': {
        '台北': (121.5654, 25.0330),
        '台中': (120.6736, 24.1477),
        '高雄': (120.3133, 22.6273),
    },
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def extract_coordinates(md_file):
    """提取坐標"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(COORD_PATTERN, content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return lng, lat
    except:
        pass
    return None, None

def classify_by_coordinate(lat, lng):
    """根據坐標判斷國家和城市"""
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
print("🔧 偵測和修復中國目錄裡的誤分類檔案", flush=True)
print("=" * 70, flush=True)

moved_count = 0
stayed_in_china = 0
unclassified = 0
failed_list = []

# 掃描所有省份
for province in sorted(os.listdir(WIKI_CHINA)):
    province_path = os.path.join(WIKI_CHINA, province)

    if not os.path.isdir(province_path):
        continue

    # 列出根目錄的 .md 檔案
    root_files = [f for f in os.listdir(province_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(province_path, f))]

    if not root_files:
        continue

    print(f"\n🔍 檢查 {province} ({len(root_files)} 個根目錄檔案)", flush=True)

    for filename in root_files:
        file_path = os.path.join(province_path, filename)
        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            failed_list.append((title, f"{province}/×", "無坐標"))
            continue

        # 判斷國家和城市
        country, city = classify_by_coordinate(lat, lng)

        if not country:
            unclassified += 1
            failed_list.append((title, f"{province}/×", f"[{lng:.2f}, {lat:.2f}]"))
            continue

        # 如果判斷為中國，保留在原地（已有機制處理）
        if country == '中國':
            stayed_in_china += 1
            continue

        # 否則移動到對應國家/城市
        try:
            if city:
                target_dir = os.path.join(WIKI_BASE, country, city)
            else:
                target_dir = os.path.join(WIKI_BASE, country)

            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, filename)

            shutil.move(file_path, target_file)
            moved_count += 1
            print(f"  ✓ {title[:35]:<35} → {country}/{city or '×'}", flush=True)

        except Exception as e:
            failed_list.append((title, f"{province}/{country}", str(e)[:30]))
            print(f"  ❌ {title[:35]:<35} 錯誤: {str(e)[:30]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動到正確國家: {moved_count} 個", flush=True)
print(f"  保留在中國: {stayed_in_china} 個", flush=True)
print(f"  無法分類: {unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

if failed_list:
    print(f"\n⚠️  無法判斷或失敗的檔案：", flush=True)
    for title, location, reason in failed_list[:15]:
        print(f"  - {title[:40]:<40} ({location}) {reason}", flush=True)
    if len(failed_list) > 15:
        print(f"  ... 及其他 {len(failed_list)-15} 個", flush=True)

print(f"{'='*70}", flush=True)
