#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證和修復台灣檔案位置
根據座標判斷檔案是否在正確的縣市/鄉鎮市區目錄
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

# 導入台灣城市座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from taiwan_cities_coords import TAIWAN_COUNTIES_COORDS, TAIWAN_DISTRICTS_COORDS, get_nearest_county, get_nearest_district

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

def scan_taiwan_files():
    """掃描台灣目錄下的所有檔案"""
    files_info = []
    taiwan_path = os.path.join(WIKI_BASE, "台灣")

    if not os.path.isdir(taiwan_path):
        return files_info

    for county_name in sorted(os.listdir(taiwan_path)):
        county_path = os.path.join(taiwan_path, county_name)
        if not os.path.isdir(county_path):
            continue

        for district_name in sorted(os.listdir(county_path)):
            district_path = os.path.join(county_path, district_name)

            if district_name.endswith('.md'):
                # 直接在縣市目錄下
                coords = extract_coordinates(district_path)
                files_info.append({
                    'file': district_name,
                    'path': district_path,
                    'coords': coords,
                    'current_county': county_name,
                    'current_district': None,
                    'is_direct': True
                })
            elif os.path.isdir(district_path):
                # 在鄉鎮市區子目錄下
                for file_name in os.listdir(district_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(district_path, file_name)
                        coords = extract_coordinates(file_path)
                        files_info.append({
                            'file': file_name,
                            'path': file_path,
                            'coords': coords,
                            'current_county': county_name,
                            'current_district': district_name,
                            'is_direct': False
                        })

    return files_info

def determine_correct_location(coords):
    """根據座標確定正確的縣市和鄉鎮市區"""
    if coords is None:
        return None, None

    county = get_nearest_county(coords)
    if county is None:
        return None, None

    district = get_nearest_district(coords, county)
    return county, district

print("=" * 80)
print("🔧 台灣檔案位置驗證和修復")
print("=" * 80)

print("\n🔍 掃描台灣目錄下的所有檔案...")
all_files = scan_taiwan_files()
print(f"   發現 {len(all_files)} 個檔案")

# 統計結果
correct_location = []
wrong_location = []
no_coords = []
outside_taiwan = []

print(f"\n📍 驗證座標與位置的對應性...\n")

for idx, file_info in enumerate(all_files, 1):
    county = file_info['current_county']
    district = file_info['current_district']
    coords = file_info['coords']
    file_name = file_info['file']

    if coords is None:
        no_coords.append(file_info)
        if idx % 100 == 0:
            print(f"   [{idx}/{len(all_files)}] ⊘ {county}/{district or '根目錄'}/{file_name[:40]:40} - 無座標")
    else:
        correct_county, correct_district = determine_correct_location(coords)

        if correct_county is None:
            outside_taiwan.append(file_info)
            if idx % 100 == 0:
                print(f"   [{idx}/{len(all_files)}] ⊘ {county}/{district or '根目錄'}/{file_name[:40]:40} - 座標超出台灣")
        elif county == correct_county and district == correct_district:
            correct_location.append(file_info)
        else:
            wrong_location.append({
                **file_info,
                'correct_county': correct_county,
                'correct_district': correct_district
            })
            print(f"✗ {county}/{district or '根目錄'}/{file_name[:40]:40}")
            print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f}")
            print(f"  應該: {correct_county}/{correct_district}")
            print()

print(f"\n{'='*80}")
print(f"📊 驗證結果")
print(f"{'='*80}\n")

print(f"✓ 位置正確:       {len(correct_location):5d} 個")
print(f"✗ 位置不對:       {len(wrong_location):5d} 個")
print(f"⊘ 沒有座標:       {len(no_coords):5d} 個")
print(f"⊙ 超出台灣:       {len(outside_taiwan):5d} 個")
print(f"─────────────────────")
print(f"  總計:           {len(all_files):5d} 個")

# 開始修復
if wrong_location:
    print(f"\n{'='*80}")
    print(f"🔧 開始修復位置錯誤的檔案")
    print(f"{'='*80}\n")

    total_moved = 0
    total_errors = 0
    errors_list = []

    for idx, file_info in enumerate(wrong_location, 1):
        file_name = file_info['file']
        from_path = file_info['path']
        to_county = file_info['correct_county']
        to_district = file_info['correct_district']
        coords = file_info['coords']

        # 建立目標目錄
        if to_district:
            to_dir = os.path.join(WIKI_BASE, "台灣", to_county, to_district)
        else:
            to_dir = os.path.join(WIKI_BASE, "台灣", to_county)

        os.makedirs(to_dir, exist_ok=True)
        to_path = os.path.join(to_dir, file_name)

        try:
            # 移動檔案
            shutil.move(from_path, to_path)
            total_moved += 1
            if idx % 50 == 0 or idx == 1:
                print(f"[{idx:4d}/{len(wrong_location)}] ✓ {file_name[:40]:40}")
                print(f"         → {to_county}/{to_district} (座標: {coords[0]:.4f}, {coords[1]:.4f})")
        except Exception as e:
            total_errors += 1
            errors_list.append(f"{file_name}: {str(e)}")
            print(f"[{idx:4d}/{len(wrong_location)}] ✗ {file_name[:40]:40}")
            print(f"         錯誤: {str(e)[:60]}")

    print(f"\n{'='*80}")
    print(f"✅ 修復完成")
    print(f"   移動: {total_moved} 個檔案")
    if total_errors > 0:
        print(f"   錯誤: {total_errors} 個")
        if errors_list:
            print(f"\n   錯誤列表:")
            for err in errors_list[:10]:
                print(f"     - {err}")
            if len(errors_list) > 10:
                print(f"     ... 還有 {len(errors_list) - 10} 個錯誤")
    print(f"{'='*80}")
else:
    print(f"\n{'='*80}")
    print(f"✅ 所有檔案位置都正確，無需修復")
    print(f"{'='*80}")

# 清理空目錄
print(f"\n🗑️  清理空目錄...")
taiwan_path = os.path.join(WIKI_BASE, "台灣")
removed_dirs = 0

for county_name in os.listdir(taiwan_path):
    county_path = os.path.join(taiwan_path, county_name)
    if not os.path.isdir(county_path):
        continue

    for district_name in os.listdir(county_path):
        district_path = os.path.join(county_path, district_name)
        if os.path.isdir(district_path):
            if not os.listdir(district_path):  # 空目錄
                try:
                    os.rmdir(district_path)
                    removed_dirs += 1
                except:
                    pass

if removed_dirs > 0:
    print(f"   已移除 {removed_dirs} 個空目錄")
else:
    print(f"   無空目錄")
