#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""診斷 CASE 2 的失敗原因"""

import os
import sys
import io
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

WIKI_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\台灣"
TWGEOJSON_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\twgeojson\twtown2010.json"

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """射線投射演算法，加入邊界容差處理"""
    x, y = point
    n = len(polygon)
    inside = False
    tolerance = 1e-3  # 容差值，約 100m 級別

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]

        # 檢查點是否在邊上（點到直線的距離）
        edge_len = ((p2y - p1y)**2 + (p2x - p1x)**2)**0.5
        if edge_len > 0:
            dist = abs((p2y - p1y) * x - (p2x - p1x) * y + p2x * p1y - p2y * p1x) / edge_len
            if dist < tolerance:
                return True

        # 標準射線投射
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def load_geojson_towns() -> Dict[str, Dict]:
    """載入 GeoJSON（自動合併重複區域）"""
    try:
        with open(TWGEOJSON_PATH, 'r', encoding='utf-8') as f:
            geojson = json.load(f)

        towns = {}
        for feature in geojson.get('features', []):
            props = feature.get('properties', {})
            town_name = props.get('town')
            county_name = props.get('county')
            geometry = feature.get('geometry', {})

            if town_name and county_name and geometry.get('type') == 'MultiPolygon':
                key = f"{county_name}/{town_name}"
                if key not in towns:
                    towns[key] = {
                        'county': county_name,
                        'town': town_name,
                        'geometry': {'type': 'MultiPolygon', 'coordinates': []}
                    }
                # 合併 polygons（處理重複的鄉鎮市區）
                towns[key]['geometry']['coordinates'].extend(geometry.get('coordinates', []))

        return towns
    except Exception as e:
        print(f"❌ 無法載入 GeoJSON: {e}")
        return {}

def extract_coordinates(file_path: Path) -> Optional[Tuple[float, float]]:
    """提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def find_correct_district(coords: Tuple[float, float], towns: Dict[str, Dict]) -> Optional[str]:
    """根據座標找正確的鄉鎮市區"""
    point = coords
    for key, town_data in towns.items():
        geometry = town_data['geometry']
        for polygon_ring in geometry.get('coordinates', []):
            if not polygon_ring:
                continue
            ring = [(float(c[0]), float(c[1])) for c in polygon_ring[0]]
            if len(ring) > 2 and point_in_polygon(point, ring):
                return key
    return None

# 診斷
print("🔍 診斷 CASE 2 失敗原因")
print("=" * 60)

# 載入
print("1️⃣ 載入 GeoJSON...")
towns = load_geojson_towns()
print(f"   ✓ 載入 {len(towns)} 個鄉鎮市區")

# 找第一個檔案
print("\n2️⃣ 找第一個在'其他'目錄的檔案...")
test_file = None
wiki_path = Path(WIKI_PATH)
for county_dir in wiki_path.iterdir():
    if not county_dir.is_dir():
        continue
    other_dir = county_dir / '其他'
    if other_dir.exists():
        for md_file in other_dir.glob('*.md'):
            test_file = md_file
            break
    if test_file:
        break

if not test_file:
    print("   ❌ 找不到測試檔案")
    sys.exit(1)

print(f"   ✓ {test_file.name}")
print(f"   縣市: {test_file.parent.parent.name}")

# 提取座標
print("\n3️⃣ 提取座標...")
coords = extract_coordinates(test_file)
if not coords:
    print("   ❌ 無法提取座標")
    sys.exit(1)
print(f"   ✓ [{coords[0]}, {coords[1]}]")

# 找正確的鄉鎮市區
print("\n4️⃣ 用 find_correct_district() 查詢...")
result = find_correct_district(coords, towns)
if not result:
    print("   ❌ 找不到匹配的鄉鎮市區！")
    print("   這是主要問題！")
else:
    county, town = result.split('/')
    print(f"   ✓ 應該在: {county}/{town}")

# 測試目標路徑
if result:
    county, town = result.split('/')
    dest_dir = Path(WIKI_PATH) / county / town
    print(f"\n5️⃣ 測試目標路徑...")
    print(f"   路徑: {dest_dir}")
    print(f"   是否存在: {dest_dir.exists()}")

    if not dest_dir.exists():
        print(f"   嘗試建立...")
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ 成功建立")
        except Exception as e:
            print(f"   ❌ 失敗: {e}")

print("\n" + "=" * 60)
print("診斷完成")
