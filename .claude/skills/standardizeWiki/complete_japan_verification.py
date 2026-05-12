#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本景點 1:1 清點驗證
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

# 導入日本市町村座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

def extract_kml_japan_pois():
    """從 KML 提取日本範圍內的所有 POI"""
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

                        # 檢查是否在日本範圍內（包含沖繩）
                        if 125 <= lng <= 145 and 24 <= lat <= 46:
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

def find_poi_in_kml(poi_name, coords, kml_pois, threshold=0.01):
    """在 KML 中找到匹配的 POI"""
    # 先按名稱精確匹配
    for kml_poi in kml_pois:
        if kml_poi['name'].lower() == poi_name.lower():
            return kml_poi

    # 按座標近似匹配
    if coords:
        lng, lat = coords
        for kml_poi in kml_pois:
            dist = ((kml_poi['lng'] - lng) ** 2 + (kml_poi['lat'] - lat) ** 2) ** 0.5
            if dist < threshold:
                return kml_poi

    return None

def get_wiki_japan_files():
    """掃描 Wiki 日本目錄下的所有檔案"""
    files_info = defaultdict(lambda: defaultdict(list))
    japan_path = os.path.join(WIKI_BASE, "日本")

    if not os.path.isdir(japan_path):
        return files_info

    for pref_name in sorted(os.listdir(japan_path)):
        pref_path = os.path.join(japan_path, pref_name)
        if not os.path.isdir(pref_path):
            continue

        for city_name in sorted(os.listdir(pref_path)):
            city_path = os.path.join(pref_path, city_name)
            if os.path.isdir(city_path):
                for file_name in os.listdir(city_path):
                    if file_name.endswith('.md'):
                        file_path = os.path.join(city_path, file_name)
                        coords = extract_coordinates(file_path)
                        poi_name = file_name[:-3]  # 移除 .md

                        files_info[pref_name][city_name].append({
                            'name': poi_name,
                            'file': file_name,
                            'path': file_path,
                            'coords': coords
                        })

    return files_info

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    # 移除或替換不允許的字符
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    # 移除其他特殊控制字符
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    # 移除首尾空格和點
    filename = filename.strip('. ')
    # 限制長度
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

def create_markdown(poi_name, coords, city_name, pref_name):
    """為 POI 創建 Markdown 內容"""
    timestamp = datetime.now().isoformat() + 'Z'
    slug = poi_name.lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    frontmatter = f"""---
title: {poi_name}
slug: {slug}
location: {city_name}
country: 日本
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
**國家：** 日本
**座標：** {coords[0]}, {coords[1]}

## 描述

待補充
"""

    return frontmatter

print("=" * 80)
print("🔍 日本景點 1:1 清點驗證")
print("=" * 80)

# 掃描 KML
print("\n📄 掃描 KML 檔案...")
kml_pois = extract_kml_japan_pois()
print(f"   發現 {len(kml_pois)} 個日本 POI")

# 掃描 Wiki
print(f"\n📂 掃描 Wiki 日本目錄...")
wiki_files = get_wiki_japan_files()
total_wiki_files = sum(len(cities) for cities in wiki_files.values())
print(f"   發現 {len(wiki_files)} 個都道府縣")
print(f"   發現 {total_wiki_files} 個 Wiki 檔案")

# 逐個都道府縣進行清點
print(f"\n{'='*80}")
print(f"🔄 逐個都道府縣清點")
print(f"{'='*80}\n")

total_matched = 0
total_missing = 0
total_extra = 0
missing_list = []
extra_list = []

