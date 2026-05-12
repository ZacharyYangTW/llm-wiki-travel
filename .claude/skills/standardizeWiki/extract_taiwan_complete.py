#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取台灣景點
按縣市/鄉鎮市區完整建立 Wiki 二級結構
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

# 導入台灣縣市座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from taiwan_cities_coords import TAIWAN_COUNTIES_COORDS, TAIWAN_DISTRICTS_COORDS, get_nearest_county, get_nearest_district

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def extract_kml_taiwan_pois():
    """從 KML 提取台灣範圍內的所有 POI"""
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

                        # 檢查是否在台灣範圍內
                        if 120 <= lng <= 122 and 21.8 <= lat <= 25.2:
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

def find_location_for_poi(poi):
    """根據座標找到 POI 應該屬於哪個縣市和鄉鎮市區"""
    lng, lat = poi['lng'], poi['lat']

    min_distance = float('inf')
    best_county = None
    best_district = None

    # 遍歷所有縣市，在每個縣市內找最近的鄉鎮市區
    for county_name in TAIWAN_COUNTIES_COORDS.keys():
        # 計算該縣市的平均座標
        districts = TAIWAN_DISTRICTS_COORDS.get(county_name, {})
        if not districts:
            continue

        # 計算該縣市所有區的平均座標
        avg_lng = sum(coords[0] for coords in districts.values()) / len(districts)
        avg_lat = sum(coords[1] for coords in districts.values()) / len(districts)

        # 計算到該縣市的距離
        county_distance = ((lng - avg_lng) ** 2 + (lat - avg_lat) ** 2) ** 0.5

        # 如果這個縣市更近，更新最佳匹配
        if county_distance < min_distance:
            min_distance = county_distance
            best_county = county_name
            # 在該縣市內找最近的鄉鎮市區
            best_district = get_nearest_district((lng, lat), county_name)

    return best_county, best_district

def create_markdown(poi_name, coords, district_name, county_name, desc):
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
location: {district_name}
country: 台灣
city: {county_name}
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

**位置：** {district_name}
**縣市：** {county_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

print("=" * 80)
print("🌍 台灣景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_taiwan_pois()
print(f"   發現 {len(kml_pois)} 個台灣 POI")

# 2. 清空舊的台灣 Wiki
print("\n🗑️  清理舊 Wiki 結構...")
taiwan_path = os.path.join(WIKI_BASE, "台灣")
if os.path.isdir(taiwan_path):
    for county_name in os.listdir(taiwan_path):
        county_path = os.path.join(taiwan_path, county_name)
        if os.path.isdir(county_path):
            # 刪除舊結構
            for item in os.listdir(county_path):
                item_path = os.path.join(county_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    try:
                        os.remove(item_path)
                    except:
                        pass
print("   舊 Wiki 結構已清理")

# 3. 按縣市/鄉鎮市區組織景點
print("\n📊 組織景點數據...")
organized_pois = defaultdict(lambda: defaultdict(list))
unlocated = []

for poi in kml_pois:
    county, district = find_location_for_poi(poi)
    if county and district:
        organized_pois[county][district].append(poi)
    else:
        unlocated.append(poi)

print(f"   已分類: {sum(len(districts) for districts in organized_pois.values())} 個縣市")
print(f"   未分類: {len(unlocated)} 個")

# 4. 建立檔案
print(f"\n{'='*80}")
print(f"📝 建立檔案")
print(f"{'='*80}\n")

total_created = 0
total_errors = 0
errors_list = []

for county_idx, county_name in enumerate(sorted(organized_pois.keys()), 1):
    districts = organized_pois[county_name]
    county_created = 0

    print(f"[{county_idx:2d}/22] {county_name}")

    for district_name in sorted(districts.keys()):
        pois = districts[district_name]

        # 建立目錄
        district_path = os.path.join(WIKI_BASE, "台灣", county_name, district_name)
        os.makedirs(district_path, exist_ok=True)

        # 建立檔案
        for poi in pois:
            clean_name = sanitize_filename(poi['name'])
            filename = f"{clean_name}.md"
            filepath = os.path.join(district_path, filename)

            try:
                # 檢查檔案是否已存在
                if not os.path.exists(filepath):
                    content = create_markdown(
                        poi['name'],
                        (poi['lng'], poi['lat']),
                        district_name,
                        county_name,
                        poi['desc']
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_created += 1
                    county_created += 1

            except Exception as e:
                total_errors += 1
                errors_list.append(f"{county_name}/{district_name}/{poi['name']}: {str(e)}")

        if county_created > 0:
            print(f"      {district_name}: {county_created:4d} 個")

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
print(f"✓ 縣市: {len(organized_pois):5d} 個")
print(f"✓ 鄉鎮市區: {sum(len(districts) for districts in organized_pois.values()):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")
    for poi in unlocated[:5]:
        print(f"    - {poi['name']} ({poi['lng']}, {poi['lat']})")
    if len(unlocated) > 5:
        print(f"    ... 還有 {len(unlocated) - 5} 個")

print(f"\n{'='*80}")
print(f"✅ 台灣景點完整提取完成！")
print(f"{'='*80}")
