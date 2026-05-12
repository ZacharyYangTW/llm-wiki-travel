#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 2,757 個 Wiki Only 檔案是否在正確的資料夾
根據座標判斷檔案是否應該在當前目錄
"""

import os
import sys
import re
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

def get_wiki_cities():
    """獲取 Wiki 中所有日本二級目錄和其檔案"""
    cities = []
    japan_path = os.path.join(WIKI_BASE, "日本")

    if not os.path.isdir(japan_path):
        return cities

    for pref_name in sorted(os.listdir(japan_path)):
        pref_path = os.path.join(japan_path, pref_name)
        if not os.path.isdir(pref_path):
            continue

        for city_name in sorted(os.listdir(pref_path)):
            city_path = os.path.join(pref_path, city_name)
            if os.path.isdir(city_path):
                # 獲取該市町村下的所有檔案
                for file_name in os.listdir(city_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(city_path, file_name)
                        coords = extract_coordinates(file_path)

                        cities.append({
                            'pref': pref_name,
                            'city': city_name,
                            'file': file_name,
                            'path': file_path,
                            'coords': coords
                        })

    return cities

print("=" * 80)
print("✓ 驗證 Wiki Only 檔案的位置")
print("=" * 80)

print("\n📄 掃描所有日本檔案...")
all_files = get_wiki_cities()
print(f"   總計: {len(all_files)} 個檔案")

# 統計結果
correct_location = []  # 座標符合當前位置
wrong_location = []    # 座標不符合當前位置
no_coords = []         # 沒有座標

print(f"\n📍 驗證座標與位置的對應性...\n")

for file_info in all_files:
    pref = file_info['pref']
    city = file_info['city']
    coords = file_info['coords']

    if coords is None:
        no_coords.append(file_info)
        print(f"⊘ {pref}/{city}/{file_info['file'][:40]:40} - 無座標")
    else:
        # 根據座標找到應該所在的市町村
        correct_pref, correct_city = None, None
        for p in JAPAN_TOWNS_COORDS.keys():
            t = get_nearest_town(coords, p)
            if t:
                correct_pref = p
                correct_city = t
                break

        if correct_pref and correct_city:
            # 檢查座標是否符合當前位置
            if pref == correct_pref and city == correct_city:
                correct_location.append(file_info)
                # 正確位置不輸出
            else:
                wrong_location.append({
                    **file_info,
                    'correct_pref': correct_pref,
                    'correct_city': correct_city
                })
                print(f"✗ {pref}/{city}/{file_info['file'][:40]:40}")
                print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f}")
                print(f"  應該: {correct_pref}/{correct_city}")
                print()

print(f"\n{'='*80}")
print(f"📊 驗證結果")
print(f"{'='*80}\n")

print(f"✓ 位置正確:     {len(correct_location):5d} 個")
print(f"✗ 位置不對:     {len(wrong_location):5d} 個")
print(f"⊘ 沒有座標:     {len(no_coords):5d} 個")
print(f"─────────────────────")
print(f"  總計:         {len(all_files):5d} 個")

# 詳細列出位置不對的檔案（按都道府縣分組）
if wrong_location:
    print(f"\n{'='*80}")
    print(f"🔴 位置錯誤的檔案清單（前 50 個）")
    print(f"{'='*80}\n")

    by_from_pref = defaultdict(list)
    for item in wrong_location:
        key = f"{item['pref']}/{item['city']}"
        by_from_pref[key].append(item)

    count = 0
    for location in sorted(by_from_pref.keys()):
        items = by_from_pref[location]
        print(f"\n{location} ({len(items)} 個)")
        for item in items[:5]:
            print(f"  → {item['correct_pref']}/{item['correct_city']}")
            print(f"     {item['file'][:60]}")
            if item['coords']:
                print(f"     座標: {item['coords'][0]:.4f}, {item['coords'][1]:.4f}")
            count += 1
            if count >= 50:
                break
        if count >= 50:
            print(f"\n  ... 還有 {len(wrong_location) - 50} 個")
            break

print(f"\n{'='*80}")
