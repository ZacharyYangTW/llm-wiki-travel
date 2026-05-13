#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正德里資料夾中的所有誤分類檔案
根據坐標判斷真實位置
"""

import os
import sys
import re
import shutil
import math
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\印度"
DELHI_PATH = os.path.join(WIKI_BASE, '德里')

# 印度主要城市坐標
CITY_CENTERS = {
    '德里': (77.2090, 28.6139),
    '孟買': (72.8479, 19.0760),
    '加爾各答': (88.3626, 22.5726),
    '清奈': (80.2707, 13.0827),
}

COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

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

def find_nearest_city(lng, lat):
    """找最近的城市"""
    min_dist = float('inf')
    best_city = None

    for city_name, (c_lng, c_lat) in CITY_CENTERS.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            best_city = city_name

    return best_city

print("=" * 70, flush=True)
print("🔧 修正德里資料夾中的誤分類檔案", flush=True)
print("=" * 70, flush=True)

# 列出德里的所有檔案
files = [f for f in os.listdir(DELHI_PATH)
         if f.endswith('.md') and os.path.isfile(os.path.join(DELHI_PATH, f))]

print(f"\n掃描 {len(files)} 個檔案...\n", flush=True)

moved = 0
no_coords = 0
correct_location = 0
failed = []

for filename in sorted(files):
    file_path = os.path.join(DELHI_PATH, filename)

    # 提取坐標
    lng, lat = extract_coordinates(file_path)

    if lng is None or lat is None:
        no_coords += 1
        print(f"⚠️  {filename[:50]:<50} [無坐標]", flush=True)
        continue

    # 判斷應該在哪個城市
    city = find_nearest_city(lng, lat)

    if city == '德里':
        correct_location += 1
        print(f"✓ {filename[:50]:<50} [德里 正確]", flush=True)
        continue

    # 移動到正確的城市
    target_dir = os.path.join(WIKI_BASE, city)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, filename)

    if os.path.exists(target_file):
        os.remove(target_file)

    try:
        shutil.move(file_path, target_file)
        moved += 1
        print(f"✓ {filename[:45]:<45} → {city}", flush=True)
    except Exception as e:
        failed.append((filename, str(e)[:30]))
        print(f"❌ {filename[:45]:<45} {str(e)[:30]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個檔案", flush=True)
print(f"  正確位置: {correct_location} 個檔案", flush=True)
print(f"  無坐標: {no_coords} 個檔案", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
