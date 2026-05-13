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

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
peru_path = wiki_path / '秘魯'
chile_path = wiki_path / '智利'

print("=" * 80)
print("修正秘魯誤分類檔案")
print("=" * 80)

# 修正秘魯/洛杉磯 → 智利（復活節島）
print("\n秘魯/洛杉磯 → 智利:")
los_angeles_path = peru_path / '洛杉磯'

if los_angeles_path.exists():
    for md_file in los_angeles_path.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            # 復活節島座標範圍: (-109.5 ~ -109.2, -27.2 ~ -27.0)
            is_easter_island = False
            if coords:
                lng, lat = coords
                if -109.6 <= lng <= -109.1 and -27.3 <= lat <= -26.9:
                    is_easter_island = True

            if is_easter_island or 'Easter Island' in md_file.name or 'Rapa Nui' in md_file.name or 'Ahu' in md_file.name or 'Moai' in md_file.name:
                target_city = 'Easter Island'
                target_folder = chile_path / target_city
                target_folder.mkdir(parents=True, exist_ok=True)

                target_file = target_folder / md_file.name

                print(f"  ✓ {md_file.name}")
                print(f"    座標: {coords}")

                shutil.move(str(md_file), str(target_file))
            else:
                print(f"  ⚠ {md_file.name}: 無法確定目標城市")

        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

# 修正秘魯/紐約 → 秘魯/Cusco
print("\n秘魯/紐約 → 秘魯/Cusco:")
newyork_path = peru_path / '紐約'

if newyork_path.exists():
    for md_file in newyork_path.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            # 根據檔案名判斷
            if 'Ollantaytambo' in md_file.name or 'Fortaleza' in md_file.name:
                target_city = 'Cusco'
                target_folder = peru_path / target_city
                target_folder.mkdir(parents=True, exist_ok=True)

                target_file = target_folder / md_file.name

                print(f"  ✓ {md_file.name} → {target_city}")
                print(f"    座標: {coords}")

                shutil.move(str(md_file), str(target_file))
            else:
                print(f"  ⚠ {md_file.name}: 無法確定目標城市")

        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

# 刪除空的誤分類資料夾
print("\n" + "=" * 80)
print("刪除空的誤分類資料夾")
print("=" * 80)

for folder_path in [los_angeles_path, newyork_path]:
    if folder_path.exists():
        if not any(folder_path.glob('*.md')):
            print(f"  ✓ 刪除 {folder_path.name}")
            folder_path.rmdir()
        else:
            remaining = list(folder_path.glob('*.md'))
            print(f"  ⚠ {folder_path.name}: 仍有 {len(remaining)} 個檔案")

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
