#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取韓國景點
建立 Wiki 二級結構：道 + 城市
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

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def extract_kml_korea_pois():
    """從 KML 提取韓國範圍內的所有 POI"""
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

                        # 檢查是否在韓國範圍內
                        if 125 <= lng <= 130 and 33 <= lat <= 44:
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

def create_markdown(poi_name, coords, city_name, province_name, desc):
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
country: 韓國
province: {province_name}
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
**道：** {province_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

# 韓國主要道名
KOREA_PROVINCES = {
    'Seoul': (126.9784, 37.5665),
    'Busan': (129.0756, 35.1796),
    'Incheon': (126.7052, 37.4563),
    'Daegu': (128.5916, 35.8748),
    'Daejeon': (127.3845, 36.3504),
    'Gwangju': (126.8854, 35.1595),
    'Ulsan': (129.3159, 35.5384),
    'Gyeonggi': (127.0822, 37.2756),
    'Gangwon': (127.7455, 37.5500),
    'North Chungcheong': (127.2886, 36.8000),
    'South Chungcheong': (127.1086, 36.3000),
    'North Jeolla': (126.5349, 35.8242),
    'South Jeolla': (126.8000, 34.8000),
    'North Gyeongsang': (128.8054, 36.5723),
    'South Gyeongsang': (128.6900, 35.2271),
    'Jeju': (126.5233, 33.5186),
}

def get_nearest_province(coords):
    """根據座標找到最近的韓國道"""
    lng, lat = coords
    min_distance = float('inf')
    best_province = None

    for province_name, (prov_lng, prov_lat) in KOREA_PROVINCES.items():
        distance = ((lng - prov_lng) ** 2 + (lat - prov_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_province = province_name

    return best_province

print("=" * 80)
print("🌍 韓國景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_korea_pois()
print(f"   發現 {len(kml_pois)} 個韓國 POI")

# 2. 清空舊的韓國 Wiki
print("\n🗑️  清理舊 Wiki 結構...")
korea_path = os.path.join(WIKI_BASE, "韓國")
if os.path.isdir(korea_path):
    for province_name in os.listdir(korea_path):
        province_path = os.path.join(korea_path, province_name)
        if os.path.isdir(province_path):
            for item in os.listdir(province_path):
                item_path = os.path.join(province_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    try:
                        os.remove(item_path)
                    except:
                        pass
print("   舊 Wiki 結構已清理")

# 3. 按道/城市組織景點
print("\n📊 組織景點數據...")
organized_pois = defaultdict(lambda: defaultdict(list))
unlocated = []

for poi in kml_pois:
    province = get_nearest_province((poi['lng'], poi['lat']))
    if province:
        organized_pois[province]['POI'].append(poi)
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

for prov_idx, province_name in enumerate(sorted(organized_pois.keys()), 1):
    cities = organized_pois[province_name]
    prov_created = 0

    print(f"[{prov_idx:2d}/{len(organized_pois)}] {province_name}")

    for city_name in sorted(cities.keys()):
        pois = cities[city_name]

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "韓國", province_name, city_name)
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
                        province_name,
                        poi['desc']
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_created += 1
                    prov_created += 1

            except Exception as e:
                total_errors += 1
                errors_list.append(f"{province_name}/{city_name}/{poi['name']}: {str(e)}")

        if prov_created > 0:
            print(f"      {city_name}: {prov_created:4d} 個")

print(f"\n{'='*80}")
print(f"📊 建立完成")
print(f"{'='*80}\n")

print(f"✓ 新建檔案: {total_created:5d} 個")
if total_errors > 0:
    print(f"✗ 建立失敗: {total_errors:5d} 個")

print(f"\n✓ KML 景點: {len(kml_pois):5d} 個")
print(f"✓ 道: {len(organized_pois):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")

print(f"\n{'='*80}")
print(f"✅ 韓國景點完整提取完成！")
print(f"{'='*80}")
