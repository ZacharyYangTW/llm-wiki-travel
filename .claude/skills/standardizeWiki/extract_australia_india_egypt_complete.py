#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取澳洲、印度、埃及景點
建立 Wiki 二級結構
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

# 三個國家的地區定義
COUNTRIES = {
    '澳洲': {
        'coords': {'lng': (113, 154), 'lat': (-44, -10)},
        'divisions': {
            'New South Wales': (151.2093, -33.8688),
            'Queensland': (145.7781, -23.6978),
            'South Australia': (135.3105, -34.9285),
            'Tasmania': (147.1093, -42.8821),
            'Victoria': (145.1098, -37.8136),
            'Western Australia': (122.3312, -31.9505),
            'Australian Capital Territory': (149.1200, -35.2809),
            'Northern Territory': (133.8807, -12.4638),
        }
    },
    '印度': {
        'coords': {'lng': (68, 97), 'lat': (8, 35)},
        'divisions': {
            'Andaman and Nicobar': (92.7597, 11.7401),
            'Andhra Pradesh': (79.9120, 15.2993),
            'Arunachal Pradesh': (93.6053, 28.2180),
            'Assam': (91.7898, 26.2006),
            'Bihar': (85.5200, 25.0961),
            'Chhattisgarh': (81.8661, 21.2787),
            'Delhi': (77.1025, 28.7041),
            'Goa': (73.8278, 15.3017),
            'Gujarat': (72.6369, 22.2587),
            'Haryana': (77.0266, 29.0588),
            'Himachal Pradesh': (77.1734, 31.7433),
            'Jharkhand': (85.2799, 23.6102),
            'Karnataka': (75.7139, 15.3173),
            'Kerala': (76.2711, 10.8505),
            'Madhya Pradesh': (78.6569, 22.9375),
            'Maharashtra': (75.7139, 19.7515),
            'Manipur': (94.7868, 24.6637),
            'Meghalaya': (91.8960, 25.4670),
            'Mizoram': (93.2197, 23.1815),
            'Nagaland': (94.5614, 26.1584),
            'Odisha': (85.8830, 20.9517),
            'Puducherry': (79.8355, 11.9416),
            'Punjab': (75.5941, 31.5497),
            'Rajasthan': (75.5941, 27.5922),
            'Sikkim': (88.5122, 27.5330),
            'Tamil Nadu': (78.6569, 11.1271),
            'Telangana': (78.4744, 17.3850),
            'Tripura': (91.5868, 23.8103),
            'Uttar Pradesh': (80.9462, 26.8467),
            'Uttarakhand': (79.0193, 30.0668),
            'West Bengal': (88.3639, 24.8355),
        }
    },
    '埃及': {
        'coords': {'lng': (24, 35), 'lat': (22, 32)},
        'divisions': {
            'Alexandria': (29.9187, 31.2001),
            'Aswan': (32.8872, 24.0889),
            'Cairo': (31.2357, 30.0444),
            'Giza': (30.8025, 30.0131),
            'Hurghada': (33.8169, 27.2574),
            'Luxor': (32.6401, 25.6872),
            'Sharm El-Sheikh': (34.3394, 27.9645),
            'Suez': (32.5498, 29.9668),
        }
    }
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

def extract_kml_pois(country_name, coords):
    """從 KML 提取指定國家的 POI"""
    pois = []
    lng_min, lng_max = coords['lng']
    lat_min, lat_max = coords['lat']

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

                        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
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

def create_markdown(poi_name, coords, city_name, division_name, country, desc):
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
country: {country}
division: {division_name}
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
**地區：** {division_name}
**國家：** {country}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

def get_nearest_division(coords, divisions):
    """根據座標找到最近的行政區"""
    lng, lat = coords
    min_distance = float('inf')
    best_division = None

    for division_name, (div_lng, div_lat) in divisions.items():
        distance = ((lng - div_lng) ** 2 + (lat - div_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_division = division_name

    return best_division

def process_country(country_name, country_config):
    """處理單個國家"""
    print(f"\n{'='*80}")
    print(f"🌍 {country_name}景點完整提取（KML → Wiki 1:1）")
    print(f"{'='*80}")

    # 1. 掃描 KML
    print(f"\n📄 掃描 KML 檔案...")
    kml_pois = extract_kml_pois(country_name, country_config['coords'])
    print(f"   發現 {len(kml_pois)} 個{country_name}POI")

    # 2. 清空舊 Wiki
    print(f"\n🗑️  清理舊 Wiki 結構...")
    country_path = os.path.join(WIKI_BASE, country_name)
    if os.path.isdir(country_path):
        for division_name in os.listdir(country_path):
            division_path = os.path.join(country_path, division_name)
            if os.path.isdir(division_path):
                for item in os.listdir(division_path):
                    item_path = os.path.join(division_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                    else:
                        try:
                            os.remove(item_path)
                        except:
                            pass
    print("   舊 Wiki 結構已清理")

    # 3. 組織景點
    print(f"\n📊 組織景點數據...")
    organized_pois = defaultdict(lambda: defaultdict(list))
    unlocated = []

    for poi in kml_pois:
        division = get_nearest_division((poi['lng'], poi['lat']), country_config['divisions'])
        if division:
            organized_pois[division]['POI'].append(poi)
        else:
            unlocated.append(poi)

    print(f"   已分類: {sum(len(cities) for cities in organized_pois.values())} 個")
    print(f"   未分類: {len(unlocated)} 個")

    # 4. 建立檔案
    print(f"\n{'='*80}")
    print(f"📝 建立檔案")
    print(f"{'='*80}\n")

    total_created = 0
    for division_idx, division_name in enumerate(sorted(organized_pois.keys()), 1):
        cities = organized_pois[division_name]
        division_created = 0

        print(f"[{division_idx:2d}/{len(organized_pois)}] {division_name}")

        for city_name in sorted(cities.keys()):
            pois = cities[city_name]
            city_path = os.path.join(WIKI_BASE, country_name, division_name, city_name)
            os.makedirs(city_path, exist_ok=True)

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
                            division_name,
                            country_name,
                            poi['desc']
                        )
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        total_created += 1
                        division_created += 1
                except:
                    pass

            if division_created > 0:
                print(f"      {city_name}: {division_created:4d} 個")

    print(f"\n{'='*80}")
    print(f"✅ {country_name}景點完整提取完成！")
    print(f"   新建檔案: {total_created} 個")
    print(f"{'='*80}")

# 處理三個國家
for country_name, country_config in COUNTRIES.items():
    process_country(country_name, country_config)

print(f"\n{'='*80}")
print(f"✅ 所有國家提取完成！")
print(f"{'='*80}")
