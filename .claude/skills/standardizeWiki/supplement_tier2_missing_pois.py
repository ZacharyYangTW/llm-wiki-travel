#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
補充第二梯隊缺失景點
根據座標找到最近的行政區並建立檔案
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
import io
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

# 第二梯隊國家定義及其行政區中心
COUNTRIES = {
    '越南': {
        'coords': {'lng': (102, 110), 'lat': (8, 24)},
        'divisions': {
            'Da Nang': (107.5711, 16.0544),
            'Dong Nai': (107.0797, 10.9610),
            'Ha Giang': (104.9833, 22.8000),
            'Hai Phong': (106.6837, 20.8449),
            'Hanoi': (105.8542, 21.0285),
            'Ho Chi Minh City': (106.6663, 10.7769),
            'Long An': (106.2500, 10.5500),
            'Nam Dinh': (106.1833, 20.4167),
            'Quang Nam': (107.6931, 15.5794),
            'Quang Ninh': (107.2892, 21.0333),
            'Tay Ninh': (106.0973, 11.3100),
            'Thanh Hoa': (105.7719, 19.8074),
            'Tien Giang': (106.3667, 10.2667),
        }
    },
    '荷蘭': {
        'coords': {'lng': (3, 8), 'lat': (50, 54)},
        'divisions': {
            'Limburg': (5.8708, 50.8353),
            'North Brabant': (5.4762, 51.4447),
            'North Holland': (5.2913, 52.5170),
            'Overijssel': (6.1600, 52.5000),
            'South Holland': (4.2768, 52.0705),
            'Utrecht': (5.1214, 52.0907),
        }
    },
    '西班牙': {
        'coords': {'lng': (-10, 5), 'lat': (36, 43)},
        'divisions': {
            'Catalonia': (2.1734, 41.5868),
            'Madrid': (-3.7038, 40.4168),
        }
    },
    '奧地利': {
        'coords': {'lng': (9, 17), 'lat': (47, 49)},
        'divisions': {
            'Salzburg': (13.0550, 47.8095),
            'Vienna': (16.3738, 48.2082),
        }
    },
    '紐西蘭': {
        'coords': {'lng': (166, 179), 'lat': (-47, -34)},
        'divisions': {
            'Christchurch': (172.6362, -43.5321),
        }
    },
    '新加坡': {
        'coords': {'lng': (103, 104), 'lat': (1, 2)},
        'divisions': {
            'Central': (103.8500, 1.3500),
        }
    },
    '匈牙利': {
        'coords': {'lng': (16, 23), 'lat': (46, 49)},
        'divisions': {
            'Budapest': (19.0402, 47.4979),
        }
    },
    '秘魯': {
        'coords': {'lng': (-81, -68), 'lat': (-18, 0)},
        'divisions': {
            'Cusco': (-71.9789, -13.5319),
        }
    },
    '捷克': {
        'coords': {'lng': (12, 19), 'lat': (48, 51)},
        'divisions': {
            'Prague': (14.4378, 50.0755),
        }
    },
    '柬埔寨': {
        'coords': {'lng': (102, 107), 'lat': (10, 15)},
        'divisions': {
            'Phnom Penh': (104.9282, 11.5564),
        }
    },
    '智利': {
        'coords': {'lng': (-77, -66), 'lat': (-56, -17)},
        'divisions': {}
    },
    '比利時': {
        'coords': {'lng': (2, 6), 'lat': (49, 51)},
        'divisions': {
            'Brussels': (4.3517, 50.8503),
        }
    },
    '盧森堡': {
        'coords': {'lng': (5, 7), 'lat': (49, 51)},
        'divisions': {
            'Luxembourg City': (6.1296, 49.6116),
        }
    },
    '印尼': {
        'coords': {'lng': (95, 141), 'lat': (-11, 6)},
        'divisions': {
            'Jakarta': (106.8456, -6.2088),
        }
    },
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
                            pois.append({'name': name, 'desc': desc, 'lng': lng, 'lat': lat})
                    except:
                        pass
    except Exception as e:
        print(f"KML 解析錯誤: {str(e)}", file=sys.stderr)

    return pois

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
                        poi_name = file_name[:-3]
                        files_info[division_name][city_name].append({'name': poi_name, 'file': file_name})

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

def create_markdown(poi_name, coords, city_name, division_name, country, desc):
    """為 POI 創建 Markdown 內容"""
    timestamp = datetime.now().isoformat() + 'Z'
    slug = poi_name.lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    if desc:
        desc_text = desc.replace('<br>', '\n').strip()
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

def supplement_missing_pois():
    """補充缺失景點"""
    print("=" * 80)
    print("📝 補充第二梯隊缺失景點")
    print("=" * 80)

    total_created = 0
    total_failed = 0

    for country_name in sorted(COUNTRIES.keys()):
        print(f"\n{'='*80}")
        print(f"🌍 {country_name}")
        print(f"{'='*80}")

        # 掃描 KML
        coords = COUNTRIES[country_name]['coords']
        kml_pois = extract_kml_pois(country_name, coords)

        if len(kml_pois) == 0:
            print(f"   未發現 KML POI")
            continue

        # 掃描 Wiki
        wiki_files = get_wiki_files(country_name)

        # 建立 Wiki 名稱集合（小寫）
        wiki_names = set()
        for division_files in wiki_files.values():
            for city_files in division_files.values():
                for f in city_files:
                    wiki_names.add(f['name'].lower())

        # 找出缺失的景點並建立檔案
        missing = []
        for kml_poi in kml_pois:
            if kml_poi['name'].lower() not in wiki_names:
                missing.append(kml_poi)

        if len(missing) == 0:
            print(f"   ✅ 無缺失景點")
            continue

        print(f"   發現缺失景點 {len(missing)} 個，開始建立...")

        created = 0
        failed = 0

        for poi in missing:
            division = get_nearest_division((poi['lng'], poi['lat']), COUNTRIES[country_name]['divisions'])

            if not division:
                print(f"   ⚠️  無法分類: {poi['name'][:40]}... (座標: {poi['lng']:.4f}, {poi['lat']:.4f})")
                failed += 1
                continue

            city_name = 'POI'
            city_path = os.path.join(WIKI_BASE, country_name, division, city_name)
            os.makedirs(city_path, exist_ok=True)

            clean_name = sanitize_filename(poi['name'])
            filename = f"{clean_name}.md"
            filepath = os.path.join(city_path, filename)

            try:
                if not os.path.exists(filepath):
                    content = create_markdown(
                        poi['name'],
                        (poi['lng'], poi['lat']),
                        city_name,
                        division,
                        country_name,
                        poi['desc']
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created += 1
                    total_created += 1
            except Exception as e:
                print(f"   ❌ 建立失敗: {poi['name'][:40]}... ({str(e)})")
                failed += 1
                total_failed += 1

        if created > 0:
            print(f"   ✅ 成功建立: {created} 個檔案")
        if failed > 0:
            print(f"   ❌ 建立失敗: {failed} 個檔案")

    print(f"\n{'='*80}")
    print(f"✅ 補充完成！")
    print(f"   成功建立: {total_created} 個檔案")
    print(f"   建立失敗: {total_failed} 個檔案")
    print(f"{'='*80}")

if __name__ == '__main__':
    supplement_missing_pois()
