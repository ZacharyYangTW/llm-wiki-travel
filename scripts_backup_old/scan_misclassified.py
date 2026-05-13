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

SUSPICIOUS_FOLDERS = {
    '西班牙': ['紐約'],
    '荷蘭': ['紐約'],
    '紐西蘭': ['台南市'],
    '祕魯': ['洛杉磯', '紐約'],
    '盧森堡': ['紐約'],
    '澳洲': ['台南市'],
    '泰國': ['澳門'],
    '比利時': ['紐約'],
}

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

print("=" * 80)
print("掃描誤分類資料夾")
print("=" * 80)

all_files = {}

for country, folders in SUSPICIOUS_FOLDERS.items():
    country_path = wiki_path / country

    if not country_path.exists():
        print(f"\n❌ {country}: 資料夾不存在")
        continue

    print(f"\n🇪🇸 {country}")

    for folder in folders:
        folder_path = country_path / folder

        if not folder_path.exists():
            print(f"  └─ {folder}: 不存在")
            continue

        files = list(folder_path.glob('*.md'))

        if not files:
            print(f"  └─ {folder}: 空資料夾")
            continue

        print(f"  └─ {folder}: {len(files)} 個檔案")

        for md_file in files:
            try:
                content = md_file.read_text(encoding='utf-8')
                coords = extract_coordinates(content)

                if coords:
                    lng, lat = coords
                    print(f"     • {md_file.name}")
                    print(f"       座標: ({lng}, {lat})")

                    # 儲存用於匯出
                    all_files[f"{country}/{folder}/{md_file.name}"] = coords
                else:
                    print(f"     • {md_file.name}: 無座標")
            except Exception as e:
                print(f"     • {md_file.name}: 錯誤 {e}")

# 匯出 JSON
print("\n" + "=" * 80)
print("匯出檔案清單: misclassified_files.json")
print("=" * 80)

with open('h:/我的雲端硬碟/llm_wiki_travel/misclassified_files.json', 'w', encoding='utf-8') as f:
    json.dump(all_files, f, ensure_ascii=False, indent=2)

print(f"✓ 共 {len(all_files)} 個檔案")
