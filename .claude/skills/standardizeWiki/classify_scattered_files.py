#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據座標將散落在都道府縣底層的檔案分類到市町村
"""

import os
import sys
import shutil
import re
import math
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 青森県的市町村座標（中心點）
AOMORI_TOWNS = {
    "弘前市": (139.548, 40.589),
    "八戸市": (141.497, 40.510),
    "深浦町": (140.458, 40.868),
}

def extract_coordinates(file_path):
    """從檔案的 frontmatter 提取座標"""
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

def calculate_distance(coord1, coord2):
    """計算兩個座標之間的歐氏距離"""
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def find_nearest_town(file_coords, towns):
    """找到最接近的市町村"""
    if not file_coords:
        return None

    min_distance = float('inf')
    nearest_town = None

    for town_name, town_coords in towns.items():
        distance = calculate_distance(file_coords, town_coords)
        if distance < min_distance:
            min_distance = distance
            nearest_town = town_name

    return nearest_town

# 掃描青森県
aomori_path = os.path.join(WIKI_BASE, "日本", "青森県")
if not os.path.isdir(aomori_path):
    print("❌ 青森県目錄不存在")
    sys.exit(1)

print("=" * 80)
print("🔍 掃描青森県散落檔案")
print("=" * 80)

scattered_files = []
for file_name in os.listdir(aomori_path):
    file_path = os.path.join(aomori_path, file_name)
    if os.path.isfile(file_path) and file_name.endswith('.md'):
        coords = extract_coordinates(file_path)
        if coords:
            nearest_town = find_nearest_town(coords, AOMORI_TOWNS)
            scattered_files.append({
                'name': file_name,
                'path': file_path,
                'coords': coords,
                'nearest_town': nearest_town
            })

print(f"\n發現 {len(scattered_files)} 個散落檔案\n")

# 按市町村分組
by_town = {}
for item in scattered_files:
    town = item['nearest_town']
    if town not in by_town:
        by_town[town] = []
    by_town[town].append(item)
    print(f"  {item['name'][:40]:40} → {town}")

# 移動檔案
print(f"\n{'='*80}")
print(f"🔧 開始分類檔案...")
print(f"{'='*80}\n")

for town, files in sorted(by_town.items()):
    town_path = os.path.join(aomori_path, town)
    os.makedirs(town_path, exist_ok=True)

    for item in files:
        try:
            dst = os.path.join(town_path, item['name'])
            shutil.move(item['path'], dst)
            print(f"✓ {item['name'][:40]:40} → {town}/")
        except Exception as e:
            print(f"❌ {item['name']}: {str(e)}")

print(f"\n{'='*80}")
print(f"✅ 完成! 分類了 {len(scattered_files)} 個檔案到 {len(by_town)} 個市町村")
print(f"{'='*80}")
