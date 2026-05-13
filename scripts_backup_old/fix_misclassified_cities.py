#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import json
import sys
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 城市座標對應表（用來判斷正確位置）
CITY_COORDS = {
    '西班牙': {
        '馬德里': (-3.7038, 40.4168),
        '巴塞隆納': (2.1734, 41.3851),
        '塞維亞': (-5.9844, 37.3891),
        '馬拉加': (-3.7596, 36.7213),
    },
    '荷蘭': {
        '阿姆斯特丹': (4.8952, 52.3676),
        '鹿特丹': (4.4699, 51.9225),
        '海牙': (4.3007, 52.0705),
    },
    '美國': {
        '紐約': (-74.0060, 40.7128),
        '洛杉磯': (-118.2437, 34.0522),
        '芝加哥': (-87.6298, 41.8781),
        '舊金山': (-122.4194, 37.7749),
    },
    '紐西蘭': {
        '奧克蘭': (174.8860, -37.0082),
        '威靈頓': (174.7762, -41.2865),
    },
    '祕魯': {
        '利馬': (-77.0369, -12.0464),
        '庫斯科': (-71.9789, -13.5319),
    },
    '盧森堡': {
        '盧森堡市': (6.1296, 49.6116),
    },
    '澳洲': {
        '雪梨': (151.2093, -33.8688),
        '墨爾本': (144.9631, -37.8136),
        '布里斯本': (153.0251, -27.4698),
    },
    '泰國': {
        '曼谷': (100.5018, 13.7563),
        '清邁': (98.9853, 18.7883),
        '普吉島': (98.3298, 7.8804),
    }
}

# 誤分類的資料夾清單（要檢查和修正的）
MISCLASSIFIED = {
    '西班牙': ['紐約'],
    '荷蘭': ['紐約'],
    '美國': [],  # 檢查所有 Chinese 資料夾
    '紐西蘭': ['台南市'],
    '祕魯': ['洛杉磯', '紐約'],
    '盧森堡': ['紐約'],
    '澳洲': ['台南市'],
    '泰國': ['澳門'],
    '比利時': ['紐約'],
}

def extract_coordinates(md_content):
    """從 markdown 檔案提取座標"""
    match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', md_content)
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except:
            return None
    return None

def find_nearest_city(coords, country):
    """找到最近的城市"""
    if country not in CITY_COORDS:
        return None

    lng, lat = coords
    cities = CITY_COORDS[country]

    min_dist = float('inf')
    nearest = None

    for city, (city_lng, city_lat) in cities.items():
        dist = ((lng - city_lng)**2 + (lat - city_lat)**2)**0.5
        if dist < min_dist:
            min_dist = dist
            nearest = city

    return nearest

def scan_country(country, misclassified_folders):
    """掃描國家並修正誤分類"""
    wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
    country_path = wiki_path / country

    if not country_path.exists():
        return []

    results = []

    # 檢查指定的誤分類資料夾
    for folder in misclassified_folders:
        folder_path = country_path / folder
        if not folder_path.exists():
            continue

        print(f"\n檢查 {country}/{folder}")

        for md_file in folder_path.glob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                coords = extract_coordinates(content)

                if coords:
                    nearest_city = find_nearest_city(coords, country)

                    if nearest_city and nearest_city != folder:
                        print(f"  ❌ {md_file.name}: 座標 {coords} → 應該在 {nearest_city}")

                        # 建立目標資料夾
                        target_folder = country_path / nearest_city
                        target_folder.mkdir(parents=True, exist_ok=True)

                        # 移動檔案
                        target_file = target_folder / md_file.name
                        shutil.move(str(md_file), str(target_file))

                        results.append({
                            'file': md_file.name,
                            'from': folder,
                            'to': nearest_city,
                            'coords': coords,
                            'country': country,
                            'status': 'moved'
                        })
                    else:
                        print(f"  ✓ {md_file.name}: 座標 {coords} 正確在 {folder}")
            except Exception as e:
                print(f"  ⚠️ {md_file.name}: 錯誤 {e}")

    return results

def check_chinese_cities(country):
    """檢查國家中所有中文城市資料夾"""
    wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
    country_path = wiki_path / country

    if not country_path.exists():
        return []

    results = []
    chinese_folders = []

    # 找所有中文名資料夾
    for folder in country_path.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            # 簡單判斷：如果資料夾名是中文字
            if any('一' <= c <= '鿿' for c in folder.name):
                chinese_folders.append(folder.name)

    if chinese_folders:
        print(f"\n{country} 中文資料夾: {chinese_folders}")

        for folder in chinese_folders:
            folder_path = country_path / folder
            for md_file in folder_path.glob('*.md'):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    coords = extract_coordinates(content)

                    if coords:
                        nearest_city = find_nearest_city(coords, country)
                        if nearest_city and nearest_city != folder:
                            print(f"  {md_file.name}: {coords} → {nearest_city}")
                            results.append({
                                'file': md_file.name,
                                'from': folder,
                                'to': nearest_city,
                                'coords': coords,
                                'country': country
                            })
                except:
                    pass

    return results

def main():
    print("=" * 60)
    print("開始修正誤分類的城市資料夾")
    print("=" * 60)

    all_results = []

    # 修正指定的誤分類
    for country, folders in MISCLASSIFIED.items():
        results = scan_country(country, folders)
        all_results.extend(results)

    # 檢查美國的中文資料夾
    print("\n檢查美國的中文資料夾...")
    us_chinese = check_chinese_cities('美國')
    all_results.extend(us_chinese)

    print("\n" + "=" * 60)
    print(f"總計：{len(all_results)} 個檔案需要移動")
    print("=" * 60)

    if all_results:
        print("\n移動摘要:")
        by_country = defaultdict(list)
        for r in all_results:
            by_country[r['country']].append(r)

        for country in sorted(by_country.keys()):
            items = by_country[country]
            print(f"\n{country}:")
            for item in items:
                if item.get('status') == 'moved':
                    print(f"  ✓ {item['file']}: {item['from']} → {item['to']}")

if __name__ == '__main__':
    main()
