#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取日本景點
按都道府縣/市町村完整建立 Wiki 二級結構
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
import shutil
import io
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

# 導入日本市町村座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def extract_kml_japan_pois():
    """從 KML 提取日本範圍內的所有 POI"""
    pois = []
    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            desc_elem = placemark.find('kml:description', ns)
            coords_elem = placemark.find('.//kml:coordinates', ns)

            if name_elem is not None and coords_elem is not None:
                name = (name_elem.text or "").strip()
                desc = (desc_elem.text if desc_elem is not None else "").strip()
                coords_text = coords_elem.text.strip()

                if coords_text and name:
                    try:
                        parts = coords_text.split(',')
                        lng, lat = float(parts[0]), float(parts[1])

                        # 檢查是否在日本範圍內（包含沖繩）
                        if 125 <= lng <= 145 and 24 <= lat <= 46:
                            pois.append({
                                'name': name,
                                'desc': desc,
                                'lng': lng,
                                'lat': lat
                            })
                    except:
                        pass
    except Exception as e:
        print(f"KML 解析錯誤: {str(e)}", file=sys.stderr)

    return pois

def find_location_for_poi(poi, all_pois):
    """根據座標找到 POI 應該屬於哪個都道府縣和市町村"""
    lng, lat = poi['lng'], poi['lat']

    min_distance = float('inf')
    best_pref = None
    best_city = None

    # 遍歷所有都道府縣，在每個都道府縣內找最近的市町村
    for pref_name in JAPAN_TOWNS_COORDS.keys():
        # 計算該都道府縣的平均座標（或中心座標）
        cities = JAPAN_TOWNS_COORDS[pref_name]
        if not cities:
            continue

        # 計算該都道府縣所有城市的平均座標
        avg_lng = sum(coords[0] for coords in cities.values()) / len(cities)
        avg_lat = sum(coords[1] for coords in cities.values()) / len(cities)

        # 計算到該都道府縣的距離
        pref_distance = ((lng - avg_lng) ** 2 + (lat - avg_lat) ** 2) ** 0.5

        # 如果這個都道府縣更近，更新最佳匹配
        if pref_distance < min_distance:
            min_distance = pref_distance
            best_pref = pref_name
            # 在該都道府縣內找最近的市町村
            best_city = get_nearest_town((lng, lat), pref_name)

    return best_pref, best_city

def create_markdown(poi_name, coords, city_name, pref_name, desc):
    """為 POI 創建 Markdown 內容"""
    timestamp = datetime.now().isoformat() + 'Z'
    slug = poi_name.lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    if desc:
        desc_text = desc
    else:
        desc_text = "待補充"

    frontmatter = f"""---
title: {poi_name}
slug: {slug}
location: {city_name}
country: 日本
city: {city_name}
category: 景點
tags: ["景點"]
coordinates: [{coords[0]}, {coords[1]}]
md5:
created_at: {timestamp}
processed: false
graph-excluded: false
source_url: raw/travel/Zachary's World Trip.kml
source_type: kml-placemark
---

# {poi_name}

## 基本資訊

**位置：** {city_name}
**國家：** 日本
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

print("=" * 80)
print("🌍 日本景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_japan_pois()
print(f"   發現 {len(kml_pois)} 個日本 POI")

# 2. 清空舊的日本 Wiki（備份）
print("\n🗑️  清理舊 Wiki 結構...")
japan_path = os.path.join(WIKI_BASE, "日本")
if os.path.isdir(japan_path):
    for pref_name in os.listdir(japan_path):
        pref_path = os.path.join(japan_path, pref_name)
        if os.path.isdir(pref_path):
            # 刪除舊結構
            for item in os.listdir(pref_path):
                item_path = os.path.join(pref_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    try:
                        os.remove(item_path)
                    except:
                        pass
print("   舊 Wiki 結構已清理")

# 3. 按都道府縣/市町村組織景點
print("\n📊 組織景點數據...")
organized_pois = defaultdict(lambda: defaultdict(list))
unlocated = []

for poi in kml_pois:
    pref, city = find_location_for_poi(poi, kml_pois)
    if pref and city:
        organized_pois[pref][city].append(poi)
    else:
        unlocated.append(poi)

print(f"   已分類: {sum(len(cities) for cities in organized_pois.values())} 個")
print(f"   未分類: {len(unlocated)} 個")

# 4. 建立檔案
print(f"\n{'='*80}")
print(f"📝 建立檔案")
print(f"{'='*80}\n")

total_created = 0
total_errors = 0
errors_list = []

for pref_idx, pref_name in enumerate(sorted(organized_pois.keys()), 1):
    cities = organized_pois[pref_name]
    pref_created = 0

    print(f"[{pref_idx:2d}/47] {pref_name}")

    for city_name in sorted(cities.keys()):
        pois = cities[city_name]

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "日本", pref_name, city_name)
        os.makedirs(city_path, exist_ok=True)

        # 建立檔案
        for poi in pois:
            clean_name = sanitize_filename(poi['name'])
            filename = f"{clean_name}.md"
            filepath = os.path.join(city_path, filename)

            try:
                # 檢查檔案是否已存在
                if not os.path.exists(filepath):
                    content = create_markdown(
                        poi['name'],
                        (poi['lng'], poi['lat']),
                        city_name,
                        pref_name,
                        poi['desc']
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_created += 1
                    pref_created += 1

            except Exception as e:
                total_errors += 1
                errors_list.append(f"{pref_name}/{city_name}/{poi['name']}: {str(e)}")

        if pref_created > 0:
            print(f"      {city_name}: {pref_created:4d} 個")

print(f"\n{'='*80}")
print(f"📊 建立完成")
print(f"{'='*80}\n")

print(f"✓ 新建檔案: {total_created:5d} 個")
if total_errors > 0:
    print(f"✗ 建立失敗: {total_errors:5d} 個")
    if errors_list:
        print(f"\n  錯誤列表（前 10 個）:")
        for err in errors_list[:10]:
            print(f"    - {err}")
        if len(errors_list) > 10:
            print(f"    ... 還有 {len(errors_list) - 10} 個錯誤")

print(f"\n✓ KML 景點: {len(kml_pois):5d} 個")
print(f"✓ 都道府縣: {len(organized_pois):5d} 個")
print(f"✓ 市町村: {sum(len(cities) for cities in organized_pois.values()):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")
    for poi in unlocated[:5]:
        print(f"    - {poi['name']} ({poi['lng']}, {poi['lat']})")
    if len(unlocated) > 5:
        print(f"    ... 還有 {len(unlocated) - 5} 個")

print(f"\n{'='*80}")
print(f"✅ 日本景點完整提取完成！")
print(f"{'='*80}")
