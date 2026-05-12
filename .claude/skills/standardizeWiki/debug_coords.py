#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試座標和分類問題
"""

import os
import sys
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 地理坐標範圍定義
COUNTRY_COORDS = {
    '印尼': {'lng': (95, 141), 'lat': (-11, 6)},
    '馬來西亞': {'lng': (99.6, 119.3), 'lat': (0.85, 6.7)},
}

# 城市中心座標
CITY_COORDS = {
    'Penang': (100.3333, 5.3667),
    'Kuala Lumpur': (101.6964, 3.1390),
    'Malacca': (102.2381, 2.1896),
    'Medan': (98.6722, 3.5952),
    'Palembang': (104.7458, -2.9181),
}

def extract_coordinates_from_file(filepath):
    """從 markdown 檔案提取座標"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def is_within_bounds(coords, bounds):
    """檢查座標是否在範圍內"""
    lng, lat = coords
    lng_min, lng_max = bounds['lng']
    lat_min, lat_max = bounds['lat']
    return lng_min <= lng <= lng_max and lat_min <= lat <= lat_max

def debug():
    """調試"""
    source_path = os.path.join(WIKI_BASE, '印尼', 'Medan', 'POI')

    print("=" * 100)
    print("🐛 調試座標和分類")
    print("=" * 100)

    # 檢查幾個具體的檔案
    test_files = [
        '92 Armenian 穎川燕窩.md',
        'Batu Caves.md',
        'Medan Airport.md',
        'Sunway Pyramid.md'
    ]

    for filename in test_files:
        filepath = os.path.join(source_path, filename)
        if not os.path.exists(filepath):
            print(f"\n❌ 檔案不存在: {filename}")
            continue

        coords = extract_coordinates_from_file(filepath)

        print(f"\n📄 {filename}")
        print(f"   座標: {coords}")

        if coords:
            malaysia_bounds = COUNTRY_COORDS['馬來西亞']
            indonesia_bounds = COUNTRY_COORDS['印尼']

            in_malaysia = is_within_bounds(coords, malaysia_bounds)
            in_indonesia = is_within_bounds(coords, indonesia_bounds)

            print(f"   馬來西亞範圍: {malaysia_bounds}")
            print(f"   在馬來西亞: {in_malaysia}")
            print(f"   在印尼: {in_indonesia}")

            # 找到最近的城市
            lng, lat = coords
            distances = {}
            for city_name, (city_lng, city_lat) in CITY_COORDS.items():
                distance = ((lng - city_lng) ** 2 + (lat - city_lat) ** 2) ** 0.5
                distances[city_name] = distance

            nearest = min(distances.items(), key=lambda x: x[1])
            print(f"   最近城市: {nearest[0]} (距離: {nearest[1]:.4f}°)")

if __name__ == '__main__':
    debug()
