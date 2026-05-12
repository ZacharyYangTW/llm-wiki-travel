#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML vs Wiki 總體對比報告
統計 KML 總 POI 數 vs Wiki 總檔案數
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

def count_kml_pois():
    """計算 KML 中的所有 POI"""
    pois = defaultdict(int)
    total = 0

    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            if name_elem is not None and name_elem.text:
                total += 1
                pois['total'] += 1
    except Exception as e:
        print(f"KML 解析錯誤: {str(e)}", file=sys.stderr)

    return total, pois

def count_wiki_files():
    """計算 Wiki 中的所有檔案"""
    files_by_country = defaultdict(int)
    total = 0

    if not os.path.isdir(WIKI_BASE):
        return 0, files_by_country

    for country_name in os.listdir(WIKI_BASE):
        country_path = os.path.join(WIKI_BASE, country_name)
        if not os.path.isdir(country_path):
            continue

        country_files = 0
        for root_dir, dirs, files in os.walk(country_path):
            for file in files:
                if file.endswith('.md'):
                    country_files += 1
                    total += 1

        if country_files > 0:
            files_by_country[country_name] = country_files

    return total, files_by_country

print("=" * 80)
print("📊 KML vs Wiki 總體對比報告")
print("=" * 80)

# 計算 KML
print("\n📄 掃描 KML 檔案...")
kml_total, _ = count_kml_pois()
print(f"   KML 總 POI 數: {kml_total} 個")

# 計算 Wiki
print(f"\n📂 掃描 Wiki 檔案...")
wiki_total, files_by_country = count_wiki_files()
print(f"   Wiki 總檔案數: {wiki_total} 個")
print(f"   國家/地區數: {len(files_by_country)} 個")

# 對比
print(f"\n{'='*80}")
print(f"🔄 KML ↔ Wiki 對比")
print(f"{'='*80}\n")

print(f"KML 總 POI 數:      {kml_total:6d} 個")
print(f"Wiki 總檔案數:      {wiki_total:6d} 個")
print(f"差異:              {abs(kml_total - wiki_total):6d} 個")

if kml_total > wiki_total:
    print(f"\n⚠️  KML 多於 Wiki: {kml_total - wiki_total} 個 POI")
    print(f"   (可能是: 座標重複、邊界 POI、未驗證的國家)")
elif wiki_total > kml_total:
    print(f"\n⚠️  Wiki 多於 KML: {wiki_total - kml_total} 個檔案")
    print(f"   (可能是: 已驗證但 KML 沒有的額外景點)")
else:
    print(f"\n✅ KML 和 Wiki 數量相等")

# 按國家統計
print(f"\n{'='*80}")
print(f"📊 已驗證國家詳細統計 (按 Wiki 檔案數排序)")
print(f"{'='*80}\n")

sorted_countries = sorted(files_by_country.items(), key=lambda x: x[1], reverse=True)

print(f"{'國家/地區':<20} {'Wiki檔案':<12} {'佔比':<8}")
print("-" * 50)

for country, count in sorted_countries:
    percentage = (count / wiki_total * 100) if wiki_total > 0 else 0
    print(f"{country:<20} {count:>8} 個    {percentage:>6.1f}%")

print("-" * 50)
print(f"{'合計':<20} {wiki_total:>8} 個    {'100.0%':>6}")

print(f"\n{'='*80}")
print(f"✅ 統計完成")
print(f"{'='*80}")
