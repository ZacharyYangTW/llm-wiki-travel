#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據檔案座標重新分類日本都道府縣下的檔案
"""

import os
import sys
import shutil
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 導入日本市町村座標表
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

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

print("=" * 80)
print("🔄 根據座標重新分類日本都道府縣檔案")
print("=" * 80)

japan_path = os.path.join(WIKI_BASE, "日本")
total_moved = 0
total_checked = 0
errors = []

for pref_name in sorted(os.listdir(japan_path)):
    pref_path = os.path.join(japan_path, pref_name)
    if not os.path.isdir(pref_path):
        continue

    if pref_name not in JAPAN_TOWNS_COORDS:
        continue

    # 遍歷都道府縣下的所有子目錄
    for city_name in os.listdir(pref_path):
        city_path = os.path.join(pref_path, city_name)
        if not os.path.isdir(city_path):
            continue

        # 掃描這個市町村目錄下的所有 .md 檔案
        for file_name in os.listdir(city_path):
            file_path = os.path.join(city_path, file_name)
            if not os.path.isfile(file_path) or not file_name.endswith('.md'):
                continue

            total_checked += 1
            coords = extract_coordinates(file_path)

            if not coords:
                continue

            # 根據座標找到最接近的市町村
            nearest_town = get_nearest_town(coords, pref_name)

            if nearest_town and nearest_town != city_name:
                # 檔案應該被移到不同的市町村
                target_path = os.path.join(pref_path, nearest_town)
                os.makedirs(target_path, exist_ok=True)

                dst_path = os.path.join(target_path, file_name)
                try:
                    shutil.move(file_path, dst_path)
                    total_moved += 1
                    print(f"✓ {pref_name}/{city_name}/{file_name[:30]:30} → {nearest_town}/")
                except Exception as e:
                    errors.append(f"{file_name}: {str(e)}")

print(f"\n{'='*80}")
print(f"✅ 完成")
print(f"  檢查: {total_checked} 個檔案")
print(f"  移動: {total_moved} 個檔案")
if errors:
    print(f"  錯誤: {len(errors)} 個")
    for err in errors[:5]:
        print(f"    - {err}")
print(f"{'='*80}")
