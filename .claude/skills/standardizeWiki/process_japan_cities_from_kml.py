#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
為每個日本二級目錄（市町村）從 KML 中提取對應的 POI
"""

import os
import sys
import xml.etree.ElementTree as ET
import re
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

# 導入日本市町村座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

def extract_kml_pois():
    """從 KML 提取所有日本 POI"""
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

                        # 檢查是否在日本
                        if 130 <= lng <= 145 and 30 <= lat <= 46:
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

def get_wiki_cities():
    """獲取 Wiki 中所有日本二級目錄（都道府縣/市町村）"""
    cities = []
    japan_path = os.path.join(WIKI_BASE, "日本")

    if not os.path.isdir(japan_path):
        return cities

    for pref_name in sorted(os.listdir(japan_path)):
        pref_path = os.path.join(japan_path, pref_name)
        if not os.path.isdir(pref_path):
            continue

        for city_name in sorted(os.listdir(pref_path)):
            city_path = os.path.join(pref_path, city_name)
            if os.path.isdir(city_path):
                # 獲取該市町村下的所有檔案
                files = [f for f in os.listdir(city_path) if f.endswith('.md')]
                cities.append({
                    'pref': pref_name,
                    'city': city_name,
                    'path': city_path,
                    'files': files
                })

    return cities

def find_pois_for_city(city_name, kml_pois):
    """為一個市町村從 KML 中找到對應的 POI"""
    # 移除 "市"、"町"、"村" 等後綴來進行模糊匹配
    city_base = city_name.replace('市', '').replace('町', '').replace('村', '').strip()

    matching_pois = []

    for poi in kml_pois:
        # 檢查 POI 名稱是否包含城市名
        if city_name in poi['name'] or city_base in poi['name']:
            matching_pois.append(poi)

    return matching_pois

def create_markdown(poi):
    """為 POI 創建 Markdown 內容"""
    timestamp = datetime.now().isoformat() + 'Z'

    slug = poi['name'].lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    frontmatter = f"""---
title: {poi['name']}
slug: {slug}
location: {poi.get('location', '')}
country: 日本
city: {poi.get('city', '')}
category: 景點
tags: ["景點"]
coordinates: [{poi['lng']}, {poi['lat']}]
md5:
created_at: {timestamp}
processed: false
graph-excluded: false
source_url: raw/travel/Zachary's World Trip.kml
source_type: kml-placemark
---

# {poi['name']}

## 基本資訊

**位置：** {poi.get('location', '')}
**國家：** 日本
**座標：** {poi['lng']}, {poi['lat']}

## 描述

{poi['desc'] or '待補充'}
"""

    return frontmatter

print("=" * 80)
print("📝 為日本所有二級目錄從 KML 提取 POI")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_pois()
print(f"   日本 POI: {len(kml_pois)} 個")

# 2. 獲取所有市町村
print(f"\n🗂️  掃描 Wiki 日本二級目錄...")
cities = get_wiki_cities()
print(f"   市町村: {len(cities)} 個")

# 3. 逐個處理每個市町村
print(f"\n{'='*80}")
print(f"🔄 逐個處理市町村")
print(f"{'='*80}\n")

total_created = 0
total_skipped = 0
total_wiki_only = 0

for idx, city_info in enumerate(cities, 1):
    pref = city_info['pref']
    city = city_info['city']
    path = city_info['path']
    wiki_files = set(city_info['files'])

    # 從 KML 找到對應的 POI
    kml_matches = find_pois_for_city(city, kml_pois)

    # 去重（移除已在 Wiki 中的檔案）
    kml_new = []
    kml_duplicates = []

    for poi in kml_matches:
        filename = f"{poi['name']}.md"
        if filename in wiki_files:
            kml_duplicates.append(poi['name'])
        else:
            kml_new.append(poi)

    # 標記 Wiki Only 檔案（在 Wiki 中但不在 KML 中）
    kml_names = set([p['name'] for p in kml_matches])
    wiki_only = [f[:-3] for f in wiki_files if f[:-3] not in kml_names]

    # 顯示進度
    print(f"[{idx:3d}/{len(cities)}] {pref}/{city}")
    print(f"      Wiki 檔案: {len(wiki_files):3d} | KML 匹配: {len(kml_matches):3d} | 新增: {len(kml_new):3d} | 重複: {len(kml_duplicates):3d} | Only: {len(wiki_only):3d}")

    if wiki_only:
        print(f"      🔴 Wiki Only: {', '.join(wiki_only[:5])}{' ...' if len(wiki_only) > 5 else ''}")

    # 創建新檔案
    for poi in kml_new:
        poi['location'] = city
        poi['city'] = city

        filename = f"{poi['name']}.md"
        filepath = os.path.join(path, filename)

        try:
            content = create_markdown(poi)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_created += 1
        except Exception as e:
            print(f"      ✗ 創建失敗: {poi['name']}: {str(e)}")

    total_skipped += len(kml_duplicates)
    total_wiki_only += len(wiki_only)

print(f"\n{'='*80}")
print(f"✅ 完成")
print(f"  新增: {total_created} 個檔案")
print(f"  重複跳過: {total_skipped} 個")
print(f"  Wiki Only: {total_wiki_only} 個（需要確認）")
print(f"{'='*80}")
