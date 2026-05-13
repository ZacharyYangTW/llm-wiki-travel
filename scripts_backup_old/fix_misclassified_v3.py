#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v3: 正確的分類邏輯
1. 先用國家範圍判斷（中國範圍優先）
2. 再用距離法精確分城市
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

# 國家地理範圍（優先級：中國 > 其他）
COUNTRY_RANGES = {
    '中國': {'lng': (73, 135), 'lat': (18, 54)},
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '日本': {'lng': (122, 146), 'lat': (24, 46)},
    '韓國': {'lng': (124, 132), 'lat': (33, 43)},
    '泰國': {'lng': (97, 106), 'lat': (5, 21)},
    '越南': {'lng': (102, 110), 'lat': (8, 24)},
    '印度': {'lng': (68, 97), 'lat': (8, 37)},
}

# 用於區分日本和韓國邊界
COUNTRY_CENTERS = {
    '日本': (138.2529, 36.2048),
    '韓國': (127.0995, 37.6011),
}

# 日本城市
JAPAN_CITIES = {
    '東京': (139.6917, 35.6895),
    '大阪': (135.5023, 34.6937),
    '京都': (135.7681, 35.0116),
    '沖繩': (127.6809, 26.2125),
    '長崎': (129.8707, 32.7513),
    '福岡': (130.4017, 33.5904),
    '札幌': (141.3469, 43.0642),
    '名古屋': (136.8822, 35.1815),
}

# 韓國城市
KOREA_CITIES = {
    '首爾': (126.9780, 37.5665),
    '釜山': (129.0756, 35.1595),
    '大邱': (128.5626, 35.8714),
    '濟州': (126.5227, 33.5133),
    '仁川': (126.7345, 37.4563),
    '大田': (127.4240, 36.3504),
    '光州': (126.8793, 35.1603),
    '蔚山': (129.3159, 35.5380),
}

# 泰國城市
THAILAND_CITIES = {
    '曼谷': (100.5018, 13.7563),
    '清萊': (100.7932, 20.2749),
    '清邁': (98.9853, 18.7883),
}

# 越南城市
VIETNAM_CITIES = {
    '河內': (105.8517, 21.0285),
    '胡志明市': (106.6669, 10.7769),
}

# 印度城市
INDIA_CITIES = {
    '德里': (77.1025, 28.6139),
    '孟買': (72.8479, 19.0760),
}

CITY_MAPPING = {
    '日本': JAPAN_CITIES,
    '韓國': KOREA_CITIES,
    '泰國': THAILAND_CITIES,
    '越南': VIETNAM_CITIES,
    '印度': INDIA_CITIES,
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

def find_city(lat, lng, country):
    """找該國家內最近的城市"""
    if country not in CITY_MAPPING:
        return None

    cities = CITY_MAPPING[country]
    min_dist = float('inf')
    best_city = None

    for city_name, (c_lng, c_lat) in cities.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            best_city = city_name

    return best_city

def classify_coordinate(lat, lng):
    """
    分類邏輯：
    1. 先用範圍判斷，中國優先
    2. 日本/韓國邊界用距離區分
    """
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None, None

    # 先檢查是否在中國範圍內
    china_ranges = COUNTRY_RANGES['中國']
    lng_min, lng_max = china_ranges['lng']
    lat_min, lat_max = china_ranges['lat']
    if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
        return '中國', None  # 中國檔案保留，無需移動

    # 不在中國範圍，檢查其他國家
    country = None
    for c, ranges in COUNTRY_RANGES.items():
        if c == '中國':
            continue
        lng_min, lng_max = ranges['lng']
        lat_min, lat_max = ranges['lat']
        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
            country = c
            break

    if not country:
        return None, None

    # 特殊情況：日本和韓國邊界用距離判斷
    if country in ['日本', '韓國']:
        japan_center = COUNTRY_CENTERS['日本']
        korea_center = COUNTRY_CENTERS['韓國']
        japan_dist = euclidean_distance(lat, lng, japan_center[1], japan_center[0])
        korea_dist = euclidean_distance(lat, lng, korea_center[1], korea_center[0])

        if korea_dist < japan_dist:
            country = '韓國'
        else:
            country = '日本'

    # 找該國家內最近的城市
    city = find_city(lat, lng, country)

    return country, city

print("=" * 70, flush=True)
print("🔧 v3: 正確分類（先範圍，再距離）", flush=True)
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

        # 分類
        country, city = classify_coordinate(lat, lng)

        if not country:
            unclassified += 1
            failed_list.append((title, f"{province}/×", f"[{lng:.2f}, {lat:.2f}]"))
            continue

        # 如果是中國，保留在原地
        if country == '中國':
            stayed_in_china += 1
            continue

        # 移動到對應國家/城市
        try:
            if city:
                target_dir = os.path.join(WIKI_BASE, country, city)
            else:
                target_dir = os.path.join(WIKI_BASE, country)

            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, filename)

            if os.path.exists(target_file):
                os.remove(target_file)

            shutil.move(file_path, target_file)
            moved_count += 1

            print(f"  ✓ {title[:35]:<35} → {country}/{city or '×'}", flush=True)

        except Exception as e:
            failed_list.append((title, f"{province}/{country}", str(e)[:30]))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動到正確國家: {moved_count} 個", flush=True)
print(f"  保留在中國: {stayed_in_china} 個", flush=True)
print(f"  無法分類: {unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

if failed_list:
    print(f"\n⚠️  無法判斷或失敗的檔案（前 10 個）：", flush=True)
    for title, location, reason in failed_list[:10]:
        print(f"  - {title[:40]:<40} ({location}) {reason}", flush=True)
    if len(failed_list) > 10:
        print(f"  ... 及其他 {len(failed_list)-10} 個", flush=True)

print(f"{'='*70}", flush=True)
