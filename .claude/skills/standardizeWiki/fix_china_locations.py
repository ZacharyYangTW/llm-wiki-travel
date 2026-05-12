#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證和修復中國檔案位置
根據座標判斷檔案是否在正確的省份/城市目錄
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

# 導入中國城市座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from china_cities_coords import CHINA_PROVINCES_COORDS, CHINA_CITIES_COORDS, get_nearest_province, get_nearest_city

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

def scan_china_files():
    """掃描中國目錄下的所有檔案"""
    files_info = []
    china_path = os.path.join(WIKI_BASE, "中國")

    if not os.path.isdir(china_path):
        return files_info

    for prov_name in sorted(os.listdir(china_path)):
        prov_path = os.path.join(china_path, prov_name)
        if not os.path.isdir(prov_path):
            continue

        # 檢查該省份下是否直接有 .md 檔案（二級結構）
        for item_name in sorted(os.listdir(prov_path)):
            item_path = os.path.join(prov_path, item_name)

            if item_name.endswith('.md'):
                # 直接在省份目錄下
                coords = extract_coordinates(item_path)
                files_info.append({
                    'file': item_name,
                    'path': item_path,
                    'coords': coords,
                    'current_prov': prov_name,
                    'current_city': None,
                    'is_direct': True
                })
            elif os.path.isdir(item_path):
                # 在城市子目錄下
                for file_name in os.listdir(item_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(item_path, file_name)
                        coords = extract_coordinates(file_path)
                        files_info.append({
                            'file': file_name,
                            'path': file_path,
                            'coords': coords,
                            'current_prov': prov_name,
                            'current_city': item_name,
                            'is_direct': False
                        })

    return files_info

def determine_correct_location(coords):
    """根據座標確定正確的省份和城市"""
    if coords is None:
        return None, None

    prov = get_nearest_province(coords)
    if prov is None:
        return None, None

    # 澳門和香港不需要城市子目錄
    if prov in ["澳門", "香港"]:
        return prov, None

    city = get_nearest_city(coords, prov)
    return prov, city

print("=" * 80)
print("🔧 中國檔案位置驗證和修復")
print("=" * 80)

print("\n🔍 掃描中國目錄下的所有檔案...")
all_files = scan_china_files()
print(f"   發現 {len(all_files)} 個檔案")

# 統計結果
correct_location = []
wrong_location = []
no_coords = []
outside_china = []

print(f"\n📍 驗證座標與位置的對應性...\n")

for idx, file_info in enumerate(all_files, 1):
    prov = file_info['current_prov']
    city = file_info['current_city']
    coords = file_info['coords']
    file_name = file_info['file']

    if coords is None:
        no_coords.append(file_info)
        if idx % 100 == 0:
            print(f"   [{idx}/{len(all_files)}] ⊘ {prov}/{city or '根目錄'}/{file_name[:40]:40} - 無座標")
    else:
        correct_prov, correct_city = determine_correct_location(coords)

        if correct_prov is None:
            outside_china.append(file_info)
            if idx % 100 == 0:
                print(f"   [{idx}/{len(all_files)}] ⊘ {prov}/{city or '根目錄'}/{file_name[:40]:40} - 座標超出中國")
        elif prov == correct_prov and city == correct_city:
            correct_location.append(file_info)
        else:
            wrong_location.append({
                **file_info,
                'correct_prov': correct_prov,
                'correct_city': correct_city
            })
            print(f"✗ {prov}/{city or '根目錄'}/{file_name[:40]:40}")
            print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f}")
            print(f"  應該: {correct_prov}/{correct_city}")
            print()

print(f"\n{'='*80}")
print(f"📊 驗證結果")
print(f"{'='*80}\n")

print(f"✓ 位置正確:       {len(correct_location):5d} 個")
print(f"✗ 位置不對:       {len(wrong_location):5d} 個")
print(f"⊘ 沒有座標:       {len(no_coords):5d} 個")
print(f"⊙ 超出中國:       {len(outside_china):5d} 個")
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
        to_prov = file_info['correct_prov']
        to_city = file_info['correct_city']
        coords = file_info['coords']

        # 建立目標目錄
        if to_city:
            to_dir = os.path.join(WIKI_BASE, "中國", to_prov, to_city)
        else:
            to_dir = os.path.join(WIKI_BASE, "中國", to_prov)

        os.makedirs(to_dir, exist_ok=True)
        to_path = os.path.join(to_dir, file_name)

        try:
            # 移動檔案
            shutil.move(from_path, to_path)
            total_moved += 1
            if idx % 20 == 0 or idx == 1:
                print(f"[{idx:3d}/{len(wrong_location)}] ✓ {file_name[:40]:40}")
                print(f"         → {to_prov}/{to_city} (座標: {coords[0]:.4f}, {coords[1]:.4f})")
        except Exception as e:
            total_errors += 1
            errors_list.append(f"{file_name}: {str(e)}")
            print(f"[{idx:3d}/{len(wrong_location)}] ✗ {file_name[:40]:40}")
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
china_path = os.path.join(WIKI_BASE, "中國")
removed_dirs = 0

for prov_name in os.listdir(china_path):
    prov_path = os.path.join(china_path, prov_name)
    if not os.path.isdir(prov_path):
        continue

    for city_name in os.listdir(prov_path):
        city_path = os.path.join(prov_path, city_name)
        if os.path.isdir(city_path):
            if not os.listdir(city_path):  # 空目錄
                try:
                    os.rmdir(city_path)
                    removed_dirs += 1
                except:
                    pass

if removed_dirs > 0:
    print(f"   已移除 {removed_dirs} 個空目錄")
else:
    print(f"   無空目錄")
