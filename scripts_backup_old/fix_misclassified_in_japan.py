#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復日本目錄裡的誤分類檔案
偵測並移動釜山、濟州、首爾等韓國檔案到韓國目錄
以及其他非日本的檔案到正確的國家
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
WIKI_JAPAN = os.path.join(WIKI_BASE, "日本")
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 國家地理範圍
COUNTRY_RANGES = {
    '日本': {'lng': (122, 146), 'lat': (24, 46)},
    '韓國': {'lng': (124, 132), 'lat': (33, 43)},
    '中國': {'lng': (73, 135), 'lat': (18, 54)},
    '泰國': {'lng': (97, 106), 'lat': (5, 21)},
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
}

# 各國主要城市中心
CITY_CENTERS = {
    '韓國': {
        '首爾': (126.9780, 37.5665),
        '釜山': (129.0756, 35.1595),
        '大邱': (128.5626, 35.8714),
        '濟州': (126.5227, 33.5133),
        '仁川': (126.7345, 37.4563),
        '大田': (127.4240, 36.3504),
        '光州': (126.8793, 35.1603),
        '蔚山': (129.3159, 35.5380),
    },
    '日本': {
        '東京': (139.6917, 35.6895),
        '大阪': (135.5023, 34.6937),
        '京都': (135.7681, 35.0116),
        '沖繩': (127.6809, 26.2125),
        '長崎': (129.8707, 32.7513),
        '福岡': (130.4017, 33.5904),
        '札幌': (141.3469, 43.0642),
        '名古屋': (136.8822, 35.1815),
    },
    '泰國': {
        '曼谷': (100.5018, 13.7563),
        '清萊': (100.7932, 20.2749),
        '清邁': (98.9853, 18.7883),
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
    """根據坐標判斷真正的國家和城市（優先檢查韓國）"""
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None, None

    # 優先檢查韓國（因為與日本重疊）
    korea_ranges = COUNTRY_RANGES['韓國']
    lng_min, lng_max = korea_ranges['lng']
    lat_min, lat_max = korea_ranges['lat']
    if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
        # 檢查是否更接近韓國
        if lng in CITY_CENTERS['韓國'].values():
            cities = CITY_CENTERS['韓國']
            min_dist = float('inf')
            best_city = None
            for city_name, (c_lng, c_lat) in cities.items():
                dist = euclidean_distance(lat, lng, c_lat, c_lng)
                if dist < min_dist:
                    min_dist = dist
                    best_city = city_name
            return '韓國', best_city

        # 用距離法判斷是韓國還是日本
        korea_center = CITY_CENTERS['韓國'].get('首爾', (126.9780, 37.5665))
        japan_center = CITY_CENTERS['日本'].get('福岡', (130.4017, 33.5904))

        korea_dist = euclidean_distance(lat, lng, korea_center[1], korea_center[0])
        japan_dist = euclidean_distance(lat, lng, japan_center[1], japan_center[0])

        # 如果更接近韓國
        if korea_dist < japan_dist:
            cities = CITY_CENTERS['韓國']
            min_dist = float('inf')
            best_city = None
            for city_name, (c_lng, c_lat) in cities.items():
                dist = euclidean_distance(lat, lng, c_lat, c_lng)
                if dist < min_dist:
                    min_dist = dist
                    best_city = city_name
            return '韓國', best_city

    # 再檢查其他國家
    country = None
    for c, ranges in COUNTRY_RANGES.items():
        if c == '韓國':  # 已檢查過
            continue
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
print("🔧 修復日本目錄的誤分類檔案", flush=True)
print("=" * 70, flush=True)

moved_count = 0
stayed_in_japan = 0
unclassified = 0
failed_list = []

# 掃描日本目錄下的所有子目錄
for subdir in sorted(os.listdir(WIKI_JAPAN)):
    subdir_path = os.path.join(WIKI_JAPAN, subdir)

    if not os.path.isdir(subdir_path):
        continue

    # 列出該目錄下的 .md 檔案
    files = [f for f in os.listdir(subdir_path)
             if f.endswith('.md') and os.path.isfile(os.path.join(subdir_path, f))]

    if not files:
        continue

    # 檢查該目錄名稱是否看起來像日本都道府縣
    is_japan_prefecture = any(x in subdir for x in ['都', '道', '府', '県', '縣', '東京', '大阪', '長崎', '福岡', '沖繩', '沖縄'])

    if not is_japan_prefecture:
        # 這個目錄名稱不像日本地名，跳過警告
        continue

    print(f"\n🔍 掃描 {subdir} ({len(files)} 個檔案)", flush=True)

    for filename in files:
        file_path = os.path.join(subdir_path, filename)
        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            continue  # 無坐標的跳過（保留在原地）

        # 判斷真正的國家和城市
        country, city = classify_by_coordinate(lat, lng)

        if not country:
            unclassified += 1
            continue

        # 如果是日本，保留在原地
        if country == '日本':
            stayed_in_japan += 1
            continue

        # 否則移動到對應國家/城市
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
            failed_list.append((title, f"{subdir}/{country}", str(e)[:30]))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動到正確國家: {moved_count} 個", flush=True)
print(f"  保留在日本: {stayed_in_japan} 個", flush=True)
print(f"  無法分類: {unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

if failed_list:
    print(f"\n⚠️  失敗的檔案：", flush=True)
    for title, location, reason in failed_list[:10]:
        print(f"  - {title[:40]:<40} ({location}) {reason}", flush=True)
    if len(failed_list) > 10:
        print(f"  ... 及其他 {len(failed_list)-10} 個", flush=True)

print(f"{'='*70}", flush=True)
