#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分類最後 26 個殘餘檔案
根據坐標移動到正確的國家/城市
"""

import os
import sys
import re
import shutil
import math
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 國家地理範圍（優先級順序重要）
COUNTRY_RANGES = {
    '香港': {'lng': (113.8, 114.4), 'lat': (22.2, 22.6)},
    '澳門': {'lng': (113.5, 113.6), 'lat': (22.1, 22.2)},
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '印度': {'lng': (68, 97), 'lat': (8, 37)},
    '泰國': {'lng': (97, 106), 'lat': (5, 21)},
    '越南': {'lng': (102, 110), 'lat': (8, 24)},
    '日本': {'lng': (122, 146), 'lat': (24, 46)},
    '韓國': {'lng': (124, 132), 'lat': (33, 43)},
    '中國': {'lng': (73, 123), 'lat': (18, 54)},
    '菲律賓': {'lng': (117, 127), 'lat': (5, 19)},
    '加拿大': {'lng': (-141, -52), 'lat': (42, 84)},
}

# 各國城市中心
CITY_CENTERS = {
    '中國': {
        '北京': (116.4074, 39.9042),
        '上海': (121.4737, 31.2304),
        '廣州': (113.2644, 23.1291),
        '西安': (108.9398, 34.3416),
        '成都': (104.0660, 30.5728),
        '敦煌': (100.7500, 40.1500),
        '麗江': (100.2324, 26.8154),
        '拉薩': (91.1173, 29.6470),
        '蘭州': (103.8343, 36.0611),
    },
    '台灣': {
        '台北': (121.5654, 25.0330),
        '基隆': (121.7581, 25.1276),
        '台中': (120.6736, 24.1477),
        '高雄': (120.3133, 22.6273),
    },
    '香港': {
        '香港': (114.1095, 22.3193),
    },
    '澳門': {
        '澳門': (113.5549, 22.1987),
    },
    '菲律賓': {
        '馬尼拉': (120.9842, 14.5995),
        '長灘島': (121.9347, 11.9674),
    },
    '加拿大': {
        '多倫多': (-79.3871, 43.6629),
        '溫哥華': (-123.1207, 49.2827),
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

    # 用範圍判斷國家（優先級順序）
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

# 待分類的檔案清單（國家/檔案名）
REMAINING_FILES = {
    '中國': [
        'A&F.md', '丸作食茶.md', '升庵祠.md', '博多一山道.md', '天山山脈.md',
        '茶馬花街.md', '敦煌機場.md', '清邁國際機場.md', '莫高窟.md',
        '西山景區（東北門）.md', '西寺塔.md', '西都城.md',
        '長安生態保護區-陸龍灣.md', '長頸族.md', '麗江宋城旅遊區-麗江千古情.md'
    ],
    '澳門': [
        'Starbucks Reserve.md', '中國青海省西寧市城北區西寧西站售票處.md',
        '武威市.md', '武隆縣.md', '秦始皇帝陵博物院.md'
    ],
    '香港': ['土樓行程去程休息站.md'],
    '加拿大': ['6.  Fred Meyer West.md'],
    '菲律賓': ['Boracays Grotto (Willys Rock).md'],
}

print("=" * 70, flush=True)
print("🔧 分類最後 26 個殘餘檔案", flush=True)
print("=" * 70, flush=True)

total_moved = 0
total_unclassified = 0
failed_list = []

for source_country, files in REMAINING_FILES.items():
    source_dir = os.path.join(WIKI_BASE, source_country)

    print(f"\n📍 {source_country} ({len(files)} 個檔案)", flush=True)

    for filename in files:
        file_path = os.path.join(source_dir, filename)

        if not os.path.exists(file_path):
            print(f"  ⚠️  {filename[:40]} [找不到檔案]", flush=True)
            continue

        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            total_unclassified += 1
            print(f"  ⚠️  {title[:40]:<40} [無坐標]", flush=True)
            continue

        # 判斷國家和城市
        country, city = classify_by_coordinate(lat, lng)

        if not country:
            total_unclassified += 1
            print(f"  ⚠️  {title[:40]:<40} [無法分類 {lat:.2f},{lng:.2f}]", flush=True)
            continue

        # 移動檔案
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
            total_moved += 1

            # 如果移動到不同國家
            if country != source_country:
                print(f"  ✓ {title[:35]:<35} → {country}/{city or '×'} (跨國移動)", flush=True)
            else:
                print(f"  ✓ {title[:35]:<35} → {city or '×'}", flush=True)

        except Exception as e:
            failed_list.append((f"{source_country}/{title}", str(e)[:30]))
            print(f"  ❌ {title[:35]:<35} {str(e)[:30]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {total_moved} 個", flush=True)
print(f"  無法分類: {total_unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)
    for item, error in failed_list:
        print(f"    - {item}: {error}", flush=True)

print(f"{'='*70}", flush=True)
