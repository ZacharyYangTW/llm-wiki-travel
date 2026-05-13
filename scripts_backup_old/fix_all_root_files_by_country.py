#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復所有國家根目錄的未分類檔案
根據坐標分類到城市級
"""

import os
import sys
import re
import shutil
import math
from collections import defaultdict
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 各國主要城市中心（用於坐標分類）
CITY_CENTERS = {
    '台灣': {
        '台北': (121.5654, 25.0330),
        '台中': (120.6736, 24.1477),
        '高雄': (120.3133, 22.6273),
    },
    '泰國': {
        '曼谷': (100.5018, 13.7563),
        '清萊': (100.7932, 20.2749),
        '清邁': (98.9853, 18.7883),
    },
    '越南': {
        '河內': (105.8517, 21.0285),
        '胡志明市': (106.6669, 10.7769),
    },
    '澳洲': {
        '雪梨': (151.2093, -33.8688),
        '墨爾本': (144.9631, -37.8136),
        '布里斯本': (153.0235, -27.4698),
    },
    '美國': {
        '紐約': (-74.0060, 40.7128),
        '洛杉磯': (-118.2437, 34.0522),
        '舊金山': (-122.4194, 37.7749),
    },
    '馬來西亞': {
        '吉隆坡': (101.6869, 3.1390),
        '檳城': (100.3275, 5.3521),
    },
    '荷蘭': {
        '阿姆斯特丹': (4.8945, 52.3676),
        '鹿特丹': (4.4899, 51.9225),
    },
    '西班牙': {
        '馬德里': (-3.7038, 40.4168),
        '巴塞隆納': (2.1686, 41.3851),
    },
    '紐西蘭': {
        '奧克蘭': (174.8860, -37.0082),
        '惠靈頓': (174.7762, -41.2865),
    },
    '秘魯': {
        '利馬': (-77.0369, -12.0464),
        '庫斯科': (-71.9789, -13.5316),
    },
    '法國': {
        '巴黎': (2.3522, 48.8566),
        '馬賽': (5.3698, 43.2965),
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

def find_nearest_city(lat, lng, country):
    """找該國最近的城市"""
    if country not in CITY_CENTERS:
        return None

    cities = CITY_CENTERS[country]
    min_dist = float('inf')
    best_city = None

    for city_name, (c_lng, c_lat) in cities.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            best_city = city_name

    return best_city

print("=" * 70, flush=True)
print("🔧 修復所有國家根目錄的未分類檔案", flush=True)
print("=" * 70, flush=True)

total_moved = 0
total_unclassified = 0
failed_list = []

# 掃描所有國家目錄
for country in sorted(os.listdir(WIKI_BASE)):
    country_path = os.path.join(WIKI_BASE, country)

    if not os.path.isdir(country_path):
        continue

    # 列出根目錄的 .md 檔案
    root_files = [f for f in os.listdir(country_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(country_path, f))]

    if not root_files:
        continue

    print(f"\n📍 {country} ({len(root_files)} 個根目錄檔案)", flush=True)

    moved = 0
    unclassified = 0

    for filename in root_files:
        file_path = os.path.join(country_path, filename)
        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            unclassified += 1
            continue

        # 找最近的城市
        city = find_nearest_city(lat, lng, country)

        if not city:
            unclassified += 1
            continue

        # 移動到城市目錄
        try:
            city_dir = os.path.join(country_path, city)
            os.makedirs(city_dir, exist_ok=True)
            target_file = os.path.join(city_dir, filename)

            if os.path.exists(target_file):
                os.remove(target_file)

            shutil.move(file_path, target_file)
            moved += 1
            total_moved += 1

        except Exception as e:
            failed_list.append((f"{country}/{title}", str(e)[:30]))

    print(f"  ✓ 已移動 {moved} 個 | ⚠️  無法分類 {unclassified} 個", flush=True)
    total_unclassified += unclassified

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {total_moved} 個", flush=True)
print(f"  無法分類: {total_unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

print(f"{'='*70}", flush=True)
