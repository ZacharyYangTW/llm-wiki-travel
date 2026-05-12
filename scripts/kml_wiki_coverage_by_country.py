#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每個國家的 KML POI 數 vs Wiki 檔案數覆蓋率報告
"""

import os
import sys
import xml.etree.ElementTree as ET
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

# 國家座標範圍定義
COUNTRY_RANGES = {
    '中國': {'lng': (73, 135), 'lat': (18, 54)},
    '台灣': {'lng': (120, 122), 'lat': (21.8, 25.2)},
    '日本': {'lng': (125, 145), 'lat': (24, 46)},
    '韓國': {'lng': (125, 130), 'lat': (33, 44)},
    '泰國': {'lng': (97, 106), 'lat': (6, 21)},
    '美國': {'lng': (-180, -50), 'lat': (20, 50)},
    '越南': {'lng': (102, 110), 'lat': (8, 23)},
    '柬埔寨': {'lng': (102, 108), 'lat': (10, 14)},
    '馬來西亞': {'lng': (99, 120), 'lat': (1, 7)},
    '新加坡': {'lng': (103, 104), 'lat': (1, 2)},
    '印尼': {'lng': (95, 141), 'lat': (-11, 6)},
    '菲律賓': {'lng': (117, 127), 'lat': (5, 21)},
    '印度': {'lng': (68, 97), 'lat': (8, 35)},
    '埃及': {'lng': (24, 35), 'lat': (22, 32)},
    '香港': {'lng': (113.8, 114.4), 'lat': (22.2, 22.6)},
    '澳門': {'lng': (113.5, 113.6), 'lat': (22.1, 22.2)},
    '澳洲': {'lng': (113, 154), 'lat': (-44, -10)},
    '紐西蘭': {'lng': (166, 179), 'lat': (-47, -34)},
    '加拿大': {'lng': (-141, -52), 'lat': (42, 84)},
    '墨西哥': {'lng': (-117, -87), 'lat': (14, 33)},
    '巴西': {'lng': (-74, -35), 'lat': (-33, 5)},
    '秘魯': {'lng': (-81, -67), 'lat': (-18, 0)},
    '智利': {'lng': (-77, -67), 'lat': (-56, -17)},
    '阿根廷': {'lng': (-73, -54), 'lat': (-56, -22)},
    '英國': {'lng': (-8, 2), 'lat': (50, 59)},
    '法國': {'lng': (-5, 8), 'lat': (42, 51)},
    '德國': {'lng': (6, 15), 'lat': (47, 56)},
    '荷蘭': {'lng': (3, 7), 'lat': (50, 54)},
    '比利時': {'lng': (2, 6), 'lat': (49, 51)},
    '盧森堡': {'lng': (5, 7), 'lat': (49, 50)},
    '瑞士': {'lng': (6, 9), 'lat': (45, 48)},
    '義大利': {'lng': (6, 19), 'lat': (37, 47)},
    '西班牙': {'lng': (-9, 4), 'lat': (36, 43)},
    '葡萄牙': {'lng': (-9, -6), 'lat': (37, 42)},
    '奧地利': {'lng': (10, 17), 'lat': (47, 49)},
    '捷克': {'lng': (12, 19), 'lat': (48, 51)},
    '匈牙利': {'lng': (16, 23), 'lat': (46, 48)},
    '波蘭': {'lng': (14, 24), 'lat': (49, 54)},
    '烏克蘭': {'lng': (22, 41), 'lat': (44, 52)},
    '波多黎各': {'lng': (-67, -66), 'lat': (18, 19)},
}

def classify_poi_by_country(lng, lat):
    """根據座標分類 POI 到國家"""
    for country, ranges in COUNTRY_RANGES.items():
        lng_min, lng_max = ranges['lng']
        lat_min, lat_max = ranges['lat']

        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
            return country

    return None

def count_kml_by_country():
    """按國家統計 KML 中的 POI"""
    pois_by_country = defaultdict(int)
    unlocated = 0

    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        for placemark in root.findall('.//kml:Placemark', ns):
            coords_elem = placemark.find('.//kml:coordinates', ns)

            if coords_elem is not None:
                coords_text = coords_elem.text.strip()
                if coords_text:
                    try:
                        parts = coords_text.split(',')
                        lng, lat = float(parts[0]), float(parts[1])

                        country = classify_poi_by_country(lng, lat)
                        if country:
                            pois_by_country[country] += 1
                        else:
                            unlocated += 1
                    except:
                        unlocated += 1
    except Exception as e:
        print(f"KML 解析錯誤: {str(e)}", file=sys.stderr)

    return pois_by_country, unlocated

def count_wiki_by_country():
    """按國家統計 Wiki 中的檔案"""
    files_by_country = defaultdict(int)

    if not os.path.isdir(WIKI_BASE):
        return files_by_country

    for country_name in os.listdir(WIKI_BASE):
        country_path = os.path.join(WIKI_BASE, country_name)
        if not os.path.isdir(country_path):
            continue

        country_files = 0
        for root_dir, dirs, files in os.walk(country_path):
            for file in files:
                if file.endswith('.md'):
                    country_files += 1

        if country_files > 0:
            files_by_country[country_name] = country_files

    return files_by_country

print("=" * 100)
print("📊 每個國家的 KML vs Wiki 覆蓋率報告")
print("=" * 100)

# 統計 KML
print("\n📄 掃描 KML 檔案...")
kml_by_country, unlocated = count_kml_by_country()
kml_total = sum(kml_by_country.values())
print(f"   KML 總 POI 數: {kml_total} 個")
print(f"   未定位 POI: {unlocated} 個")

# 統計 Wiki
print(f"\n📂 掃描 Wiki 檔案...")
wiki_by_country = count_wiki_by_country()
wiki_total = sum(wiki_by_country.values())
print(f"   Wiki 總檔案數: {wiki_total} 個")

# 計算覆蓋率並排序
coverage_data = []
all_countries = set(kml_by_country.keys()) | set(wiki_by_country.keys())

for country in all_countries:
    kml_count = kml_by_country.get(country, 0)
    wiki_count = wiki_by_country.get(country, 0)

    if kml_count > 0:
        coverage = (wiki_count / kml_count) * 100
    else:
        coverage = 100.0 if wiki_count > 0 else 0.0

    coverage_data.append({
        'country': country,
        'kml': kml_count,
        'wiki': wiki_count,
        'coverage': coverage,
        'diff': wiki_count - kml_count
    })

# 按覆蓋率從高到低排序
coverage_data.sort(key=lambda x: x['coverage'], reverse=True)

# 輸出表格
print(f"\n{'='*100}")
print(f"📈 國家/地區覆蓋率詳表")
print(f"{'='*100}\n")

print(f"{'國家/地區':<15} {'KML POI':<10} {'Wiki檔案':<10} {'覆蓋率':<10} {'差異':<10} {'狀態':<10}")
print("-" * 100)

verified = 0
partial = 0
unverified = 0

for data in coverage_data:
    country = data['country']
    kml = data['kml']
    wiki = data['wiki']
    coverage = data['coverage']
    diff = data['diff']

    # 判斷狀態
    if coverage >= 95:
        status = "✅ 完整"
        verified += 1
    elif coverage >= 50:
        status = "⚠️  部分"
        partial += 1
    else:
        status = "❌ 不足"
        unverified += 1

    coverage_str = f"{coverage:.1f}%"
    diff_str = f"{diff:+d}" if diff != 0 else "0"

    print(f"{country:<15} {kml:>8} 個  {wiki:>8} 個  {coverage_str:>8}  {diff_str:>8}  {status:<10}")

print("-" * 100)
print(f"{'合計':<15} {kml_total:>8} 個  {wiki_total:>8} 個  {(wiki_total/kml_total*100 if kml_total>0 else 0):>7.1f}%")

# 統計摘要
print(f"\n{'='*100}")
print(f"📊 驗證狀態統計")
print(f"{'='*100}\n")

print(f"✅ 完整覆蓋 (≥95%):   {verified:3d} 個國家")
print(f"⚠️  部分覆蓋 (50~95%): {partial:3d} 個國家")
print(f"❌ 不足覆蓋 (<50%):   {unverified:3d} 個國家")
print(f"📍 未定位 POI:        {unlocated:3d} 個")

# 問題國家
print(f"\n{'='*100}")
print(f"⚠️  需要關注的國家 (覆蓋率 < 80%)")
print(f"{'='*100}\n")

problem_countries = [d for d in coverage_data if d['coverage'] < 80 and d['kml'] > 0]
if problem_countries:
    for data in problem_countries[:10]:
        print(f"  {data['country']:<15} KML:{data['kml']:4d} Wiki:{data['wiki']:4d} 覆蓋率:{data['coverage']:6.1f}%")
    if len(problem_countries) > 10:
        print(f"  ... 還有 {len(problem_countries) - 10} 個國家")
else:
    print("  無需要關注的國家")

print(f"\n{'='*100}")
print(f"✅ 報告完成")
print(f"{'='*100}")
