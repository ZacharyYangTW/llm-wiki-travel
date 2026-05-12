#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二梯隊缺失景點詳細報告
列出所有 KML 中存在但 Wiki 中缺失的景點
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
import io
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

def generate_report():
    """生成缺失景點報告"""
    print("=" * 100)
    print("📊 第二梯隊缺失景點詳細報告")
    print("=" * 100)

    all_missing = []
    country_missing_count = {}

    for country_name in sorted(COUNTRIES.keys()):
        print(f"\n{'='*100}")
        print(f"🔍 {country_name}")
        print(f"{'='*100}")

        # 掃描 KML
        coords = COUNTRIES[country_name]['coords']
        kml_pois = extract_kml_pois(country_name, coords)

        if len(kml_pois) == 0:
            print(f"   未發現 KML POI，跳過")
            continue

        # 掃描 Wiki
        wiki_files = get_wiki_files(country_name)

        # 建立 Wiki 名稱集合（小寫）
        wiki_names = set()
        for division_files in wiki_files.values():
            for city_files in division_files.values():
                for f in city_files:
                    wiki_names.add(f['name'].lower())

        # 找出缺失的景點
        missing = []
        for kml_poi in kml_pois:
            if kml_poi['name'].lower() not in wiki_names:
                missing.append(kml_poi)
                all_missing.append({
                    'country': country_name,
                    'name': kml_poi['name'],
                    'desc': kml_poi['desc'],
                    'lng': kml_poi['lng'],
                    'lat': kml_poi['lat']
                })

        country_missing_count[country_name] = len(missing)

        if len(missing) == 0:
            print(f"   ✅ 無缺失景點")
        else:
            print(f"   ⚠️  缺失 {len(missing)} 個景點：\n")
            print(f"{'序號':<5} {'景點名稱':<40} {'座標 (Lng, Lat)':<30} {'備註':<25}")
            print("-" * 100)
            for idx, poi in enumerate(missing, 1):
                coord_str = f"({poi['lng']:.4f}, {poi['lat']:.4f})"
                desc_short = (poi['desc'][:20] + "...") if len(poi['desc']) > 20 else poi['desc']
                print(f"{idx:<5} {poi['name']:<40} {coord_str:<30} {desc_short:<25}")

    # 生成總結報告
    print(f"\n\n{'='*100}")
    print(f"📈 缺失景點統計")
    print(f"{'='*100}\n")

    print(f"{'國家':<15} {'缺失數量':>10}")
    print("-" * 25)
    total_missing = 0
    for country_name in sorted(country_missing_count.keys()):
        count = country_missing_count[country_name]
        if count > 0:
            print(f"{country_name:<15} {count:>10}")
            total_missing += count

    print("-" * 25)
    print(f"{'合計':<15} {total_missing:>10}")

    # 輸出詳細列表為 CSV 格式便於檢查
    print(f"\n\n{'='*100}")
    print("📄 詳細列表（CSV 格式）")
    print(f"{'='*100}\n")

    print("國家,景點名稱,座標(Lng),座標(Lat),備註")
    for item in all_missing:
        desc_clean = item['desc'].replace(',', '；').replace('\n', ' ')
        print(f"{item['country']},{item['name']},{item['lng']:.6f},{item['lat']:.6f},\"{desc_clean}\"")

    return all_missing

if __name__ == '__main__':
    missing_list = generate_report()
    print(f"\n\n✅ 報告生成完成，共找到 {len(missing_list)} 個缺失景點")
