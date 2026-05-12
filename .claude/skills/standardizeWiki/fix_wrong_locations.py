#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐個修復位置錯誤的檔案
"""

import os
import sys
import re
import shutil
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 導入日本市町村座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
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

def find_wrong_locations():
    """找出所有位置錯誤的檔案"""
    wrong_files = []
    japan_path = os.path.join(WIKI_BASE, "日本")

    if not os.path.isdir(japan_path):
        return wrong_files

    for pref_name in sorted(os.listdir(japan_path)):
        pref_path = os.path.join(japan_path, pref_name)
        if not os.path.isdir(pref_path):
            continue

        for city_name in sorted(os.listdir(pref_path)):
            city_path = os.path.join(pref_path, city_name)
            if not os.path.isdir(city_path):
                continue

            for file_name in os.listdir(city_path):
                if not file_name.endswith('.md'):
                    continue

                file_path = os.path.join(city_path, file_name)
                coords = extract_coordinates(file_path)

                if coords is None:
                    continue

                # 根據座標找到應該所在的位置
                correct_pref, correct_city = None, None
                for p in JAPAN_TOWNS_COORDS.keys():
                    t = get_nearest_town(coords, p)
                    if t:
                        correct_pref = p
                        correct_city = t
                        break

                # 檢查是否位置錯誤
                if correct_pref and correct_city:
                    if pref_name != correct_pref or city_name != correct_city:
                        wrong_files.append({
                            'file': file_name,
                            'path': file_path,
                            'coords': coords,
                            'from_pref': pref_name,
                            'from_city': city_name,
                            'to_pref': correct_pref,
                            'to_city': correct_city
                        })

    return wrong_files

print("=" * 80)
print("🔧 修復位置錯誤的檔案")
print("=" * 80)

print("\n🔍 掃描位置錯誤的檔案...")
wrong_files = find_wrong_locations()
print(f"   發現 {len(wrong_files)} 個位置錯誤的檔案")

# 按「從」的位置分組
by_from_location = defaultdict(list)
for item in wrong_files:
    key = (item['from_pref'], item['from_city'])
    by_from_location[key].append(item)

# 逐個處理每個源位置
print(f"\n{'='*80}")
print(f"🔧 開始修復")
print(f"{'='*80}\n")

total_moved = 0
total_errors = 0
errors_list = []

for idx, (from_key, files) in enumerate(sorted(by_from_location.items()), 1):
    from_pref, from_city = from_key
    print(f"[{idx}/{len(by_from_location)}] {from_pref}/{from_city} ({len(files)} 個檔案)\n")

    for file_info in files:
        file_name = file_info['file']
        from_path = file_info['path']
        to_pref = file_info['to_pref']
        to_city = file_info['to_city']
        coords = file_info['coords']

        # 建立目標目錄
        to_dir = os.path.join(WIKI_BASE, "日本", to_pref, to_city)
        os.makedirs(to_dir, exist_ok=True)

        to_path = os.path.join(to_dir, file_name)

        try:
            # 移動檔案
            shutil.move(from_path, to_path)
            total_moved += 1
            print(f"   ✓ {file_name[:50]:50}")
            print(f"     {to_pref}/{to_city} (座標: {coords[0]:.4f}, {coords[1]:.4f})")
        except Exception as e:
            total_errors += 1
            errors_list.append(f"{from_pref}/{from_city}/{file_name}: {str(e)}")
            print(f"   ✗ {file_name[:50]:50}")
            print(f"     錯誤: {str(e)[:60]}")

    print()

print(f"\n{'='*80}")
print(f"✅ 修復完成")
print(f"   移動: {total_moved} 個檔案")
if total_errors > 0:
    print(f"   錯誤: {total_errors} 個")
    print(f"\n   錯誤列表:")
    for err in errors_list[:10]:
        print(f"     - {err}")
    if len(errors_list) > 10:
        print(f"     ... 還有 {len(errors_list) - 10} 個錯誤")
print(f"{'='*80}")
