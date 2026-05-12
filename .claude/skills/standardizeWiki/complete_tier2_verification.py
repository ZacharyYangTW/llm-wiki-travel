#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二梯隊國家景點 1:1 清點驗證
越南、荷蘭、西班牙、奧地利、紐西蘭、新加坡、加拿大、匈牙利、秘魯、捷克、柬埔寨、智利、比利時、盧森堡、印尼
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

# 第二梯隊國家定義（與提取腳本相同）
COUNTRIES = {
    '越南': {'coords': {'lng': (102, 110), 'lat': (8, 24)}},
    '荷蘭': {'coords': {'lng': (3, 8), 'lat': (50, 54)}},
    '西班牙': {'coords': {'lng': (-10, 5), 'lat': (36, 43)}},
    '奧地利': {'coords': {'lng': (9, 17), 'lat': (47, 49)}},
    '紐西蘭': {'coords': {'lng': (166, 179), 'lat': (-47, -34)}},
    '新加坡': {'coords': {'lng': (103, 104), 'lat': (1, 2)}},
    '加拿大': {'coords': {'lng': (-141, -52), 'lat': (42, 85)}},
    '匈牙利': {'coords': {'lng': (16, 23), 'lat': (46, 49)}},
    '秘魯': {'coords': {'lng': (-81, -68), 'lat': (-18, 0)}},
    '捷克': {'coords': {'lng': (12, 19), 'lat': (48, 51)}},
    '柬埔寨': {'coords': {'lng': (102, 107), 'lat': (10, 15)}},
    '智利': {'coords': {'lng': (-77, -66), 'lat': (-56, -17)}},
    '比利時': {'coords': {'lng': (2, 6), 'lat': (49, 51)}},
    '盧森堡': {'coords': {'lng': (5, 7), 'lat': (49, 51)}},
    '印尼': {'coords': {'lng': (95, 141), 'lat': (-11, 6)}},
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

def verify_country(country_name):
    """驗證單個國家"""
    print(f"{'='*80}")
    print(f"🔍 {country_name}景點 1:1 清點驗證")
    print(f"{'='*80}")

    if country_name not in COUNTRIES:
        print(f"   ⚠️  未定義，跳過")
        return 0, 0, 0

    # 掃描 KML
    print(f"\n📄 掃描 KML 檔案...")
    coords = COUNTRIES[country_name]['coords']
    kml_pois = extract_kml_pois(country_name, coords)
    print(f"   發現 {len(kml_pois)} 個{country_name}POI")

    if len(kml_pois) == 0:
        print(f"   ⚠️  未發現任何 POI，跳過驗證")
        return 0, 0, 0

    # 掃描 Wiki
    print(f"\n📂 掃描 Wiki {country_name}目錄...")
    wiki_files = get_wiki_files(country_name)
    total_wiki_files = sum(sum(len(cities) for cities in divisions.values()) for divisions in wiki_files.values())
    print(f"   發現 {len(wiki_files)} 個地區")
    print(f"   發現 {total_wiki_files} 個 Wiki 檔案")

    # 清點結果
    total_matched = 0
    total_missing = 0
    total_extra = 0
    missing_list = []
    extra_list = []

    wiki_names = set()
    for division_files in wiki_files.values():
        for city_files in division_files.values():
            for f in city_files:
                wiki_names.add(f['name'].lower())

    for kml_poi in kml_pois:
        if kml_poi['name'].lower() not in wiki_names:
            total_missing += 1
            missing_list.append({
                'division': 'Unknown',
                'city': 'POI',
                'name': kml_poi['name'],
                'desc': kml_poi['desc'],
                'lng': kml_poi['lng'],
                'lat': kml_poi['lat']
            })

    for division_files in wiki_files.values():
        for city_files in division_files.values():
            for wiki_file in city_files:
                found = False
                for kml_poi in kml_pois:
                    if kml_poi['name'].lower() == wiki_file['name'].lower():
                        found = True
                        total_matched += 1
                        break
                if not found:
                    total_extra += 1
                    extra_list.append(wiki_file['file'])

    print(f"\n✓ 完全匹配: {total_matched} 個")
    print(f"✗ 缺失: {total_missing} 個")
    print(f"✗ 多餘: {total_extra} 個")

    # 處理缺失和多餘
    if missing_list:
        print(f"\n   ⚠️  缺失 {len(missing_list)} 個景點，無法自動建立（無行政區分類）")

    if extra_list:
        deleted = 0
        for div_name, div_data in wiki_files.items():
            for city_name, city_data in div_data.items():
                for f in city_data:
                    if f['file'] in extra_list:
                        try:
                            filepath = os.path.join(WIKI_BASE, country_name, div_name, city_name, f['file'])
                            if os.path.exists(filepath):
                                os.remove(filepath)
                                deleted += 1
                        except:
                            pass

        if deleted > 0:
            print(f"   刪除多餘: {deleted} 個")

    print(f"✅ {country_name}驗證完成！\n")

    return total_matched, total_missing, total_extra

# 驗證所有第二梯隊國家
print("🚀 第二梯隊國家 1:1 驗證開始")
print("="*80)

results = {}
total_matched_all = 0
total_missing_all = 0
total_extra_all = 0

for country_name in sorted(COUNTRIES.keys()):
    matched, missing, extra = verify_country(country_name)
    results[country_name] = {'matched': matched, 'missing': missing, 'extra': extra}
    total_matched_all += matched
    total_missing_all += missing
    total_extra_all += extra

print(f"\n{'='*80}")
print(f"✅ 第二梯隊國家驗證完成！")
print(f"{'='*80}")

# 統計報告
print(f"\n📊 驗證統計：")
print(f"{'國家':<12} {'KML POI':>8} {'Wiki檔案':>8} {'完全匹配':>8} {'缺失':>6} {'多餘':>6}")
print("-" * 50)

for country_name in sorted(results.keys()):
    r = results[country_name]
    if r['matched'] + r['missing'] + r['extra'] == 0:
        continue
    total_kml = r['matched'] + r['missing']
    total_wiki = r['matched'] + r['extra']
    print(f"{country_name:<12} {total_kml:>8} {total_wiki:>8} {r['matched']:>8} {r['missing']:>6} {r['extra']:>6}")

print("-" * 50)
total_kml_all = total_matched_all + total_missing_all
total_wiki_all = total_matched_all + total_extra_all
print(f"{'合計':<12} {total_kml_all:>8} {total_wiki_all:>8} {total_matched_all:>8} {total_missing_all:>6} {total_extra_all:>6}")
print(f"\n匹配率: {(total_matched_all / max(total_kml_all, 1) * 100):.1f}%")
print(f"{'='*80}")
