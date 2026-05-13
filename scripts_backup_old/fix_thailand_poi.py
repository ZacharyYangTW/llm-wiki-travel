#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import io
import re
from pathlib import Path

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

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

# 泰國城市座標
THAILAND_CITIES = {
    'Bangkok': (-100.5018, 13.7563),
    'Bangkok Noi': (-100.4935, 13.7442),
    'Chon Buri': (100.9833, 13.1939),
    'Lopburi': (100.7612, 14.8009),
    'Nakhon Phanom': (104.7744, 17.3822),
    'Phang Nga': (98.5281, 8.4264),
    'Phuket': (98.3923, 7.8804),
    'Rayong': (101.2833, 12.6833),
    'Samut Prakan': (100.5997, 13.5931),
    'Samut Sakhon': (100.3064, 13.5406),
    'Samut Songkhram': (100.0131, 13.0754),
}

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

print("=" * 80)
print("分類泰國 POI 檔案")
print("=" * 80)

thailand_poi = wiki_path / '泰國' / 'POI'
if thailand_poi.exists():
    for md_file in thailand_poi.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        coords = extract_coordinates(content)

        city = find_nearest_city(coords, THAILAND_CITIES)

        if city:
            target_folder = wiki_path / '泰國' / city
            target_folder.mkdir(parents=True, exist_ok=True)
            target_file = target_folder / md_file.name
            shutil.move(str(md_file), str(target_file))
            print(f"✓ {md_file.name}")
            print(f"  → {city} {coords}")
        else:
            print(f"⚠ {md_file.name}: 無法判斷城市")

    if not any(thailand_poi.glob('*.md')):
        thailand_poi.rmdir()
        print(f"\n✓ 刪除空的 泰國/POI 目錄")
else:
    print("✓ 泰國/POI 不存在")

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
