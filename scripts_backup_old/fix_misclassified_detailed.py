#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import sys
import io
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

def euclidean_distance(coords1, coords2):
    """計算兩點間的歐幾里得距離"""
    return ((coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2)**0.5

# 城市座標（用來找最近的城市）
CITY_MAPPINGS = {
    '西班牙': {
        'Madrid': (-3.7038, 40.4168),
        'Catalonia': (2.0, 41.5),
    },
    '荷蘭': {
        'Amsterdam': (4.8952, 52.3676),
        'Rotterdam': (4.4699, 51.9225),
        'Utrecht': (5.1214, 52.0907),
    },
    '紐西蘭': {
        'Auckland': (174.8860, -37.0082),
        'Christchurch': (172.6362, -43.5321),
    },
    '盧森堡': {
        'Luxembourg City': (6.1296, 49.6116),
    },
    '澳洲': {
        'Tasmania': (147.3, -42.8),  # Hobart area
    },
    '泰國': {
        'Bangkok': (100.5018, 13.7563),
        'Nakhon Phanom': (104.7748, 17.4049),
    },
}

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

# 定義要修正的資料夾
FIXES = {
    '西班牙': {
        '紐約': lambda coords: 'Madrid' if coords[0] < 0 else None,
    },
    '荷蘭': {
        '紐約': lambda coords: (
            'Amsterdam' if 4.85 <= coords[0] <= 4.92 and 52.33 <= coords[1] <= 52.39
            else 'Rotterdam' if 4.40 <= coords[0] <= 4.45 and 51.90 <= coords[1] <= 51.95
            else None
        ),
    },
    '紐西蘭': {
        '台南市': lambda coords: 'Christchurch' if 170 <= coords[0] <= 173 and -44 <= coords[1] <= -42 else None,
    },
    '盧森堡': {
        '紐約': lambda coords: 'Luxembourg City',
    },
    '澳洲': {
        '台南市': lambda coords: 'Tasmania' if 147 <= coords[0] <= 149 and -43 <= coords[1] <= -40 else None,
    },
    '泰國': {
        '澳門': lambda coords: (
            'Bangkok' if 100 <= coords[0] <= 101 and 13 <= coords[1] <= 14
            else 'Nakhon Phanom' if 104 <= coords[0] <= 106 and 16 <= coords[1] <= 18
            else None
        ),
    },
}

print("=" * 80)
print("修正誤分類檔案")
print("=" * 80)

all_moves = []

for country, folders in FIXES.items():
    country_path = wiki_path / country

    if not country_path.exists():
        print(f"\n❌ {country}: 資料夾不存在")
        continue

    print(f"\n{country}")

    for wrong_folder, destination_func in folders.items():
        wrong_path = country_path / wrong_folder

        if not wrong_path.exists():
            print(f"  {wrong_folder}: 不存在")
            continue

        files = list(wrong_path.glob('*.md'))

        for md_file in files:
            try:
                content = md_file.read_text(encoding='utf-8')
                coords = extract_coordinates(content)

                if coords:
                    destination = destination_func(coords)

                    if destination:
                        target_folder = country_path / destination
                        target_folder.mkdir(parents=True, exist_ok=True)

                        target_file = target_folder / md_file.name

                        print(f"  ✓ {wrong_folder} → {destination}: {md_file.name}")

                        shutil.move(str(md_file), str(target_file))

                        all_moves.append({
                            'file': md_file.name,
                            'from': wrong_folder,
                            'to': destination,
                            'country': country,
                        })
                    else:
                        print(f"  ⚠ {md_file.name}: 無法判斷目標位置")
                else:
                    print(f"  ⚠ {md_file.name}: 無座標")

            except Exception as e:
                print(f"  ❌ {md_file.name}: {e}")

# 刪除空的誤分類資料夾
print("\n" + "=" * 80)
print("刪除空的誤分類資料夾")
print("=" * 80)

for country, folders in FIXES.items():
    country_path = wiki_path / country

    for folder in folders.keys():
        folder_path = country_path / folder

        if folder_path.exists():
            if not any(folder_path.glob('*.md')):
                print(f"  ✓ 刪除 {country}/{folder}")
                folder_path.rmdir()
            else:
                remaining = list(folder_path.glob('*.md'))
                print(f"  ⚠ {country}/{folder}: 仍有 {len(remaining)} 個檔案")

print("\n" + "=" * 80)
print(f"完成：移動 {len(all_moves)} 個檔案")
print("=" * 80)
