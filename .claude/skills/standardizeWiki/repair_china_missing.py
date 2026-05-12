#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
補建中國缺失的景點檔案
根據 KML 和現有 Wiki 檔案進行對比，建立缺失的檔案
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

sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from china_cities_coords import CHINA_PROVINCES_COORDS, CHINA_CITIES_COORDS, get_nearest_province, get_nearest_city

def extract_kml_china_pois():
    """從 KML 提取中國範圍內的所有 POI"""
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

                        if 73 <= lng <= 135 and 18 <= lat <= 54:
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

def get_wiki_china_files():
    """掃描 Wiki 中國目錄下的所有檔案"""
    files_info = defaultdict(lambda: defaultdict(list))
    china_path = os.path.join(WIKI_BASE, "中國")

    if not os.path.isdir(china_path):
        return files_info

    for province_name in sorted(os.listdir(china_path)):
        province_path = os.path.join(china_path, province_name)
        if not os.path.isdir(province_path):
            continue

        for city_name in sorted(os.listdir(province_path)):
            city_path = os.path.join(province_path, city_name)
            if os.path.isdir(city_path):
                for file_name in os.listdir(city_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(city_path, file_name)
                        coords = extract_coordinates(file_path)
                        poi_name = file_name[:-3]

                        files_info[province_name][city_name].append({
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
country: 中國
city: {city_name}
province: {province_name}
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
**省份：** {province_name}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

print("=" * 80)
print("🔧 中國景點補建 - 缺失檔案")
print("=" * 80)

# 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_china_pois()
print(f"   發現 {len(kml_pois)} 個中國 POI")

# 掃描 Wiki
print(f"\n📂 掃描 Wiki 中國目錄...")
wiki_files = get_wiki_china_files()
print(f"   發現 {len(wiki_files)} 個省份")

# 找出缺失的檔案
print(f"\n{'='*80}")
print(f"🔍 識別缺失的景點")
print(f"{'='*80}\n")

missing_pois = []

for province_name in sorted(CHINA_PROVINCES_COORDS.keys()):
    cities_in_province = CHINA_CITIES_COORDS.get(province_name, {})

    for city_name in sorted(cities_in_province.keys()):
        # 從 KML 找該城市的景點
        kml_city_pois = []
        for poi in kml_pois:
            found_province = get_nearest_province((poi['lng'], poi['lat']))
            if found_province == province_name:
                found_city = get_nearest_city((poi['lng'], poi['lat']), province_name)
                if found_city == city_name:
                    kml_city_pois.append(poi)

        # 從 Wiki 獲取該城市的檔案
        wiki_city_files = wiki_files.get(province_name, {}).get(city_name, [])
        wiki_names = set([f['name'] for f in wiki_city_files])

        # 找出缺失的
        for kml_poi in kml_city_pois:
            if kml_poi['name'] not in wiki_names:
                missing_pois.append({
                    'province': province_name,
                    'city': city_name,
                    'name': kml_poi['name'],
                    'desc': kml_poi['desc'],
                    'lng': kml_poi['lng'],
                    'lat': kml_poi['lat']
                })

print(f"發現缺失景點: {len(missing_pois)} 個\n")

# 建立缺失的檔案
if missing_pois:
    print(f"{'='*80}")
    print(f"➕ 建立缺失的景點檔案")
    print(f"{'='*80}\n")

    created = 0
    failed = 0

    for idx, item in enumerate(missing_pois, 1):
        province = item['province']
        city = item['city']
        poi_name = item['name']
        coords = (item['lng'], item['lat'])

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "中國", province, city)
        os.makedirs(city_path, exist_ok=True)

        # 建立檔案（清理檔名）
        clean_name = sanitize_filename(poi_name)
        filename = f"{clean_name}.md"
        filepath = os.path.join(city_path, filename)

        try:
            if not os.path.exists(filepath):
                content = create_markdown(poi_name, coords, city, province, item['desc'])
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                created += 1
                if idx % 10 == 0 or idx == 1 or idx == len(missing_pois):
                    print(f"[{idx:4d}/{len(missing_pois):4d}] ✓ {province}/{city}/{clean_name[:35]:35}")
            else:
                print(f"[{idx:4d}] ⚠ 檔案已存在: {province}/{city}/{filename}")
        except Exception as e:
            failed += 1
            print(f"[{idx:4d}] ✗ 建立失敗: {poi_name}: {str(e)}")

    print(f"\n{'='*80}")
    print(f"📊 建立結果")
    print(f"{'='*80}\n")
    print(f"✓ 建立成功: {created:4d} 個")
    print(f"✗ 建立失敗: {failed:4d} 個")
    print(f"📈 總計: {len(missing_pois):4d} 個缺失")

    print(f"\n{'='*80}")
    print(f"✅ 補建完成！")
    print(f"{'='*80}")
else:
    print("✓ 沒有缺失的檔案")
