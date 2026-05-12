#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import io
import json
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

# 國家邊界（粗略） - 用於判斷檔案真正屬於哪個國家
COUNTRY_BOUNDS = {
    '中國': {'west': 73.5, 'east': 135.0, 'south': 18.2, 'north': 53.6},
    '台灣': {'west': 120.0, 'east': 122.0, 'south': 22.0, 'north': 25.0},
    '日本': {'west': 123.0, 'east': 145.0, 'south': 30.0, 'north': 45.0},
    '香港': {'west': 113.75, 'east': 114.3, 'south': 22.15, 'north': 22.6},
    '澳門': {'west': 113.5, 'east': 113.65, 'south': 22.1, 'north': 22.2},
    '泰國': {'west': 97.3, 'east': 105.6, 'south': 5.6, 'north': 20.5},
    '越南': {'west': 102.1, 'east': 109.5, 'south': 8.5, 'north': 23.4},
    '美國': {'west': -125.0, 'east': -66.0, 'south': 24.0, 'north': 49.4},
    '加拿大': {'west': -141.0, 'east': -52.0, 'south': 42.0, 'north': 83.0},
    '新加坡': {'west': 103.6, 'east': 104.9, 'south': 1.1, 'north': 1.5},
    '柬埔寨': {'west': 102.3, 'east': 107.6, 'south': 10.0, 'north': 14.7},
}

# 可疑資料夾 (國家, 可疑城市名)
SUSPICIOUS = [
    ('中國', '澳門'),
    ('加拿大', '舊金山'),
    ('台灣', '台南市'),
    ('捷克', '紐約'),
    ('新加坡', '澳門'),
    ('日本', '東京'),
    ('日本', '大阪'),
    ('日本', '京都'),
    ('柬埔寨', '澳門'),
    ('美國', '洛杉磯'),
]

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

print("=" * 80)
print("分析可疑檔案的實際位置")
print("=" * 80)

def is_in_country(coords, country):
    """檢查座標是否在國家邊界內"""
    if country not in COUNTRY_BOUNDS:
        return False

    lng, lat = coords
    bounds = COUNTRY_BOUNDS[country]

    return (bounds['west'] <= lng <= bounds['east'] and
            bounds['south'] <= lat <= bounds['north'])

# 掃描並分析
results = defaultdict(lambda: defaultdict(list))

for country, folder in SUSPICIOUS:
    folder_path = wiki_path / country / folder

    if not folder_path.exists():
        continue

    files = list(folder_path.glob('*.md'))

    print(f"\n{country}/{folder} ({len(files)} 個檔案):")

    for md_file in files[:5]:  # 只檢查前 5 個
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            if coords:
                actual_country = None

                # 檢查座標在哪個國家邊界內
                for country_name in COUNTRY_BOUNDS.keys():
                    if is_in_country(coords, country_name):
                        actual_country = country_name
                        break

                status = "✓" if actual_country == country else "❌"
                print(f"  {status} {md_file.name}")
                print(f"     座標: {coords} → {actual_country}")

                results[country][folder].append({
                    'file': md_file.name,
                    'coords': coords,
                    'actual_country': actual_country
                })

        except Exception as e:
            print(f"  ⚠ {md_file.name}: {e}")

print("\n" + "=" * 80)
print("分析完成")
print("=" * 80)
