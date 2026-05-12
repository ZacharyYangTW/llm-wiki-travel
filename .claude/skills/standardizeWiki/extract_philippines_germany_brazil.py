#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取菲律賓、德國、巴西景點
建立 Wiki 二級結構：地區/州 + 城市
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

# 地區座標定義
REGIONS = {
    '菲律賓': {
        'coords': {'lng': (117, 127), 'lat': (5, 21)},
        'divisions': {
            'Luzon': (121.0000, 15.5000),
            'Visayas': (123.0000, 10.5000),
            'Mindanao': (125.0000, 7.0000),
        }
    },
    '德國': {
        'coords': {'lng': (6, 15), 'lat': (47, 56)},
        'divisions': {
            'Baden-Württemberg': (9.1050, 48.7758),
            'Bavaria': (11.5739, 48.9021),
            'Berlin': (13.4050, 52.5200),
            'Brandenburg': (13.0000, 52.5000),
            'Bremen': (8.8017, 53.0793),
            'Hamburg': (9.9937, 53.5511),
            'Hesse': (9.1829, 50.1109),
            'Lower Saxony': (9.7575, 52.6745),
            'Mecklenburg-Vorpommern': (12.5000, 54.0000),
            'North Rhine-Westphalia': (7.4653, 51.4556),
            'Rhineland-Palatinate': (7.1000, 50.0000),
            'Saarland': (6.8000, 49.3000),
            'Saxony': (13.4115, 51.1657),
            'Saxony-Anhalt': (11.8000, 52.0000),
            'Schleswig-Holstein': (10.0000, 54.3333),
            'Thuringia': (11.0000, 50.5000),
        }
    },
    '巴西': {
        'coords': {'lng': (-74, -35), 'lat': (-33, 5)},
        'divisions': {
            'São Paulo': (-46.6333, -23.5505),
            'Rio de Janeiro': (-43.1729, -22.9068),
            'Minas Gerais': (-44.8733, -18.9130),
            'Bahia': (-47.8822, -12.9822),
            'Rio Grande do Sul': (-51.4332, -27.5969),
            'Paraná': (-51.4694, -23.3045),
            'Pernambuco': (-35.0918, -7.9465),
            'Ceará': (-38.5244, -3.7319),
            'Pará': (-52.2800, -1.4296),
            'Santa Catarina': (-49.6401, -27.3345),
            'Brasília': (-47.9218, -15.8266),
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
    """從 KML 提取指定國家範圍內的所有 POI"""
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

def process_country(country_name, country_data):
    """處理單個國家"""
    print(f"\n{'='*80}")
    print(f"🌍 {country_name}景點完整提取（KML → Wiki 1:1）")
    print(f"{'='*80}")

    # 1. 掃描 KML
    print(f"\n📄 掃描 KML 檔案...")
    kml_pois = extract_kml_pois(country_name, country_data['coords'])
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
        division = get_nearest_division((poi['lng'], poi['lat']), country_data['divisions'])
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
for country_name, country_data in REGIONS.items():
    process_country(country_name, country_data)

print(f"\n{'='*80}")
print(f"✅ 所有國家提取完成！")
print(f"{'='*80}")