for pref_name in sorted(JAPAN_TOWNS_COORDS.keys()):
    pref_path = os.path.join(WIKI_BASE, "日本", pref_name)

    print(f"\n{pref_name}")
    print("-" * 60)

    cities_in_pref = JAPAN_TOWNS_COORDS[pref_name]
    pref_matched = 0
    pref_missing = 0
    pref_extra = 0

    for city_name in sorted(cities_in_pref.keys()):
        city_coords = cities_in_pref[city_name]

        # 從 KML 找該市町村的景點
        kml_city_pois = []
        for poi in kml_pois:
            # 根據座標判斷是否在該市町村
            found_pref, found_city = None, None
            for p in JAPAN_TOWNS_COORDS.keys():
                t = get_nearest_town((poi['lng'], poi['lat']), p)
                if t:
                    found_pref = p
                    found_city = t
                    break

            if found_pref == pref_name and found_city == city_name:
                kml_city_pois.append(poi)

        # 從 Wiki 獲取該市町村的檔案
        wiki_city_files = wiki_files.get(pref_name, {}).get(city_name, [])

        if not kml_city_pois and not wiki_city_files:
            continue

        # 進行 1:1 比對
        matched = 0
        missing = 0
        extra = 0

        # 檢查 Wiki 檔案
        wiki_names = set([f['name'] for f in wiki_city_files])
        kml_names = set([p['name'] for p in kml_city_pois])

        # ✓ 完全匹配
        for wiki_file in wiki_city_files:
            if find_poi_in_kml(wiki_file['name'], wiki_file['coords'], kml_city_pois):
                matched += 1
            else:
                # ✗ 多餘（Wiki 有但 KML 沒有）
                extra += 1
                extra_list.append({
                    'pref': pref_name,
                    'city': city_name,
                    'file': wiki_file['file'],
                    'path': wiki_file['path']
                })

        # ✗ 缺失（KML 有但 Wiki 沒有）
        for kml_poi in kml_city_pois:
            if kml_poi['name'] not in wiki_names:
                missing += 1
                missing_list.append({
                    'pref': pref_name,
                    'city': city_name,
                    'name': kml_poi['name'],
                    'desc': kml_poi['desc'],
                    'lng': kml_poi['lng'],
                    'lat': kml_poi['lat']
                })

        if kml_city_pois or wiki_city_files:
            status = ""
            if extra > 0:
                status += f" ⚠ 多餘:{extra}"
            if missing > 0:
                status += f" ⚠ 缺失:{missing}"
            if missing == 0 and extra == 0:
                status = " ✓"

            print(f"  {city_name:<20} KML:{len(kml_city_pois):3d} Wiki:{len(wiki_city_files):3d} 匹配:{matched:3d}{status}")

        pref_matched += matched
        pref_missing += missing
        pref_extra += extra

    if pref_missing > 0 or pref_extra > 0 or pref_matched > 0:
        print(f"\n  小計: 匹配={pref_matched:3d} 缺失={pref_missing:3d} 多餘={pref_extra:3d}")

    total_matched += pref_matched
    total_missing += pref_missing
    total_extra += pref_extra

print(f"\n{'='*80}")
print(f"📊 清點結果")
print(f"{'='*80}\n")

print(f"✓ 完全匹配: {total_matched:5d} 個")
print(f"✗ 缺失: {total_missing:5d} 個 (需建立)")
print(f"✗ 多餘: {total_extra:5d} 個 (需刪除)")
print(f"─────────────────────")
print(f"  KML 景點: {len(kml_pois):5d} 個")
print(f"  Wiki 檔案: {total_wiki_files:5d} 個")

# 處理缺失的景點
if missing_list:
    print(f"\n{'='*80}")
    print(f"➕ 建立缺失的景點檔案")
    print(f"{'='*80}\n")

    created = 0
    for item in missing_list:
        pref = item['pref']
        city = item['city']
        poi_name = item['name']
        coords = (item['lng'], item['lat'])

        # 建立目錄
        city_path = os.path.join(WIKI_BASE, "日本", pref, city)
        os.makedirs(city_path, exist_ok=True)

        # 建立檔案（清理檔名）
        clean_name = sanitize_filename(poi_name)
        filename = f"{clean_name}.md"
        filepath = os.path.join(city_path, filename)

        try:
            if not os.path.exists(filepath):
                content = create_markdown(poi_name, coords, city, pref)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                created += 1
                if created % 50 == 0 or created == 1:
                    print(f"[{created:4d}] ✓ {pref}/{city}/{clean_name[:40]:40}")
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
        pref = item['pref']
        city = item['city']
        filename = item['file']
        filepath = item['path']

        try:
            os.remove(filepath)
            deleted += 1
            if deleted % 50 == 0 or deleted == 1:
                print(f"[{deleted:4d}] ✗ 刪除 {pref}/{city}/{filename[:40]:40}")
        except Exception as e:
            print(f"   ✗ 刪除失敗: {filename}: {str(e)}")

    print(f"\n   刪除完成: {deleted} 個檔案")

# 清理空目錄
print(f"\n🗑️  清理空目錄...")
japan_path = os.path.join(WIKI_BASE, "日本")
removed_dirs = 0

for pref_name in os.listdir(japan_path):
    pref_path = os.path.join(japan_path, pref_name)
    if not os.path.isdir(pref_path):
        continue

    for city_name in os.listdir(pref_path):
        city_path = os.path.join(pref_path, city_name)
        if os.path.isdir(city_path):
            if not os.listdir(city_path):  # 空目錄
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
print(f"✅ 日本清點完成！")
print(f"{'='*80}")
