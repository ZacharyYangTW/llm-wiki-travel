#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取馬來西亞景點
建立 Wiki 二級結構：州 + 城市
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

# 馬來西亞主要州名及座標
MALAYSIA_STATES = {
    'Johor': (103.7618, 1.4854),
    'Kedah': (100.3688, 6.1184),
    'Kelantan': (102.2381, 6.1256),
    'Kuala Lumpur': (101.6869, 3.1390),
    'Labuan': (115.2309, 5.2831),
    'Malacca': (102.2381, 2.1896),
    'Negeri Sembilan': (101.9424, 2.7258),
    'Pahang': (103.3256, 3.8126),
    'Penang': (100.3288, 5.3521),
    'Perak': (101.5740, 4.5921),
    'Perlis': (100.2048, 6.4449),
    'Sabah': (117.5578, 5.0000),
    'Sarawak': (113.0000, 1.5533),
    'Selangor': (101.5229, 3.0738),
    'Terengganu': (102.6528, 5.3117),
    'Putrajaya': (101.6964, 2.9264),
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

def extract_kml_malaysia_pois():
    """從 KML 提取馬來西亞範圍內的所有 POI"""
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

                        if 99 <= lng <= 120 and 1 <= lat <= 7:
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

def create_markdown(poi_name, coords, city_name, state_name, desc):
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
country: 馬來西亞
state: {state_name}
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
**州：** {state_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

def get_nearest_state(coords):
    """根據座標找到最近的馬來西亞州"""
    lng, lat = coords
    min_distance = float('inf')
    best_state = None

    for state_name, (state_lng, state_lat) in MALAYSIA_STATES.items():
        distance = ((lng - state_lng) ** 2 + (lat - state_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_state = state_name

    return best_state

print("=" * 80)
print("🌍 馬來西亞景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_malaysia_pois()
print(f"   發現 {len(kml_pois)} 個馬來西亞 POI")

# 2. 清空舊的馬來西亞 Wiki
print("\n🗑️  清理舊 Wiki 結構...")
malaysia_path = os.path.join(WIKI_BASE, "馬來西亞")
if os.path.isdir(malaysia_path):
    for state_name in os.listdir(malaysia_path):
        state_path = os.path.join(malaysia_path, state_name)
        if os.path.isdir(state_path):
            for item in os.listdir(state_path):
                item_path = os.path.join(state_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    try:
                        os.remove(item_path)
                    except:
                        pass
print("   舊 Wiki 結構已清理")

# 3. 按州/城市組織景點
print("\n📊 組織景點數據...")
organized_pois = defaultdict(lambda: defaultdict(list))
unlocated = []

for poi in kml_pois:
    state = get_nearest_state((poi['lng'], poi['lat']))
    if state:
        organized_pois[state]['POI'].append(poi)
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

for state_idx, state_name in enumerate(sorted(organized_pois.keys()), 1):
    cities = organized_pois[state_name]
    state_created = 0

    print(f"[{state_idx:2d}/{len(organized_pois)}] {state_name}")

    for city_name in sorted(cities.keys()):
        pois = cities[city_name]

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "馬來西亞", state_name, city_name)
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
                        state_name,
                        poi['desc']
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_created += 1
                    state_created += 1

            except Exception as e:
                total_errors += 1
                errors_list.append(f"{state_name}/{city_name}/{poi['name']}: {str(e)}")

        if state_created > 0:
            print(f"      {city_name}: {state_created:4d} 個")

print(f"\n{'='*80}")
print(f"📊 建立完成")
print(f"{'='*80}\n")

print(f"✓ 新建檔案: {total_created:5d} 個")
if total_errors > 0:
    print(f"✗ 建立失敗: {total_errors:5d} 個")

print(f"\n✓ KML 景點: {len(kml_pois):5d} 個")
print(f"✓ 州: {len(organized_pois):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")
    for poi in unlocated[:5]:
        print(f"    - {poi['name']} ({poi['lng']}, {poi['lat']})")
    if len(unlocated) > 5:
        print(f"    ... 還有 {len(unlocated) - 5} 個")

print(f"\n{'='*80}")
print(f"✅ 馬來西亞景點完整提取完成！")
print(f"{'='*80}")
