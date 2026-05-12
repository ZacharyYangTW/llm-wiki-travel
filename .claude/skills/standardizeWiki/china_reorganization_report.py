#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中國目錄整理最終報告
"""

import os
import sys
import re
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\中國"

def extract_coordinates(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                return (float(match.group(1)), float(match.group(2)))
    except:
        pass
    return None

print("=" * 80)
print("📊 中國目錄整理最終報告")
print("=" * 80)

stats = {}
all_files = 0

for prov_name in sorted(os.listdir(WIKI_BASE)):
    prov_path = os.path.join(WIKI_BASE, prov_name)
    if not os.path.isdir(prov_path):
        continue

    prov_files = 0
    cities = {}

    for item_name in os.listdir(prov_path):
        item_path = os.path.join(prov_path, item_name)

        if item_name.endswith('.md'):
            prov_files += 1
            all_files += 1
        elif os.path.isdir(item_path):
            city_files = [f for f in os.listdir(item_path) if f.endswith('.md')]
            if city_files:
                cities[item_name] = len(city_files)
                prov_files += len(city_files)
                all_files += len(city_files)

    stats[prov_name] = {'files': prov_files, 'cities': len(cities)}

print(f"\n📍 目錄結構分佈（按檔案數量排序）：\n")
print(f"{'省份/地區':<25} {'檔案數':<8} {'城市數':<8}")
print("-" * 50)

sorted_stats = sorted(stats.items(), key=lambda x: x[1]['files'], reverse=True)
for prov, info in sorted_stats:
    print(f"{prov:<25} {info['files']:<8} {info['cities']:<8}")

print("-" * 50)
print(f"{'合計':<25} {all_files:<8} 個")

# 統計各大城市的檔案分佈
print(f"\n📌 主要城市檔案分佈（各省前3大）：\n")

for prov_name in sorted(stats.keys()):
    prov_path = os.path.join(WIKI_BASE, prov_name)
    cities_with_files = {}

    for item_name in os.listdir(prov_path):
        item_path = os.path.join(prov_path, item_name)
        if os.path.isdir(item_path):
            city_files = [f for f in os.listdir(item_path) if f.endswith('.md')]
            if city_files:
                cities_with_files[item_name] = len(city_files)

    if cities_with_files:
        sorted_cities = sorted(cities_with_files.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"{prov_name}:")
        for city, count in sorted_cities:
            print(f"   - {city}: {count} 個")

# 驗證澳門和香港
print(f"\n🎯 澳門和香港特別分類：\n")
macao_path = os.path.join(WIKI_BASE, "澳門")
hongkong_path = os.path.join(WIKI_BASE, "香港")

macao_count = len([f for f in os.listdir(macao_path) if f.endswith('.md')]) if os.path.exists(macao_path) else 0
hongkong_count = len([f for f in os.listdir(hongkong_path) if f.endswith('.md')]) if os.path.exists(hongkong_path) else 0

print(f"澳門: {macao_count} 個檔案")
print(f"香港: {hongkong_count} 個檔案")

# 驗證座標
print(f"\n✅ 座標驗證：\n")
correct = 0
no_coords = 0

for prov_name in sorted(os.listdir(WIKI_BASE)):
    prov_path = os.path.join(WIKI_BASE, prov_name)
    if not os.path.isdir(prov_path):
        continue

    for item_name in os.listdir(prov_path):
        item_path = os.path.join(prov_path, item_name)

        if item_name.endswith('.md'):
            coords = extract_coordinates(item_path)
            if coords:
                correct += 1
            else:
                no_coords += 1
        elif os.path.isdir(item_path):
            for file_name in os.listdir(item_path):
                if file_name.endswith('.md'):
                    file_path = os.path.join(item_path, file_name)
                    coords = extract_coordinates(file_path)
                    if coords:
                        correct += 1
                    else:
                        no_coords += 1

print(f"有座標: {correct} 個")
print(f"無座標: {no_coords} 個")

print(f"\n{'='*80}")
print(f"✅ 中國目錄整理完成！")
print(f"{'='*80}")
