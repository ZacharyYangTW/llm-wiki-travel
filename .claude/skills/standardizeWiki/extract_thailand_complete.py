#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取泰國景點
建立 Wiki 二級結構：府 + 城市
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

def extract_kml_thailand_pois():
    """從 KML 提取泰國範圍內的所有 POI"""
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

                        # 檢查是否在泰國範圍內
                        if 97 <= lng <= 106 and 6 <= lat <= 21:
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
country: 泰國
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
**府：** {province_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

# 泰國主要府名
THAILAND_PROVINCES = {
    'Bangkok': (100.5018, 13.7563),
    'Chiang Mai': (98.9853, 18.7883),
    'Phuket': (98.3923, 8.0863),
    'Chiang Rai': (99.8765, 19.9100),
    'Krabi': (98.9133, 8.0863),
    'Phang Nga': (98.4375, 8.4246),
    'Chumphon': (99.1802, 8.4681),
    'Ranong': (98.6330, 9.9683),
    'Satun': (100.0717, 7.1933),
    'Trang': (99.6083, 7.5603),
    'Nakhon Si Thammarat': (100.0767, 8.4304),
    'Phatthalung': (100.0769, 8.0410),
    'Songkhla': (100.6034, 7.1906),
    'Yala': (101.2833, 6.5406),
    'Pattani': (101.9667, 6.8347),
    'Narathiwat': (101.8243, 6.4263),
    'Rayong': (101.3064, 12.6828),
    'Chon Buri': (100.9853, 13.3611),
    'Samut Prakan': (100.5970, 13.5917),
    'Samut Sakhon': (100.3047, 13.5483),
    'Samut Songkhram': (100.0038, 13.4125),
    'Bangkok Noi': (100.4978, 13.7250),
    'Prachuap Khiri Khan': (99.8069, 12.1583),
    'Phetchaburi': (99.9483, 13.1083),
    'Lopburi': (100.6517, 14.8000),
    'Saraburi': (101.2242, 14.5319),
    'Nakhon Nayok': (101.2061, 14.2319),
    'Nakhon Ratchasima': (101.7167, 14.9669),
    'Korat': (101.7167, 14.9669),
    'Buriram': (103.1044, 14.9997),
    'Surin': (104.9147, 14.8856),
    'Sisaket': (104.8553, 15.1658),
    'Ubon Ratchathani': (105.2667, 15.2500),
    'Amnat Charoen': (104.6289, 16.0558),
    'Yasothon': (104.7719, 15.7858),
    'Maha Sarakham': (103.3036, 16.1897),
    'Kalsin': (103.1961, 16.4186),
    'Roi Et': (103.6589, 16.2500),
    'Nakhon Phanom': (104.7733, 17.4169),
    'Mukdahan': (104.7289, 16.5386),
    'Sakon Nakhon': (104.8722, 17.1500),
    'Nong Khai': (102.7447, 17.8719),
    'Loei': (101.7258, 17.4850),
    'Udon Thani': (102.7858, 17.4132),
    'Khon Kaen': (102.8360, 16.4411),
    'Kalasin': (103.1947, 16.4294),
    'Chaiyaphum': (101.8133, 15.8094),
    'Phichit': (100.3478, 15.8167),
    'Phetchabun': (101.1456, 16.1192),
    'Nakhon Sawan': (100.1344, 15.6794),
    'Sukhothai': (99.8242, 17.0058),
    'Tak': (99.1242, 16.8839),
    'Kamphaeng Phet': (99.5325, 15.4167),
    'Uttaradit': (100.0978, 17.6136),
    'Phichit': (100.3478, 15.8167),
    'Nan': (100.7764, 18.7744),
    'Phayao': (100.8147, 19.1872),
    'Lampang': (99.4978, 18.2881),
    'Lamphun': (99.0089, 18.5738),
    'Mae Hong Son': (97.9633, 19.2981),
}

def get_nearest_province(coords):
    """根據座標找到最近的泰國府"""
    lng, lat = coords
    min_distance = float('inf')
    best_province = None

    for province_name, (prov_lng, prov_lat) in THAILAND_PROVINCES.items():
        distance = ((lng - prov_lng) ** 2 + (lat - prov_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_province = province_name

    return best_province

print("=" * 80)
print("🌍 泰國景點完整提取（KML → Wiki 1:1）")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_thailand_pois()
print(f"   發現 {len(kml_pois)} 個泰國 POI")

# 2. 清空舊的泰國 Wiki
print("\n🗑️  清理舊 Wiki 結構...")
thailand_path = os.path.join(WIKI_BASE, "泰國")
if os.path.isdir(thailand_path):
    for province_name in os.listdir(thailand_path):
        province_path = os.path.join(thailand_path, province_name)
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

# 3. 按府/城市組織景點
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
        city_path = os.path.join(WIKI_BASE, "泰國", province_name, city_name)
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
print(f"✓ 府: {len(organized_pois):5d} 個")

if unlocated:
    print(f"\n⚠️  未定位景點: {len(unlocated)} 個")

print(f"\n{'='*80}")
print(f"✅ 泰國景點完整提取完成！")
print(f"{'='*80}")
