#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
馬來西亞景點 1:1 清點驗證
根據 KML 中的景點，驗證 Wiki 是否完全對應
缺失的景點建立、多餘的檔案刪除
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

def get_wiki_malaysia_files():
    """掃描 Wiki 馬來西亞目錄下的所有檔案"""
    files_info = defaultdict(lambda: defaultdict(list))
    malaysia_path = os.path.join(WIKI_BASE, "馬來西亞")

    if not os.path.isdir(malaysia_path):
        return files_info

    for state_name in sorted(os.listdir(malaysia_path)):
        state_path = os.path.join(malaysia_path, state_name)
        if not os.path.isdir(state_path):
            continue

        for city_name in sorted(os.listdir(state_path)):
            city_path = os.path.join(state_path, city_name)
            if os.path.isdir(city_path):
                for file_name in os.listdir(city_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(city_path, file_name)
                        coords = extract_coordinates(file_path)
                        poi_name = file_name[:-3]

                        files_info[state_name][city_name].append({
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

print("=" * 80)
print("🔍 馬來西亞景點 1:1 清點驗證")
print("=" * 80)

# 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_malaysia_pois()
print(f"   發現 {len(kml_pois)} 個馬來西亞 POI")

# 掃描 Wiki
print(f"\n📂 掃描 Wiki 馬來西亞目錄...")
wiki_files = get_wiki_malaysia_files()
total_wiki_files = sum(len(cities) for cities in wiki_files.values())
print(f"   發現 {len(wiki_files)} 個州")
print(f"   發現 {total_wiki_files} 個 Wiki 檔案")

# 清點結果
print(f"\n{'='*80}")
print(f"📊 清點結果")
print(f"{'='*80}\n")

total_matched = 0
total_missing = 0
total_extra = 0
missing_list = []
extra_list = []

for state_name in sorted(MALAYSIA_STATES.keys()):
    wiki_state_files = wiki_files.get(state_name, {})

    # 從 KML 找該州的景點
    kml_state_pois = [p for p in kml_pois if get_nearest_state((p['lng'], p['lat'])) == state_name]

    if not kml_state_pois and not wiki_state_files:
        continue

    state_matched = 0
    state_missing = 0
    state_extra = 0

    # 檢查所有 Wiki 檔案
    for city_name, city_files in wiki_state_files.items():
        for wiki_file in city_files:
            # 在 KML 中找到匹配
            found = False
            for kml_poi in kml_state_pois:
                if kml_poi['name'].lower() == wiki_file['name'].lower():
                    found = True
                    state_matched += 1
                    break
            if not found:
                state_extra += 1
                extra_list.append({'state': state_name, 'city': city_name, 'file': wiki_file['file']})

    # 檢查 KML 中未在 Wiki 中的
    wiki_names = set()
    for city_files in wiki_state_files.values():
        for f in city_files:
            wiki_names.add(f['name'].lower())

    for kml_poi in kml_state_pois:
        if kml_poi['name'].lower() not in wiki_names:
            state_missing += 1
            missing_list.append({
                'state': state_name,
                'city': 'POI',
                'name': kml_poi['name'],
                'desc': kml_poi['desc'],
                'lng': kml_poi['lng'],
                'lat': kml_poi['lat']
            })

    if state_matched > 0 or state_missing > 0 or state_extra > 0:
        status = ""
        if state_extra > 0:
            status += f" ⚠ 多餘:{state_extra}"
        if state_missing > 0:
            status += f" ⚠ 缺失:{state_missing}"
        if state_missing == 0 and state_extra == 0:
            status = " ✓"

        print(f"{state_name:<20} KML:{len(kml_state_pois):3d} Wiki:{len([f for cf in wiki_state_files.values() for f in cf]):3d} 匹配:{state_matched:3d}{status}")

    total_matched += state_matched
    total_missing += state_missing
    total_extra += state_extra

print(f"\n✓ 完全匹配: {total_matched:3d} 個")
print(f"✗ 缺失: {total_missing:3d} 個 (需建立)")
print(f"✗ 多餘: {total_extra:3d} 個 (需刪除)")
print(f"  KML 景點: {len(kml_pois):3d} 個")
print(f"  Wiki 檔案: {total_wiki_files:3d} 個")

# 處理缺失的景點
if missing_list:
    print(f"\n{'='*80}")
    print(f"➕ 建立缺失的景點檔案")
    print(f"{'='*80}\n")

    created = 0
    for item in missing_list:
        state = item['state']
        city = item['city']
        poi_name = item['name']
        coords = (item['lng'], item['lat'])

        city_path = os.path.join(WIKI_BASE, "馬來西亞", state, city)
        os.makedirs(city_path, exist_ok=True)

        clean_name = sanitize_filename(poi_name)
        filename = f"{clean_name}.md"
        filepath = os.path.join(city_path, filename)

        try:
            if not os.path.exists(filepath):
                content = create_markdown(poi_name, coords, city, state, item['desc'])
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                created += 1
                if created % 5 == 0 or created == 1:
                    print(f"[{created:3d}] ✓ {state}/{city}/{clean_name[:35]:35}")
        except Exception as e:
            print(f"   ✗ 建立失敗: {poi_name}: {str(e)}")

    print(f"\n   建立完成: {created} 個檔案")

# 刪除多餘的檔案
if extra_list:
    print(f"\n{'='*80}")
    print(f"🗑️  刪除多餘的 Wiki-only 檔案")
    print(f"{'='*80}\n")

    deleted = 0
    for item in extra_list:
        state = item['state']
        city = item['city']
        filename = item['file']
        filepath = os.path.join(WIKI_BASE, "馬來西亞", state, city, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted += 1
                if deleted % 5 == 0 or deleted == 1:
                    print(f"[{deleted:3d}] ✗ 刪除 {state}/{city}/{filename[:35]:35}")
        except Exception as e:
            print(f"   ✗ 刪除失敗: {filename}: {str(e)}")

    print(f"\n   刪除完成: {deleted} 個檔案")

print(f"\n{'='*80}")
print(f"✅ 馬來西亞清點完成！")
print(f"{'='*80}")
