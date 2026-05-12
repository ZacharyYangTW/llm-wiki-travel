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

# 比利時城市座標
BELGIAN_CITIES = {
    'Bruges': (3.2167, 51.2000),
    'Brussels': (4.3517, 50.8503),
    'Antwerp': (4.4000, 51.2000),
}

def determine_city(coords):
    """根據座標判斷城市"""
    lng, lat = coords

    # 布魯日 (3.21-3.22, 51.19-51.21)
    if 3.20 <= lng <= 3.23 and 51.18 <= lat <= 51.22:
        return 'Bruges'

    # 布魯塞爾 (4.35-4.42, 50.82-50.84)
    if 4.35 <= lng <= 4.43 and 50.81 <= lat <= 51.23:
        if lng > 4.39:
            return 'Antwerp'  # 更東邊可能是安特衛普
        return 'Brussels'

    return None

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
belgium_path = wiki_path / '比利時'
newyork_path = belgium_path / '紐約'

print("=" * 80)
print("修正比利時誤分類檔案")
print("=" * 80)

if newyork_path.exists():
    for md_file in newyork_path.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)

            if coords:
                city = determine_city(coords)

                if city:
                    target_folder = belgium_path / city
                    target_folder.mkdir(parents=True, exist_ok=True)

                    target_file = target_folder / md_file.name

                    print(f"  ✓ 紐約 → {city}: {md_file.name}")
                    print(f"    座標: {coords}")

                    shutil.move(str(md_file), str(target_file))
                else:
                    print(f"  ⚠ {md_file.name}: 無法判斷城市 {coords}")
            else:
                print(f"  ⚠ {md_file.name}: 無座標")

        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

# 刪除空的紐約資料夾
if newyork_path.exists():
    if not any(newyork_path.glob('*.md')):
        print(f"\n✓ 刪除比利時/紐約")
        newyork_path.rmdir()
    else:
        remaining = list(newyork_path.glob('*.md'))
        print(f"\n⚠ 比利時/紐約: 仍有 {len(remaining)} 個檔案")

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
