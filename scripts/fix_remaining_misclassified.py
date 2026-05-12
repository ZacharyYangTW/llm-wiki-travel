#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import sys
import io
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

def determine_country_from_coords(coords):
    """根據座標判斷國家"""
    if coords is None:
        return None

    lng, lat = coords

    # 美國 (-125 ~ -66, 24 ~ 49)
    if -125 <= lng <= -66 and 24 <= lat <= 49:
        return '美國'

    # 加拿大 (-141 ~ -52, 42 ~ 83)
    if -141 <= lng <= -52 and 42 <= lat <= 83:
        return '加拿大'

    # 奧地利 (10 ~ 17, 47 ~ 49)
    if 10 <= lng <= 17 and 47 <= lat <= 49:
        return '奧地利'

    # 越南 (102 ~ 110, 8 ~ 24)
    if 102 <= lng <= 110 and 8 <= lat <= 24:
        return '越南'

    return None

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

print("=" * 80)
print("修正剩餘的誤分類檔案")
print("=" * 80)

# 1. 加拿大/舊金山 → 根據座標分類
print("\n1. 加拿大/舊金山:")
sf_path = wiki_path / '加拿大' / '舊金山'
moved = {'美國': 0, '加拿大': 0}

if sf_path.exists():
    for md_file in sf_path.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            if coords:
                actual_country = determine_country_from_coords(coords)

                if actual_country and actual_country != '加拿大':
                    target_path = wiki_path / actual_country / '舊金山'
                    target_path.mkdir(parents=True, exist_ok=True)

                    target_file = target_path / md_file.name
                    shutil.move(str(md_file), str(target_file))

                    moved[actual_country] += 1
                    if moved[actual_country] <= 3:
                        print(f"  ✓ {md_file.name} → {actual_country}/舊金山")
                else:
                    moved['加拿大'] += 1

        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

    print(f"  移至美國: {moved['美國']} 個檔案")
    print(f"  保留加拿大: {moved['加拿大']} 個檔案")

# 2. 捷克/紐約 → 奧地利/維也納
print("\n2. 捷克/紐約:")
czech_ny = wiki_path / '捷克' / '紐約'

if czech_ny.exists():
    for md_file in czech_ny.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            if coords:
                actual_country = determine_country_from_coords(coords)

                if actual_country == '奧地利':
                    target_path = wiki_path / '奧地利' / 'Vienna'
                    target_path.mkdir(parents=True, exist_ok=True)

                    target_file = target_path / md_file.name
                    shutil.move(str(md_file), str(target_file))

                    print(f"  ✓ {md_file.name} → 奧地利/Vienna")

        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

# 3. 柬埔寨/澳門 → 越南
print("\n3. 柬埔寨/澳門:")
cambodia_macau = wiki_path / '柬埔寨' / '澳門'

if cambodia_macau.exists():
    for md_file in cambodia_macau.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            if coords:
                actual_country = determine_country_from_coords(coords)

                if actual_country == '越南':
                    target_city = 'Ho Chi Minh City'
                    if '河內' in content or 'Hanoi' in md_file.name:
                        target_city = 'Hanoi'

                    target_path = wiki_path / '越南' / target_city
                    target_path.mkdir(parents=True, exist_ok=True)

                    target_file = target_path / md_file.name
                    shutil.move(str(md_file), str(target_file))

                    print(f"  ✓ {md_file.name} → 越南/{target_city}")

        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

# 清理空資料夾
print("\n" + "=" * 80)
print("清理空資料夾")
print("=" * 80)

for folder_path in [sf_path, czech_ny, cambodia_macau]:
    if folder_path.exists() and not any(folder_path.glob('*.md')):
        print(f"  ✓ 刪除 {folder_path.parent.name}/{folder_path.name}")
        folder_path.rmdir()

print("\n完成")
