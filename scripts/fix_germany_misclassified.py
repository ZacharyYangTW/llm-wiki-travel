#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import io
import re
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_coordinates(md_content):
    """從 markdown 檔案提取座標"""
    match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', md_content)
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except:
            return None
    return None

def find_nearest_city(coords, cities_dict):
    """找最近的城市"""
    if not coords:
        return None

    lng, lat = coords
    min_dist = float('inf')
    nearest_city = None

    for city, (city_lng, city_lat) in cities_dict.items():
        dist = ((lng - city_lng) ** 2 + (lat - city_lat) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest_city = city

    return nearest_city

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
germany_path = wiki_path / '德國'

print("=" * 80)
print("修正德國誤分類檔案")
print("=" * 80)

# Bavaria → 奧地利
print("\n[1] 德國/Bavaria → 奧地利 (薩爾茨堡、哈爾施塔特等)")
print("-" * 80)

AUSTRIA_CITIES = {
    'Salzburg': (13.0455, 47.8095),
    'Hallstatt': (13.6491, 47.5626),
    'Bad Ischl': (13.6276, 47.7121),
    'Hallein': (13.0993, 47.6850),
}

bavaria_poi = germany_path / 'Bavaria' / 'POI'
if bavaria_poi.exists():
    moved = 0
    for md_file in bavaria_poi.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        coords = extract_coordinates(content)

        city = find_nearest_city(coords, AUSTRIA_CITIES)
        if not city:
            city = 'Salzburg'  # 預設薩爾茨堡

        target_folder = wiki_path / '奧地利' / city
        target_folder.mkdir(parents=True, exist_ok=True)
        target_file = target_folder / md_file.name

        shutil.move(str(md_file), str(target_file))
        print(f"✓ {md_file.name[:40]:40} → {city}")
        moved += 1

    if not any(bavaria_poi.glob('*.md')):
        bavaria_poi.rmdir()

    print(f"✓ 移動 {moved} 個檔案")

# North Rhine-Westphalia → 荷蘭
print("\n[2] 德國/North Rhine-Westphalia → 荷蘭/羊角村")
print("-" * 80)

nrw_poi = germany_path / 'North Rhine-Westphalia' / 'POI'
if nrw_poi.exists():
    target_folder = wiki_path / '荷蘭' / '羊角村'
    target_folder.mkdir(parents=True, exist_ok=True)

    moved = 0
    for md_file in nrw_poi.glob('*.md'):
        target_file = target_folder / md_file.name
        shutil.move(str(md_file), str(target_file))
        print(f"✓ {md_file.name[:40]:40} → 羊角村")
        moved += 1

    if not any(nrw_poi.glob('*.md')):
        nrw_poi.rmdir()

    print(f"✓ 移動 {moved} 個檔案")

# Saarland → 盧森堡
print("\n[3] 德國/Saarland → 盧森堡")
print("-" * 80)

saarland_poi = germany_path / 'Saarland' / 'POI'
if saarland_poi.exists():
    target_folder = wiki_path / '盧森堡' / 'Luxembourg City'
    target_folder.mkdir(parents=True, exist_ok=True)

    moved = 0
    for md_file in saarland_poi.glob('*.md'):
        target_file = target_folder / md_file.name
        shutil.move(str(md_file), str(target_file))
        print(f"✓ {md_file.name[:40]:40} → Luxembourg City")
        moved += 1

    if not any(saarland_poi.glob('*.md')):
        saarland_poi.rmdir()

    print(f"✓ 移動 {moved} 個檔案")

# Saxony → 捷克/布拉格
print("\n[4] 德國/Saxony → 捷克/布拉格")
print("-" * 80)

saxony_poi = germany_path / 'Saxony' / 'POI'
if saxony_poi.exists():
    target_folder = wiki_path / '捷克' / '布拉格'
    target_folder.mkdir(parents=True, exist_ok=True)

    moved = 0
    for md_file in saxony_poi.glob('*.md'):
        target_file = target_folder / md_file.name
        shutil.move(str(md_file), str(target_file))
        print(f"✓ {md_file.name[:40]:40} → 布拉格")
        moved += 1

    if not any(saxony_poi.glob('*.md')):
        saxony_poi.rmdir()

    print(f"✓ 移動 {moved} 個檔案")

# 刪除空的德國目錄
print("\n[5] 清理德國目錄")
print("-" * 80)

for region in ['Bavaria', 'North Rhine-Westphalia', 'Saarland', 'Saxony']:
    region_path = germany_path / region
    if region_path.exists() and not any(region_path.rglob('*.md')):
        shutil.rmtree(str(region_path))
        print(f"✓ 刪除空目錄: 德國/{region}")

if germany_path.exists() and not any(germany_path.rglob('*.md')):
    shutil.rmtree(str(germany_path))
    print(f"✓ 刪除空目錄: 德國")

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
