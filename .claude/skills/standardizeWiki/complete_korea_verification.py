#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
韓國景點 1:1 清點驗證
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

def get_wiki_korea_files():
    """掃描 Wiki 韓國目錄下的所有檔案"""
    files_info = defaultdict(lambda: defaultdict(list))
    korea_path = os.path.join(WIKI_BASE, "韓國")

    if not os.path.isdir(korea_path):
        return files_info

    for province_name in sorted(os.listdir(korea_path)):
        province_path = os.path.join(korea_path, province_name)
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

print("=" * 80)
print("🔍 韓國景點 1:1 清點驗證")
print("=" * 80)

# 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_korea_pois()
print(f"   發現 {len(kml_pois)} 個韓國 POI")

# 掃描 Wiki
print(f"\n📂 掃描 Wiki 韓國目錄...")
wiki_files = get_wiki_korea_files()
total_wiki_files = sum(len(cities) for cities in wiki_files.values())
print(f"   發現 {len(wiki_files)} 個道")
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

for province_name in sorted(KOREA_PROVINCES.keys()):
    wiki_province_files = wiki_files.get(province_name, {})

    # 從 KML 找該道的景點
    kml_province_pois = [p for p in kml_pois if get_nearest_province((p['lng'], p['lat'])) == province_name]

    if not kml_province_pois and not wiki_province_files:
        continue

    province_matched = 0
    province_missing = 0
    province_extra = 0

    # 檢查所有 Wiki 檔案
    for city_name, city_files in wiki_province_files.items():
        for wiki_file in city_files:
            # 在 KML 中找到匹配
            found = False
            for kml_poi in kml_province_pois:
                if kml_poi['name'].lower() == wiki_file['name'].lower():
                    found = True
                    province_matched += 1
                    break
            if not found:
                province_extra += 1
                extra_list.append({'province': province_name, 'city': city_name, 'file': wiki_file['file']})

    # 檢查 KML 中未在 Wiki 中的
    wiki_names = set()
    for city_files in wiki_province_files.values():
        for f in city_files:
            wiki_names.add(f['name'].lower())

    for kml_poi in kml_province_pois:
        if kml_poi['name'].lower() not in wiki_names:
            province_missing += 1
            missing_list.append({
                'province': province_name,
                'city': 'POI',
                'name': kml_poi['name'],
                'desc': kml_poi['desc'],
                'lng': kml_poi['lng'],
                'lat': kml_poi['lat']
            })

    if province_matched > 0 or province_missing > 0 or province_extra > 0:
        status = ""
        if province_extra > 0:
            status += f" ⚠ 多餘:{province_extra}"
        if province_missing > 0:
            status += f" ⚠ 缺失:{province_missing}"
        if province_missing == 0 and province_extra == 0:
            status = " ✓"

        print(f"{province_name:<20} KML:{len(kml_province_pois):3d} Wiki:{len([f for cf in wiki_province_files.values() for f in cf]):3d} 匹配:{province_matched:3d}{status}")

    total_matched += province_matched
    total_missing += province_missing
    total_extra += province_extra

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
        province = item['province']
        city = item['city']
        poi_name = item['name']
        coords = (item['lng'], item['lat'])

        city_path = os.path.join(WIKI_BASE, "韓國", province, city)
        os.makedirs(city_path, exist_ok=True)

        clean_name = sanitize_filename(poi_name)
        filename = f"{clean_name}.md"
        filepath = os.path.join(city_path, filename)

        try:
            if not os.path.exists(filepath):
                content = create_markdown(poi_name, coords, city, province, item['desc'])
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                created += 1
                if created % 20 == 0 or created == 1:
                    print(f"[{created:3d}] ✓ {province}/{city}/{clean_name[:35]:35}")
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
        province = item['province']
        city = item['city']
        filename = item['file']
        filepath = os.path.join(WIKI_BASE, "韓國", province, city, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted += 1
                if deleted % 20 == 0 or deleted == 1:
                    print(f"[{deleted:3d}] ✗ 刪除 {province}/{city}/{filename[:35]:35}")
        except Exception as e:
            print(f"   ✗ 刪除失敗: {filename}: {str(e)}")

    print(f"\n   刪除完成: {deleted} 個檔案")

# 清理空目錄
print(f"\n🗑️  清理空目錄...")
korea_path = os.path.join(WIKI_BASE, "韓國")
removed_dirs = 0

if os.path.isdir(korea_path):
    for province_name in os.listdir(korea_path):
        province_path = os.path.join(korea_path, province_name)
        if not os.path.isdir(province_path):
            continue

        for city_name in list(os.listdir(province_path)):
            city_path = os.path.join(province_path, city_name)
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
print(f"✅ 韓國清點完成！")
print(f"{'='*80}")
