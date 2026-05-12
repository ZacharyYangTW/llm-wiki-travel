#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 wiki/中國 根目錄的 151 個誤分類檔案
根據坐標移動到正確的國家/城市
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
WIKI_CHINA_ROOT = os.path.join(WIKI_BASE, "中國")
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 國家地理範圍（優先檢查範圍較小的國家）
COUNTRY_RANGES = {
    '香港': {'lng': (113.8, 114.4), 'lat': (22.2, 22.6)},  # 最先檢查，範圍最小
    '澳門': {'lng': (113.5, 113.6), 'lat': (22.1, 22.2)},
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '印度': {'lng': (68, 97), 'lat': (8, 37)},
    '泰國': {'lng': (97, 106), 'lat': (5, 21)},
    '越南': {'lng': (102, 110), 'lat': (8, 24)},
    '日本': {'lng': (122, 146), 'lat': (24, 46)},
    '韓國': {'lng': (124, 132), 'lat': (33, 43)},
    '中國': {'lng': (73, 123), 'lat': (18, 54)},  # 最後檢查，東邊界改為 123（台灣邊界）
}

# 各國城市中心
CITY_CENTERS = {
    '泰國': {
        '曼谷': (100.5018, 13.7563),
        '清萊': (100.7932, 20.2749),
        '清邁': (98.9853, 18.7883),
    },
    '越南': {
        '河內': (105.8517, 21.0285),
        '胡志明市': (106.6669, 10.7769),
    },
    '印度': {
        '德里': (77.1025, 28.6139),
        '孟買': (72.8479, 19.0760),
    },
    '台灣': {
        '台北': (121.5654, 25.0330),
        '台中': (120.6736, 24.1477),
    },
    '日本': {
        '東京': (139.6917, 35.6895),
        '大阪': (135.5023, 34.6937),
    },
    '韓國': {
        '首爾': (126.9780, 37.5665),
        '釜山': (129.0756, 35.1595),
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

    # 先用範圍判斷國家
    country = None
    for c, ranges in COUNTRY_RANGES.items():
        lng_min, lng_max = ranges['lng']
        lat_min, lat_max = ranges['lat']
        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
            country = c
            break

    if not country:
        return None, None

    # 找該國最近的城市
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
print("🔧 修復 wiki/中國 根目錄的誤分類檔案", flush=True)
print("=" * 70, flush=True)

# 列出根目錄的 .md 檔案
root_files = [f for f in os.listdir(WIKI_CHINA_ROOT)
              if f.endswith('.md') and os.path.isfile(os.path.join(WIKI_CHINA_ROOT, f))]

print(f"\n發現 {len(root_files)} 個根目錄檔案\n", flush=True)

moved_count = 0
stayed_count = 0
unclassified = 0
failed_list = []

for filename in sorted(root_files):
    file_path = os.path.join(WIKI_CHINA_ROOT, filename)
    title = filename[:-3]

    # 提取坐標
    lng, lat = extract_coordinates(file_path)

    if lng is None or lat is None:
        unclassified += 1
        print(f"⚠️  {title[:40]:<40} [無坐標]", flush=True)
        continue

    # 判斷國家和城市
    country, city = classify_by_coordinate(lat, lng)

    if not country:
        unclassified += 1
        print(f"⚠️  {title[:40]:<40} [無法分類]", flush=True)
        continue

    # 如果是中國，保留（應該沒有）
    if country == '中國':
        stayed_count += 1
        print(f"→ {title[:40]:<40} [保留在中國]", flush=True)
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

        print(f"✓ {title[:40]:<40} → {country}/{city or '×'}", flush=True)

    except Exception as e:
        failed_list.append((title, f"{country}/{city}", str(e)[:30]))
        print(f"❌ {title[:40]:<40} {str(e)[:30]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved_count} 個", flush=True)
print(f"  保留在中國: {stayed_count} 個", flush=True)
print(f"  無法分類: {unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

print(f"{'='*70}", flush=True)
