#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取美國景點
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

sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from china_cities_coords import get_nearest_province, get_nearest_city

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def extract_kml_usa_pois():
    """從 KML 提取美國範圍內的所有 POI"""
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

                        # 檢查是否在美國範圍內
                        if -180 <= lng <= -50 and 20 <= lat <= 50:
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
country: 美國
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

**位置：** {city_name}, {state_name}
**國家：** 美國
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

# 美國州名對應的主要城市中心座標
USA_STATES = {
    'Alabama': {'center': (-86.9023, 32.8067), 'cities': {}},
    'Alaska': {'center': (-152.4044, 64.2008), 'cities': {}},
    'Arizona': {'center': (-111.4312, 33.7298), 'cities': {}},
    'Arkansas': {'center': (-92.3731, 34.9697), 'cities': {}},
    'California': {'center': (-119.4179, 36.1162), 'cities': {}},
    'Colorado': {'center': (-105.3111, 39.0598), 'cities': {}},
    'Connecticut': {'center': (-72.7554, 41.5978), 'cities': {}},
    'Delaware': {'center': (-75.5277, 39.3185), 'cities': {}},
    'Florida': {'center': (-81.5158, 27.9947), 'cities': {}},
    'Georgia': {'center': (-83.6431, 33.0406), 'cities': {}},
    'Hawaii': {'center': (-157.5, 20.7), 'cities': {}},
    'Idaho': {'center': (-114.7420, 44.2405), 'cities': {}},
    'Illinois': {'center': (-89.0022, 40.3495), 'cities': {}},
    'Indiana': {'center': (-86.2604, 39.8494), 'cities': {}},
    'Iowa': {'center': (-93.6196, 42.0115), 'cities': {}},
    'Kansas': {'center': (-96.7265, 38.5266), 'cities': {}},
    'Kentucky': {'center': (-84.6701, 37.6681), 'cities': {}},
    'Louisiana': {'center': (-92.2896, 31.1695), 'cities': {}},
    'Maine': {'center': (-69.3819, 45.2538), 'cities': {}},
    'Maryland': {'center': (-76.8023, 39.0639), 'cities': {}},
    'Massachusetts': {'center': (-71.5301, 42.2302), 'cities': {}},
    'Michigan': {'center': (-84.5361, 43.3266), 'cities': {}},
    'Minnesota': {'center': (-94.6859, 45.6945), 'cities': {}},
    'Mississippi': {'center': (-89.6787, 32.7416), 'cities': {}},
    'Missouri': {'center': (-92.2896, 38.4561), 'cities': {}},
    'Montana': {'center': (-110.3626, 47.0527), 'cities': {}},
    'Nebraska': {'center': (-100.4659, 41.4925), 'cities': {}},
    'Nevada': {'center': (-117.0554, 38.8026), 'cities': {}},
    'New Hampshire': {'center': (-71.5653, 43.4525), 'cities': {}},
    'New Jersey': {'center': (-74.5210, 40.2989), 'cities': {}},
    'New Mexico': {'center': (-106.6504, 34.5199), 'cities': {}},
    'New York': {'center': (-75.7597, 42.1657), 'cities': {}},
    'North Carolina': {'center': (-79.8064, 35.6301), 'cities': {}},
    'North Dakota': {'center': (-101.4036, 47.5289), 'cities': {}},
    'Ohio': {'center': (-82.9071, 40.3888), 'cities': {}},
    'Oklahoma': {'center': (-96.9289, 35.5653), 'cities': {}},
    'Oregon': {'center': (-122.0710, 43.8041), 'cities': {}},
    'Pennsylvania': {'center': (-77.2098, 40.5908), 'cities': {}},
    'Rhode Island': {'center': (-71.5117, 41.6809), 'cities': {}},
    'South Carolina': {'center': (-80.9066, 33.8361), 'cities': {}},
    'South Dakota': {'center': (-99.4388, 44.2998), 'cities': {}},
    'Tennessee': {'center': (-86.6923, 35.7478), 'cities': {}},
    'Texas': {'center': (-99.9018, 31.9686), 'cities': {}},
    'Utah': {'center': (-111.8910, 39.3210), 'cities': {}},
    'Vermont': {'center': (-72.5754, 44.0459), 'cities': {}},
    'Virginia': {'center': (-78.1694, 37.7693), 'cities': {}},
    'Washington': {'center': (-121.4905, 47.7511), 'cities': {}},
    'West Virginia': {'center': (-81.6326, 38.4912), 'cities': {}},
    'Wisconsin': {'center': (-89.6165, 44.2685), 'cities': {}},
    'Wyoming': {'center': (-107.5512, 42.7559), 'cities': {}},
}

def get_nearest_state(coords):
    """根據座標找到最近的美國州"""
    lng, lat = coords
    min_distance = float('inf')
    best_state = None

    for state_name, state_data in USA_STATES.items():
        center_lng, center_lat = state_data['center']
        distance = ((lng - center_lng) ** 2 + (lat - center_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_state = state_name

    return best_state

print("=" * 80)
print("🌍 美國景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_usa_pois()
print(f"   發現 {len(kml_pois)} 個美國 POI")

# 2. 清空舊的美國 Wiki
print("\n🗑️  清理舊 Wiki 結構...")
usa_path = os.path.join(WIKI_BASE, "美國")
if os.path.isdir(usa_path):
    for state_name in os.listdir(usa_path):
        state_path = os.path.join(usa_path, state_name)
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
        # 簡單地用州名作為城市（可以後續細化）
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

    print(f"[{state_idx:2d}/50+] {state_name}")

    for city_name in sorted(cities.keys()):
        pois = cities[city_name]

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "美國", state_name, city_name)
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
    if errors_list:
        print(f"\n  錯誤列表（前 10 個）:")
        for err in errors_list[:10]:
            print(f"    - {err}")
        if len(errors_list) > 10:
            print(f"    ... 還有 {len(errors_list) - 10} 個錯誤")

print(f"\n✓ KML 景點: {len(kml_pois):5d} 個")
print(f"✓ 州: {len(organized_pois):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")
    for poi in unlocated[:5]:
        print(f"    - {poi['name']} ({poi['lng']}, {poi['lat']})")
    if len(unlocated) > 5:
        print(f"    ... 還有 {len(unlocated) - 5} 個")

print(f"\n{'='*80}")
print(f"✅ 美國景點完整提取完成！")
print(f"{'='*80}")
