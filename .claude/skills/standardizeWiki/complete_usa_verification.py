#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美國景點 1:1 清點驗證
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

USA_STATES = {
    'Alabama': {'center': (-86.9023, 32.8067)},
    'Alaska': {'center': (-152.4044, 64.2008)},
    'Arizona': {'center': (-111.4312, 33.7298)},
    'Arkansas': {'center': (-92.3731, 34.9697)},
    'California': {'center': (-119.4179, 36.1162)},
    'Colorado': {'center': (-105.3111, 39.0598)},
    'Connecticut': {'center': (-72.7554, 41.5978)},
    'Delaware': {'center': (-75.5277, 39.3185)},
    'Florida': {'center': (-81.5158, 27.9947)},
    'Georgia': {'center': (-83.6431, 33.0406)},
    'Hawaii': {'center': (-157.5, 20.7)},
    'Idaho': {'center': (-114.7420, 44.2405)},
    'Illinois': {'center': (-89.0022, 40.3495)},
    'Indiana': {'center': (-86.2604, 39.8494)},
    'Iowa': {'center': (-93.6196, 42.0115)},
    'Kansas': {'center': (-96.7265, 38.5266)},
    'Kentucky': {'center': (-84.6701, 37.6681)},
    'Louisiana': {'center': (-92.2896, 31.1695)},
    'Maine': {'center': (-69.3819, 45.2538)},
    'Maryland': {'center': (-76.8023, 39.0639)},
    'Massachusetts': {'center': (-71.5301, 42.2302)},
    'Michigan': {'center': (-84.5361, 43.3266)},
    'Minnesota': {'center': (-94.6859, 45.6945)},
    'Mississippi': {'center': (-89.6787, 32.7416)},
    'Missouri': {'center': (-92.2896, 38.4561)},
    'Montana': {'center': (-110.3626, 47.0527)},
    'Nebraska': {'center': (-100.4659, 41.4925)},
    'Nevada': {'center': (-117.0554, 38.8026)},
    'New Hampshire': {'center': (-71.5653, 43.4525)},
    'New Jersey': {'center': (-74.5210, 40.2989)},
    'New Mexico': {'center': (-106.6504, 34.5199)},
    'New York': {'center': (-75.7597, 42.1657)},
    'North Carolina': {'center': (-79.8064, 35.6301)},
    'North Dakota': {'center': (-101.4036, 47.5289)},
    'Ohio': {'center': (-82.9071, 40.3888)},
    'Oklahoma': {'center': (-96.9289, 35.5653)},
    'Oregon': {'center': (-122.0710, 43.8041)},
    'Pennsylvania': {'center': (-77.2098, 40.5908)},
    'Rhode Island': {'center': (-71.5117, 41.6809)},
    'South Carolina': {'center': (-80.9066, 33.8361)},
    'South Dakota': {'center': (-99.4388, 44.2998)},
    'Tennessee': {'center': (-86.6923, 35.7478)},
    'Texas': {'center': (-99.9018, 31.9686)},
    'Utah': {'center': (-111.8910, 39.3210)},
    'Vermont': {'center': (-72.5754, 44.0459)},
    'Virginia': {'center': (-78.1694, 37.7693)},
    'Washington': {'center': (-121.4905, 47.7511)},
    'West Virginia': {'center': (-81.6326, 38.4912)},
    'Wisconsin': {'center': (-89.6165, 44.2685)},
    'Wyoming': {'center': (-107.5512, 42.7559)},
}

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

def get_wiki_usa_files():
    """掃描 Wiki 美國目錄下的所有檔案"""
    files_info = defaultdict(lambda: defaultdict(list))
    usa_path = os.path.join(WIKI_BASE, "美國")

    if not os.path.isdir(usa_path):
        return files_info

    for state_name in sorted(os.listdir(usa_path)):
        state_path = os.path.join(usa_path, state_name)
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

print("=" * 80)
print("🔍 美國景點 1:1 清點驗證")
print("=" * 80)

# 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_usa_pois()
print(f"   發現 {len(kml_pois)} 個美國 POI")

# 掃描 Wiki
print(f"\n📂 掃描 Wiki 美國目錄...")
wiki_files = get_wiki_usa_files()
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

for state_name in sorted(USA_STATES.keys()):
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

        city_path = os.path.join(WIKI_BASE, "美國", state, city)
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
                if created % 20 == 0 or created == 1:
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
        filepath = os.path.join(WIKI_BASE, "美國", state, city, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted += 1
                if deleted % 20 == 0 or deleted == 1:
                    print(f"[{deleted:3d}] ✗ 刪除 {state}/{city}/{filename[:35]:35}")
        except Exception as e:
            print(f"   ✗ 刪除失敗: {filename}: {str(e)}")

    print(f"\n   刪除完成: {deleted} 個檔案")

# 清理空目錄
print(f"\n🗑️  清理空目錄...")
usa_path = os.path.join(WIKI_BASE, "美國")
removed_dirs = 0

if os.path.isdir(usa_path):
    for state_name in os.listdir(usa_path):
        state_path = os.path.join(usa_path, state_name)
        if not os.path.isdir(state_path):
            continue

        for city_name in list(os.listdir(state_path)):
            city_path = os.path.join(state_path, city_name)
            if os.path.isdir(city_path):
                if not os.listdir(city_path):
                    try:
                        os.rmdir(city_path)
                        removed_dirs += 1
                    except:
                        pass

if removed_dirs > 0:
    print(f"   已移除 {removed_dirs} 個空目錄")
else:
    print(f"   無空目錄")

print(f"\n{'='*80}")
print(f"✅ 美國清點完成！")
print(f"{'='*80}")
