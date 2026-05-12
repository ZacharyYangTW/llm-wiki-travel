#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
找出 Wiki 中存在但 KML 中沒有的日本景點檔案
"""

import os
import sys
import xml.etree.ElementTree as ET
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

def extract_kml_names():
    """從 KML 提取所有 POI 名稱"""
    kml_names = set()
    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()

        # 定義命名空間
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # 遍歷所有 Placemark
        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            if name_elem is not None and name_elem.text:
                kml_names.add(name_elem.text.strip())
    except Exception as e:
        print(f"KML 解析錯誤: {str(e)}", file=sys.stderr)

    return kml_names

def scan_wiki_japan():
    """掃描 Wiki 中的日本檔案"""
    wiki_files = {}
    japan_path = os.path.join(WIKI_BASE, "日本")

    if not os.path.isdir(japan_path):
        return wiki_files

    for pref_name in os.listdir(japan_path):
        pref_path = os.path.join(japan_path, pref_name)
        if not os.path.isdir(pref_path):
            continue

        for city_name in os.listdir(pref_path):
            city_path = os.path.join(pref_path, city_name)
            if not os.path.isdir(city_path):
                continue

            for file_name in os.listdir(city_path):
                if file_name.endswith('.md'):
                    # 提取檔案標題（去掉 .md）
                    title = file_name[:-3]
                    key = (pref_name, city_name, file_name)
                    wiki_files[key] = title

    return wiki_files

print("=" * 80)
print("🔍 找出 Wiki 中存在但 KML 中沒有的檔案")
print("=" * 80)

# 1. 掃描 KML
print("\n📄 掃描 KML...")
kml_names = extract_kml_names()
print(f"   KML 中的 POI 名稱: {len(kml_names)} 個")

# 2. 掃描 Wiki
print(f"\n🗂️  掃描 Wiki/日本...")
wiki_files = scan_wiki_japan()
print(f"   Wiki 中的檔案: {len(wiki_files)} 個")

# 3. 找出差異
print(f"\n🔎 比較...")
wiki_only = []

for (pref, city, filename), title in wiki_files.items():
    if title not in kml_names:
        wiki_only.append({
            'pref': pref,
            'city': city,
            'filename': filename,
            'title': title
        })

print(f"\n   Wiki Only (KML 中沒有): {len(wiki_only)} 個")

# 4. 列出結果
if wiki_only:
    print(f"\n{'='*80}")
    print(f"📌 Wiki Only 檔案列表（需要確認來源）")
    print(f"{'='*80}\n")

    # 按都道府縣分組
    by_pref = {}
    for item in wiki_only:
        pref = item['pref']
        if pref not in by_pref:
            by_pref[pref] = []
        by_pref[pref].append(item)

    for pref in sorted(by_pref.keys()):
        items = by_pref[pref]
        print(f"\n🏯 {pref} - {len(items)} 個檔案")

        # 按市町村分組
        by_city = {}
        for item in items:
            city = item['city']
            if city not in by_city:
                by_city[city] = []
            by_city[city].append(item)

        for city in sorted(by_city.keys()):
            city_items = by_city[city]
            print(f"\n   📍 {city} ({len(city_items)} 個)")
            for item in city_items[:20]:  # 只顯示前 20 個
                print(f"      • {item['title']}")
            if len(city_items) > 20:
                print(f"      ... 還有 {len(city_items) - 20} 個")

print(f"\n{'='*80}")
print(f"✅ 完成")
print(f"  Wiki 獨有: {len(wiki_only)} 個檔案")
print(f"  需要確認: 這些檔案是否應該從其他來源補充")
print(f"{'='*80}")
