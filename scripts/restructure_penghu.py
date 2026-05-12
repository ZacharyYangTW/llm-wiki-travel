#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
澎湖縣二級城市結構重新組織
根據座標將檔案分類到鄉鎮市
"""

import os
import sys
import re
import shutil
import math
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 澎湖縣鄉鎮市中心座標
PENGHU_TOWNS = {
    "馬公市": (119.5683, 23.5670),
    "湖西鄉": (119.6200, 23.6200),
    "白沙鎮": (119.5900, 23.6700),
    "西嶼鄉": (119.5200, 23.6800),
    "望安鄉": (119.4700, 23.6200),
    "七美鄉": (119.4400, 23.5500),
}

def extract_coordinates(file_path):
    """提取檔案座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', content)
            if match:
                return float(match.group(1)), float(match.group(2))
    except:
        pass
    return None

def find_nearest_town(coords):
    """根據座標找最近的鄉鎮"""
    if not coords:
        return "馬公市"  # 預設

    lng, lat = coords
    min_dist = float('inf')
    nearest = "馬公市"

    for town, (town_lng, town_lat) in PENGHU_TOWNS.items():
        dist = math.sqrt((lng - town_lng)**2 + (lat - town_lat)**2)
        if dist < min_dist:
            min_dist = dist
            nearest = town

    return nearest

print("=" * 80)
print("澎湖縣二級城市結構重新組織")
print("=" * 80)

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
penghu_path = wiki_path / '台灣' / '澎湖縣'

if not penghu_path.exists():
    print("❌ 澎湖縣目錄不存在")
    sys.exit(1)

print(f"\n掃描 {penghu_path}")
print("-" * 80)

# 統計
moved = 0
no_coords = []

# 重新組織檔案
for md_file in penghu_path.glob('*.md'):
    coords = extract_coordinates(md_file)
    town = find_nearest_town(coords)

    # 建立鄉鎮目錄
    town_dir = penghu_path / town
    town_dir.mkdir(parents=True, exist_ok=True)

    # 移動檔案
    target_file = town_dir / md_file.name
    shutil.move(str(md_file), str(target_file))

    status = "✓" if coords else "⚠"
    print(f"{status} {md_file.name[:40]:40} → {town}")

    if not coords:
        no_coords.append(md_file.name)

    moved += 1

print("\n" + "=" * 80)
print(f"✅ 完成: {moved} 個檔案")
print("=" * 80)

print("\n澎湖縣二級結構:")
for town in sorted(PENGHU_TOWNS.keys()):
    town_dir = penghu_path / town
    if town_dir.exists():
        count = len(list(town_dir.glob('*.md')))
        print(f"  {town}: {count} 檔案")

if no_coords:
    print(f"\n⚠️ 無座標檔案 ({len(no_coords)} 個):")
    for f in no_coords[:5]:
        print(f"  • {f}")
    if len(no_coords) > 5:
        print(f"  ... 還有 {len(no_coords) - 5} 個")
