#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取法國景點
建立 Wiki 二級結構：地區 + 城市
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

# 法國主要地區及座標
FRANCE_REGIONS = {
    'Paris': (-2.3522, 48.8566),
    'Auvergne-Rhône-Alpes': (4.8357, 45.7640),
    'Bourgogne-Franche-Comté': (4.3691, 47.2808),
    'Brittany': (-3.3625, 48.1173),
    'Centre-Val de Loire': (1.9369, 47.5922),
    'Corsica': (8.7686, 42.0696),
    'Grand Est': (5.0455, 48.6291),
    'Hauts-de-France': (2.8773, 50.4501),
    'Île-de-France': (2.2139, 48.8626),
    'Normandy': (0.3674, 49.2628),
    'Nouvelle-Aquitaine': (-0.2272, 45.5017),
    'Occitania': (2.1686, 43.6047),
    'Pays de la Loire': (-0.5596, 47.4667),
    'Provence-Alpes-Côte d\'Azur': (5.3698, 43.9159),
}

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def extract_kml_france_pois():
    """從 KML 提取法國範圍內的所有 POI"""
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

                        if -5 <= lng <= 8 and 42 <= lat <= 51:
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

def create_markdown(poi_name, coords, city_name, region_name, desc):
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
country: 法國
region: {region_name}
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
**地區：** {region_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

def get_nearest_region(coords):
    """根據座標找到最近的法國地區"""
    lng, lat = coords
    min_distance = float('inf')
    best_region = None

    for region_name, (region_lng, region_lat) in FRANCE_REGIONS.items():
        distance = ((lng - region_lng) ** 2 + (lat - region_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_region = region_name

    return best_region

print("=" * 80)
print("🌍 法國景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_france_pois()
print(f"   發現 {len(kml_pois)} 個法國 POI")

# 2. 清空舊的法國 Wiki
print("\n🗑️  清理舊 Wiki 結構...")
france_path = os.path.join(WIKI_BASE, "法國")
if os.path.isdir(france_path):
    for region_name in os.listdir(france_path):
        region_path = os.path.join(france_path, region_name)
        if os.path.isdir(region_path):
            for item in os.listdir(region_path):
                item_path = os.path.join(region_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    try:
                        os.remove(item_path)
                    except:
                        pass
print("   舊 Wiki 結構已清理")

# 3. 按地區/城市組織景點
print("\n📊 組織景點數據...")
organized_pois = defaultdict(lambda: defaultdict(list))
unlocated = []

for poi in kml_pois:
    region = get_nearest_region((poi['lng'], poi['lat']))
    if region:
        organized_pois[region]['POI'].append(poi)
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

for region_idx, region_name in enumerate(sorted(organized_pois.keys()), 1):
    cities = organized_pois[region_name]
    region_created = 0

    print(f"[{region_idx:2d}/{len(organized_pois)}] {region_name}")

    for city_name in sorted(cities.keys()):
        pois = cities[city_name]

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "法國", region_name, city_name)
        os.makedirs(city_path, exist_ok=True)

        # 建立檔案
        for poi in pois:
            clean_name = sanitize_filename(poi['name'])
            filename = f"{clean_name}.md"
            filepath = os.path.join(city_path, filename)

            try:
                if not os.path.exists(filepath):
                    content = create_markdown(
                        poi['name'],
                        (poi['lng'], poi['lat']),
                        city_name,
                        region_name,
                        poi['desc']
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_created += 1
                    region_created += 1

            except Exception as e:
                total_errors += 1
                errors_list.append(f"{region_name}/{city_name}/{poi['name']}: {str(e)}")

        if region_created > 0:
            print(f"      {city_name}: {region_created:4d} 個")

print(f"\n{'='*80}")
print(f"📊 建立完成")
print(f"{'='*80}\n")

print(f"✓ 新建檔案: {total_created:5d} 個")
if total_errors > 0:
    print(f"✗ 建立失敗: {total_errors:5d} 個")

print(f"\n✓ KML 景點: {len(kml_pois):5d} 個")
print(f"✓ 地區: {len(organized_pois):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")
    for poi in unlocated[:5]:
        print(f"    - {poi['name']} ({poi['lng']}, {poi['lat']})")
    if len(unlocated) > 5:
        print(f"    ... 還有 {len(unlocated) - 5} 個")

print(f"\n{'='*80}")
print(f"✅ 法國景點完整提取完成！")
print(f"{'='*80}")
