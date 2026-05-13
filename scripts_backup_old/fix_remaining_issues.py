#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import io
import re
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

print("=" * 80)
print("修正剩餘問題")
print("=" * 80)

# 1. 日本徳島県 - 建立徳島市
print("\n[1] 日本徳島県 - 建立徳島市:")
print("-" * 80)
tokushima_prefecture = wiki_path / '日本' / '徳島県'
tokushima_city = tokushima_prefecture / '徳島市'

if tokushima_city.exists():
    print("✓ 徳島市已存在")
else:
    tokushima_city.mkdir(parents=True, exist_ok=True)
    print("✓ 建立 徳島市 目錄")

# 2. 印度/廣州 → 中國/廣東省/廣州市
print("\n[2] 印度/廣州 → 中國/廣東省/廣州市:")
print("-" * 80)
india_guangzhou = wiki_path / '印度' / '廣州'
china_guangzhou = wiki_path / '中國' / '廣東省' / '廣州市'

if india_guangzhou.exists():
    china_guangzhou.mkdir(parents=True, exist_ok=True)

    for md_file in india_guangzhou.glob('*.md'):
        target_file = china_guangzhou / md_file.name
        shutil.move(str(md_file), str(target_file))
        print(f"✓ 移動 {md_file.name}")

    india_guangzhou.rmdir()
    print(f"✓ 刪除空的 印度/廣州 目錄")
else:
    print("✓ 印度/廣州 不存在")

# 3. 泰國/POI 分類到正確城市
print("\n[3] 泰國/POI - 根據座標分類:")
print("-" * 80)

# 泰國城市座標
THAILAND_CITIES = {
    'Bangkok': (-100.5018, 13.7563),
    'Bangkok Noi': (-100.4935, 13.7442),
    'Chon Buri': (100.9833, 13.1939),
    'Lopburi': (100.7612, 14.8009),
    'Nakhon Phanom': (104.7744, 17.3822),
    'Phang Nga': (98.5281, 8.4264),
    'Phuket': (98.3923, 7.8804),
    'Rayong': (101.2833, 12.6833),
    'Samut Prakan': (100.5997, 13.5931),
    'Samut Sakhon': (100.3064, 13.5406),
    'Samut Songkhram': (100.0131, 13.0754),
}

def find_nearest_city(coords, cities_dict):
    """找最近的城市"""
    if not coords:
        return None

    lng, lat = coords
    min_dist = float('inf')
    nearest_city = None

    for city, (city_lng, city_lat) in cities_dict.items():
        dist = ((lng - city_lng) ** 2 + (lat - city_lat) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest_city = city

    return nearest_city

thailand_poi = wiki_path / '泰國' / 'POI'
if thailand_poi.exists():
    for md_file in thailand_poi.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        coords = extract_coordinates(content)

        city = find_nearest_city(coords, THAILAND_CITIES)

        if city:
            target_folder = wiki_path / '泰國' / city
            target_folder.mkdir(parents=True, exist_ok=True)
            target_file = target_folder / md_file.name
            shutil.move(str(md_file), str(target_file))
            print(f"✓ {md_file.name} → {city} {coords}")
        else:
            print(f"⚠ {md_file.name}: 無法判斷城市")

    if not any(thailand_poi.glob('*.md')):
        thailand_poi.rmdir()
        print(f"✓ 刪除空的 泰國/POI 目錄")
else:
    print("✓ 泰國/POI 不存在")

# 4. 美國中文名 → 英文
print("\n[4] 美國中文資料夾 → 英文:")
print("-" * 80)

US_RENAME = {
    '洛杉磯': 'Los Angeles',
    '舊金山': 'San Francisco',
}

usa_path = wiki_path / '美國'
for chinese, english in US_RENAME.items():
    src = usa_path / chinese
    dst = usa_path / english

    if src.exists():
        if dst.exists():
            # 合併
            for md_file in src.glob('*.md'):
                target_file = dst / md_file.name
                if not target_file.exists():
                    shutil.move(str(md_file), str(target_file))
                else:
                    print(f"⚠ 重複: {english}/{md_file.name}")
            src.rmdir()
        else:
            # 重命名
            shutil.move(str(src), str(dst))

        count = len(list(dst.glob('*.md')))
        print(f"✓ {chinese} → {english} ({count} 個檔案)")
    else:
        print(f"⚠ {chinese} 不存在")

# 5. 加拿大/舊金山 → 美國/Alaska
print("\n[5] 加拿大/舊金山 → 美國/Alaska:")
print("-" * 80)

canada_sf = wiki_path / '加拿大' / '舊金山'
usa_alaska = wiki_path / '美國' / 'Alaska'

if canada_sf.exists():
    usa_alaska.mkdir(parents=True, exist_ok=True)

    count = 0
    for md_file in canada_sf.glob('*.md'):
        target_file = usa_alaska / md_file.name
        if not target_file.exists():
            shutil.move(str(md_file), str(target_file))
            count += 1
        else:
            print(f"⚠ 重複: Alaska/{md_file.name}")

    if not any(canada_sf.glob('*.md')):
        canada_sf.rmdir()

    print(f"✓ 移動 {count} 個檔案到 美國/Alaska")
    print(f"✓ 刪除空的 加拿大/舊金山 目錄")
else:
    print("✓ 加拿大/舊金山 不存在")

# 6. 台灣建立澎湖縣
print("\n[6] 台灣 - 建立澎湖縣:")
print("-" * 80)
penghu_county = wiki_path / '台灣' / '澎湖縣'

if penghu_county.exists():
    print("✓ 澎湖縣已存在")
else:
    penghu_county.mkdir(parents=True, exist_ok=True)
    print("✓ 建立 澎湖縣 目錄")

# 7. 日本建立群馬県
print("\n[7] 日本 - 建立群馬県:")
print("-" * 80)
gunma_prefecture = wiki_path / '日本' / '群馬県'

if gunma_prefecture.exists():
    print("✓ 群馬県已存在")
else:
    gunma_prefecture.mkdir(parents=True, exist_ok=True)
    print("✓ 建立 群馬県 目錄")

# 8. 日本石垣市 → 沖縄県
print("\n[8] 日本石垣市 → 沖縄県:")
print("-" * 80)
ishigaki_toplevel = wiki_path / '日本' / '石垣市'
ishigaki_city = wiki_path / '日本' / '沖縄県' / '石垣市'

if ishigaki_toplevel.exists():
    (wiki_path / '日本' / '沖縄県').mkdir(parents=True, exist_ok=True)
    ishigaki_city.mkdir(parents=True, exist_ok=True)

    count = 0
    for md_file in ishigaki_toplevel.glob('*.md'):
        target_file = ishigaki_city / md_file.name
        if not target_file.exists():
            shutil.move(str(md_file), str(target_file))
            count += 1
        else:
            print(f"⚠ 重複: 沖縄県/石垣市/{md_file.name}")

    if not any(ishigaki_toplevel.glob('*.md')):
        ishigaki_toplevel.rmdir()

    print(f"✓ 移動 {count} 個檔案到 沖縄県/石垣市")
    print(f"✓ 刪除空的 日本/石垣市 目錄")
else:
    print("✓ 日本/石垣市 不存在")

print("\n" + "=" * 80)
print("修正完成")
print("=" * 80)
