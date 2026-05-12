#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 轉換所有日本 POI 到 Wiki（按市町村分類）
- 自動判斷坐標對應的都道府縣和市町村
- 重複檔案不覆蓋
"""

import os
import sys
import re
import io
import xml.etree.ElementTree as ET
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

# 導入日本市町村座標表
sys.path.insert(0, r"h:\我的雲端硬碟\llm_wiki_travel\.claude\skills\standardizeWiki")
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

def extract_kml_pois():
    """從 KML 提取所有 POI"""
    pois = []
    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()

        # 定義命名空間
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # 遍歷所有 Placemark
        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            desc_elem = placemark.find('kml:description', ns)
            coords_elem = placemark.find('.//kml:coordinates', ns)

            if name_elem is not None and coords_elem is not None:
                name = (name_elem.text or "").strip()
                desc = (desc_elem.text if desc_elem is not None else "").strip()
                coords_text = coords_elem.text.strip()

                # 解析坐標
                if coords_text and name:
                    try:
                        parts = coords_text.split(',')
                        lng, lat = float(parts[0]), float(parts[1])
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

def is_japan_coords(lng, lat):
    """判斷座標是否在日本"""
    return 130 <= lng <= 145 and 30 <= lat <= 46

def find_pref_city(lng, lat):
    """根據坐標找到對應的都道府縣和市町村"""
    for pref_name in JAPAN_TOWNS_COORDS.keys():
        nearest_town = get_nearest_town((lng, lat), pref_name)
        if nearest_town:
            return pref_name, nearest_town
    return None, None

def create_markdown(poi):
    """為 POI 創建 Markdown 內容"""
    timestamp = datetime.now().isoformat() + 'Z'

    # 生成簡化的 slug
    slug = poi['name'].lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9\-ぁ-ん]', '', slug)

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

# {poi['name']}"""

    content = f"""
## 基本資訊

**位置：** {poi.get('location', '')}
**國家：** 日本
**座標：** {poi['lng']}, {poi['lat']}

## 描述

{poi['desc'] or '待補充'}
"""

    return frontmatter + content

print("=" * 80)
print("📝 轉換所有日本 POI 到 Wiki")
print("=" * 80)

# 1. 提取 KML 中的所有 POI
print("\n🔍 掃描 KML 檔案...")
pois = extract_kml_pois()
print(f"   總計 {len(pois)} 個 POI")

# 2. 篩選日本 POI
print(f"\n🗾 篩選日本 POI...")
japan_pois = [p for p in pois if is_japan_coords(p['lng'], p['lat'])]
print(f"   日本 POI: {len(japan_pois)} 個")

# 3. 分類到市町村
print(f"\n🏘️  分類到市町村...")
by_location = {}
unmatched = []

for poi in japan_pois:
    pref, city = find_pref_city(poi['lng'], poi['lat'])
    if pref and city:
        poi['pref'] = pref
        poi['city'] = city
        poi['location'] = city

        key = (pref, city)
        if key not in by_location:
            by_location[key] = []
        by_location[key].append(poi)
    else:
        unmatched.append(poi)

print(f"   匹配到市町村: {len(by_location)} 個位置")
print(f"   無法匹配: {len(unmatched)} 個")

# 4. 創建檔案
print(f"\n📝 建立檔案...")

created = 0
skipped = 0
errors = []

for (pref, city), location_pois in sorted(by_location.items()):
    city_path = os.path.join(WIKI_BASE, "日本", pref, city)
    os.makedirs(city_path, exist_ok=True)

    print(f"\n  {pref}/{city} ({len(location_pois)} 個)")

    for poi in location_pois:
        try:
            filename = f"{poi['name']}.md"
            filepath = os.path.join(city_path, filename)

            # 檢查檔案是否已存在
            if os.path.exists(filepath):
                skipped += 1
                print(f"    ⊘ {filename}")
                continue

            content = create_markdown(poi)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            created += 1
            print(f"    ✓ {filename}")
        except Exception as e:
            errors.append(f"{poi['name']}: {str(e)}")
            print(f"    ✗ {poi['name']}: {str(e)}")

print(f"\n{'='*80}")
print(f"✅ 完成")
print(f"  建立: {created} 個檔案")
print(f"  跳過: {skipped} 個（已存在）")
if errors:
    print(f"  錯誤: {len(errors)} 個")
    for err in errors[:5]:
        print(f"    - {err}")
if unmatched:
    print(f"  無法匹配: {len(unmatched)} 個")
print(f"{'='*80}")
