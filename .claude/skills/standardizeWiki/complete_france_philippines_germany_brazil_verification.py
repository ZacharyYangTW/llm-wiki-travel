#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法國、菲律賓、德國、巴西景點 1:1 清點驗證
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

# 四個國家的配置
COUNTRIES = {
    '法國': {
        'coords': {'lng': (-5, 8), 'lat': (42, 51)},
        'divisions': {
            'Paris': (-2.3522, 48.8566),
            'Auvergne-Rhône-Alpes': (4.8357, 45.7640),
            'Grand Est': (5.0455, 48.6291),
            'Hauts-de-France': (2.8773, 50.4501),
            'Île-de-France': (2.2139, 48.8626),
            'Normandy': (0.3674, 49.2628),
            'Nouvelle-Aquitaine': (-0.2272, 45.5017),
            'Occitania': (2.1686, 43.6047),
            'Pays de la Loire': (-0.5596, 47.4667),
            'Provence-Alpes-Côte d\'Azur': (5.3698, 43.9159),
        }
    },
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
            'Bavaria': (11.5739, 48.9021),
            'North Rhine-Westphalia': (7.4653, 51.4556),
            'Saarland': (6.8000, 49.3000),
            'Saxony': (13.4115, 51.1657),
        }
    },
    '巴西': {
        'coords': {'lng': (-74, -35), 'lat': (-33, 5)},
        'divisions': {
            'São Paulo': (-46.6333, -23.5505),
            'Rio de Janeiro': (-43.1729, -22.9068),
            'Paraná': (-51.4694, -23.3045),
            'Pará': (-52.2800, -1.4296),
        }
    }
}

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

def extract_coordinates(file_path):
    """從檔案提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

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

def get_wiki_files(country_name):
    """掃描 Wiki 國家目錄下的所有檔案"""
    files_info = defaultdict(lambda: defaultdict(list))
    country_path = os.path.join(WIKI_BASE, country_name)

    if not os.path.isdir(country_path):
        return files_info

    for division_name in sorted(os.listdir(country_path)):
        division_path = os.path.join(country_path, division_name)
        if not os.path.isdir(division_path):
            continue

        for city_name in sorted(os.listdir(division_path)):
            city_path = os.path.join(division_path, city_name)
            if os.path.isdir(city_path):
                for file_name in os.listdir(city_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(city_path, file_name)
                        coords = extract_coordinates(file_path)
                        poi_name = file_name[:-3]

                        files_info[division_name][city_name].append({
                            'name': poi_name,
                            'file': file_name,
                            'path': file_path,
                            'coords': coords
                        })

    return files_info

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def create_markdown(poi_name, coords, city_name, division_name, country_name, desc):
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
country: {country_name}
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
**國家：** {country_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

def verify_country(country_name, country_config):
    """驗證單個國家"""
    print(f"{'='*80}")
    print(f"🔍 {country_name}景點 1:1 清點驗證")
    print(f"{'='*80}")

    # 掃描 KML
    print(f"\n📄 掃描 KML 檔案...")
    kml_pois = extract_kml_pois(country_name, country_config['coords'])
    print(f"   發現 {len(kml_pois)} 個{country_name}POI")

    # 掃描 Wiki
    print(f"\n📂 掃描 Wiki {country_name}目錄...")
    wiki_files = get_wiki_files(country_name)
    total_wiki_files = sum(len(cities) for cities in wiki_files.values())
    print(f"   發現 {len(wiki_files)} 個地區")
    print(f"   發現 {total_wiki_files} 個 Wiki 檔案")

    # 清點結果
    total_matched = 0
    total_missing = 0
    total_extra = 0
    missing_list = []
    extra_list = []

    for division_name in sorted(country_config['divisions'].keys()):
        wiki_division_files = wiki_files.get(division_name, {})
        kml_division_pois = [p for p in kml_pois if get_nearest_division((p['lng'], p['lat']), country_config['divisions']) == division_name]

        if not kml_division_pois and not wiki_division_files:
            continue

        division_matched = 0
        division_missing = 0
        division_extra = 0

        for city_name, city_files in wiki_division_files.items():
            for wiki_file in city_files:
                found = False
                for kml_poi in kml_division_pois:
                    if kml_poi['name'].lower() == wiki_file['name'].lower():
                        found = True
                        division_matched += 1
                        break
                if not found:
                    division_extra += 1
                    extra_list.append({'division': division_name, 'city': city_name, 'file': wiki_file['file']})

        wiki_names = set()
        for city_files in wiki_division_files.values():
            for f in city_files:
                wiki_names.add(f['name'].lower())

        for kml_poi in kml_division_pois:
            if kml_poi['name'].lower() not in wiki_names:
                division_missing += 1
                missing_list.append({
                    'division': division_name,
                    'city': 'POI',
                    'name': kml_poi['name'],
                    'desc': kml_poi['desc'],
                    'lng': kml_poi['lng'],
                    'lat': kml_poi['lat']
                })

        total_matched += division_matched
        total_missing += division_missing
        total_extra += division_extra

    print(f"\n✓ 完全匹配: {total_matched} 個")
    print(f"✗ 缺失: {total_missing} 個")
    print(f"✗ 多餘: {total_extra} 個")

    # 處理缺失和多餘
    if missing_list:
        created = 0
        for item in missing_list:
            division = item['division']
            city = item['city']
            poi_name = item['name']
            coords = (item['lng'], item['lat'])

            city_path = os.path.join(WIKI_BASE, country_name, division, city)
            os.makedirs(city_path, exist_ok=True)

            clean_name = sanitize_filename(poi_name)
            filename = f"{clean_name}.md"
            filepath = os.path.join(city_path, filename)

            try:
                if not os.path.exists(filepath):
                    content = create_markdown(poi_name, coords, city, division, country_name, item['desc'])
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created += 1
            except:
                pass

        print(f"   建立缺失: {created} 個")

    if extra_list:
        deleted = 0
        for item in extra_list:
            division = item['division']
            city = item['city']
            filename = item['file']
            filepath = os.path.join(WIKI_BASE, country_name, division, city, filename)

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    deleted += 1
            except:
                pass

        print(f"   刪除多餘: {deleted} 個")

    print(f"✅ {country_name}清點完成！\n")

# 驗證四個國家
for country_name, country_config in COUNTRIES.items():
    verify_country(country_name, country_config)

print(f"{'='*80}")
print(f"✅ 所有國家驗證完成！")
print(f"{'='*80}")
