#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整提取第二梯隊國家景點
越南、荷蘭、西班牙、奧地利、紐西蘭、新加坡、加拿大、匈牙利、秘魯、捷克、柬埔寨、智利、比利時、盧森堡、波多黎各、印尼
建立 Wiki 二級結構
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

# 第二梯隊國家定義
COUNTRIES = {
    '越南': {
        'coords': {'lng': (102, 110), 'lat': (8, 24)},
        'divisions': {
            'Hanoi': (105.8542, 21.0285),
            'Ho Chi Minh City': (106.6663, 10.7769),
            'Da Nang': (107.5711, 16.0544),
            'Hai Phong': (106.6837, 20.8449),
            'Can Tho': (105.7668, 10.0379),
            'Quang Ninh': (107.2892, 21.0333),
            'Thai Binh': (106.3353, 20.4455),
            'Nam Dinh': (106.1833, 20.4167),
            'Thanh Hoa': (105.7719, 19.8074),
            'Nghe An': (104.9972, 18.6797),
            'Ha Tinh': (105.9042, 18.3357),
            'Quang Binh': (106.5964, 17.4765),
            'Quang Tri': (106.9542, 16.7539),
            'Thua Thien-Hue': (107.5909, 16.4674),
            'Quang Nam': (107.6931, 15.5794),
            'Quang Ngai': (108.7797, 15.1203),
            'Binh Dinh': (108.9932, 13.7832),
            'Phu Yen': (109.0967, 13.0956),
            'Khanh Hoa': (109.1967, 12.2381),
            'Ninh Thuan': (108.9956, 11.5648),
            'Binh Thuan': (108.1011, 11.1913),
            'Dong Nai': (107.0797, 10.9610),
            'Tay Ninh': (106.0973, 11.3100),
            'Long An': (106.2500, 10.5500),
            'Tien Giang': (106.3667, 10.2667),
            'Ben Tre': (106.3758, 9.2426),
            'Vinh Long': (105.9667, 10.2500),
            'Tra Vinh': (106.3444, 9.9181),
            'Soc Trang': (105.9667, 9.6000),
            'Bac Lieu': (105.7289, 9.2795),
            'Ca Mau': (104.7500, 8.7667),
            'Lao Cai': (104.8519, 22.3402),
            'Yen Bai': (104.9083, 21.7249),
            'Dien Bien': (103.9833, 21.3833),
            'Son La': (104.3667, 21.3333),
            'Hoa Binh': (105.3333, 20.8167),
            'Phu Tho': (105.4000, 21.5667),
            'Bac Kan': (105.8452, 22.1415),
            'Cao Bang': (106.2536, 22.6667),
            'Lang Son': (106.7619, 21.8559),
            'Ha Giang': (104.9833, 22.8000),
            'Tuyen Quang': (105.2167, 21.8667),
        }
    },
    '荷蘭': {
        'coords': {'lng': (3, 8), 'lat': (50, 54)},
        'divisions': {
            'North Holland': (5.2913, 52.5170),
            'South Holland': (4.2768, 52.0705),
            'Utrecht': (5.1214, 52.0907),
            'Gelderland': (5.8520, 51.9851),
            'Overijssel': (6.1600, 52.5000),
            'Drenthe': (6.8000, 53.1600),
            'Groningen': (6.5667, 53.2167),
            'Friesland': (5.7333, 53.1333),
            'Flevoland': (5.5500, 52.5000),
            'North Brabant': (5.4762, 51.4447),
            'Limburg': (5.8708, 50.8353),
        }
    },
    '西班牙': {
        'coords': {'lng': (-10, 5), 'lat': (36, 43)},
        'divisions': {
            'Madrid': (-3.7038, 40.4168),
            'Catalonia': (2.1734, 41.5868),
            'Basque Country': (-2.6271, 43.2627),
            'Andalusia': (-3.6053, 37.3891),
            'Valencian Community': (-0.3763, 39.4699),
            'Galicia': (-8.3881, 42.6026),
            'Castile and Leon': (-4.7023, 41.6488),
            'Aragon': (-1.1743, 41.6149),
            'Murcia': (-1.1303, 38.0046),
            'Extremadura': (-6.3734, 39.0000),
            'Asturias': (-5.5289, 43.3347),
            'Cantabria': (-3.8083, 43.1828),
            'Castilla La Mancha': (-2.6846, 39.3434),
            'Balearic Islands': (3.0588, 39.5699),
            'Canary Islands': (-15.6104, 28.2915),
        }
    },
    '奧地利': {
        'coords': {'lng': (9, 17), 'lat': (47, 49)},
        'divisions': {
            'Vienna': (16.3738, 48.2082),
            'Lower Austria': (15.3000, 48.3333),
            'Upper Austria': (13.8000, 48.3000),
            'Salzburg': (13.0550, 47.8095),
            'Tyrol': (11.4041, 47.2654),
            'Vorarlberg': (10.0000, 47.4000),
            'Styria': (14.5500, 47.1667),
            'Carinthia': (14.3667, 46.6667),
            'Burgenland': (16.2833, 47.5500),
        }
    },
    '紐西蘭': {
        'coords': {'lng': (166, 179), 'lat': (-47, -34)},
        'divisions': {
            'Auckland': (174.8860, -37.0082),
            'Wellington': (174.7762, -41.2865),
            'Christchurch': (172.6362, -43.5321),
            'Hamilton': (175.2793, -37.7870),
            'Tauranga': (176.1667, -37.6833),
            'Rotorua': (176.2500, -38.1333),
            'Palmerston North': (175.6128, -40.3567),
            'Nelson': (173.2836, -41.2865),
            'Dunedin': (170.5028, -45.8788),
            'Invercargill': (168.3469, -46.4167),
            'Greymouth': (171.2011, -42.4500),
            'Blenheim': (173.9467, -41.5167),
            'Napier': (176.9217, -39.4833),
        }
    },
    '新加坡': {
        'coords': {'lng': (103, 104), 'lat': (1, 2)},
        'divisions': {
            'Central': (103.8500, 1.3500),
            'East': (103.9500, 1.3200),
            'North': (103.8200, 1.4200),
            'Northeast': (103.9000, 1.4500),
            'West': (103.7500, 1.3500),
        }
    },
    '加拿大': {
        'coords': {'lng': (-141, -52), 'lat': (42, 85)},
        'divisions': {
            'Ontario': (-85.0000, 51.3333),
            'Quebec': (-73.5673, 46.8139),
            'British Columbia': (-122.3045, 53.7267),
            'Alberta': (-114.0708, 53.5461),
            'Saskatchewan': (-106.3468, 56.1304),
            'Manitoba': (-98.8139, 56.1500),
            'Nova Scotia': (-62.4097, 45.3435),
            'New Brunswick': (-65.4673, 46.5653),
            'Prince Edward Island': (-63.0896, 46.2382),
            'Newfoundland and Labrador': (-52.7126, 53.1355),
            'Yukon': (-135.0000, 62.6667),
            'Northwest Territories': (-117.0000, 62.4540),
            'Nunavut': (-95.0000, 70.0000),
        }
    },
    '匈牙利': {
        'coords': {'lng': (16, 23), 'lat': (46, 49)},
        'divisions': {
            'Budapest': (19.0402, 47.4979),
            'Baranya': (18.2333, 46.0833),
            'Bács-Kiskun': (19.3500, 46.3333),
            'Békés': (20.8667, 46.7333),
            'Csongrád': (20.1500, 46.4000),
            'Fejér': (18.4333, 47.1833),
            'Győr-Moson-Sopron': (17.6500, 47.6833),
            'Hajdú-Bihar': (21.6000, 47.5333),
            'Heves': (19.8333, 47.5833),
            'Jász-Nagykun-Szolnok': (20.2500, 47.1500),
            'Komárom-Esztergom': (18.5833, 47.5667),
            'Nógrád': (19.6667, 48.0000),
            'Pest': (19.1111, 47.5000),
            'Somogy': (17.8000, 46.3333),
            'Szabolcs-Szatmár-Bereg': (22.0833, 47.9333),
            'Tolna': (18.9167, 46.4000),
            'Vas': (16.9167, 47.2167),
            'Veszprém': (17.8667, 47.1000),
            'Zala': (16.8333, 46.6667),
        }
    },
    '秘魯': {
        'coords': {'lng': (-81, -68), 'lat': (-18, 0)},
        'divisions': {
            'Lima': (-77.0349, -12.0464),
            'Arequipa': (-71.5393, -16.3889),
            'Cusco': (-71.9789, -13.5319),
            'Trujillo': (-79.0259, -8.1270),
            'Ica': (-75.7393, -14.0708),
            'Piura': (-80.6328, -5.1951),
            'Cajamarca': (-78.5044, -7.1547),
            'Puno': (-70.1270, -15.8402),
            'Ayacucho': (-74.2090, -13.1592),
            'Huancayo': (-75.2140, -12.0656),
            'Tacna': (-70.2538, -18.0150),
            'Junín': (-75.7333, -12.0667),
            'Ucayali': (-74.5737, -8.3829),
        }
    },
    '捷克': {
        'coords': {'lng': (12, 19), 'lat': (48, 51)},
        'divisions': {
            'Prague': (14.4378, 50.0755),
            'Central Bohemia': (14.5833, 49.8000),
            'South Bohemia': (14.4500, 48.9500),
            'Plzen Region': (13.3833, 49.7333),
            'Karlovy Vary': (12.8667, 50.2333),
            'Usti nad Labem': (14.0333, 50.6500),
            'Liberec': (15.0667, 50.7667),
            'Hradec Králové': (15.8333, 50.2167),
            'Pardubice': (15.7667, 50.0167),
            'Ústí nad Orlicí': (16.3167, 49.6167),
            'South Moravia': (16.6000, 49.3000),
            'Olomouc': (17.2500, 49.5833),
            'Zlín': (17.6667, 49.2167),
            'Moravia-Silesia': (18.2833, 49.8500),
        }
    },
    '柬埔寨': {
        'coords': {'lng': (102, 107), 'lat': (10, 15)},
        'divisions': {
            'Phnom Penh': (104.9282, 11.5564),
            'Siem Reap': (104.7469, 13.3671),
            'Battambang': (103.2019, 13.0954),
            'Sihanoukville': (104.1636, 10.6280),
            'Kampong Som': (104.1750, 10.6200),
            'Kratie': (105.9833, 12.4833),
            'Stung Treng': (105.9833, 13.5333),
            'Mondulkiri': (106.8333, 12.2667),
            'Ratanakiri': (106.7333, 13.7667),
        }
    },
    '智利': {
        'coords': {'lng': (-77, -66), 'lat': (-56, -17)},
        'divisions': {
            'Santiago': (-70.6693, -33.4489),
            'Valparaíso': (-71.5500, -33.0458),
            'Concepción': (-72.1529, -36.8201),
            'Temuco': (-72.5898, -38.7381),
            'Puerto Montt': (-72.4861, -41.3212),
            'Punta Arenas': (-70.1667, -53.1667),
            'La Serena': (-71.5507, -29.9069),
            'Antofagasta': (-70.4069, -23.6585),
            'Iquique': (-70.1333, -20.2167),
            'Arica': (-70.3119, -18.4861),
            'Los Angeles': (-72.3575, -37.4667),
            'Valdivia': (-73.2353, -39.8141),
            'Osorno': (-72.5325, -40.5833),
        }
    },
    '比利時': {
        'coords': {'lng': (2, 6), 'lat': (49, 51)},
        'divisions': {
            'Brussels': (4.3517, 50.8503),
            'Antwerp': (4.4167, 51.2167),
            'Limburg': (5.6000, 50.9667),
            'Liege': (5.5667, 50.6333),
            'Hainaut': (3.9667, 50.4000),
            'Namur': (4.8667, 50.4667),
            'Walloon Brabant': (4.6000, 50.6333),
            'East Flanders': (3.8000, 51.0333),
            'West Flanders': (2.8333, 51.0000),
            'Flemish Brabant': (4.4167, 50.8667),
        }
    },
    '盧森堡': {
        'coords': {'lng': (5, 7), 'lat': (49, 51)},
        'divisions': {
            'Luxembourg City': (6.1296, 49.6116),
            'Esch-sur-Alzette': (5.9787, 49.4892),
            'Differdange': (5.8833, 49.5333),
        }
    },
    '波多黎各': {
        'coords': {'lng': (-66, -65), 'lat': (17, 19)},
        'divisions': {
            'San Juan': (-66.1057, 18.4655),
            'Ponce': (-66.6136, 17.9808),
            'Mayagüez': (-67.1393, 18.2010),
        }
    },
    '印尼': {
        'coords': {'lng': (95, 141), 'lat': (-11, 6)},
        'divisions': {
            'Jakarta': (106.8456, -6.2088),
            'Bandung': (107.6191, -6.9147),
            'Surabaya': (112.7380, -7.2575),
            'Medan': (98.6722, 3.5952),
            'Palembang': (104.7458, -2.9181),
            'Semarang': (110.4158, -6.9667),
            'Makassar': (119.4026, -5.1477),
            'Yogyakarta': (110.3722, -7.7956),
            'Bali': (115.2125, -8.6705),
            'Lombok': (116.3156, -8.6705),
        }
    },
}

def sanitize_filename(filename):
    """清理檔名中的特殊字符"""
    invalid_chars = r'[/\\:*?"<>|]'
    filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip('. ')
    if len(filename) > 200:
        filename = filename[:197] + '...'
    return filename

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

def create_markdown(poi_name, coords, city_name, division_name, country, desc):
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
country: {country}
division: {division_name}
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
**地區：** {division_name}
**國家：** {country}
**座標：** {coords[0]}, {coords[1]}

## 描述

{desc_text}
"""

    return frontmatter

def get_nearest_division(coords, divisions):
    """根據座標找到最近的行政區"""
    lng, lat = coords
    min_distance = float('inf')
    best_division = None

    for division_name, (div_lng, div_lat) in divisions.items():
        distance = ((lng - div_lng) ** 2 + (lat - div_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_division = division_name

    return best_division

def process_country(country_name, country_config):
    """處理單個國家"""
    print(f"\n{'='*80}")
    print(f"🌍 {country_name}景點完整提取（KML → Wiki 1:1）")
    print(f"{'='*80}")

    # 1. 掃描 KML
    print(f"\n📄 掃描 KML 檔案...")
    kml_pois = extract_kml_pois(country_name, country_config['coords'])
    print(f"   發現 {len(kml_pois)} 個{country_name}POI")

    if len(kml_pois) == 0:
        print(f"   ⚠️  未發現任何 POI，跳過此國家")
        return 0

    # 2. 清空舊 Wiki
    print(f"\n🗑️  清理舊 Wiki 結構...")
    country_path = os.path.join(WIKI_BASE, country_name)
    if os.path.isdir(country_path):
        for division_name in os.listdir(country_path):
            division_path = os.path.join(country_path, division_name)
            if os.path.isdir(division_path):
                for item in os.listdir(division_path):
                    item_path = os.path.join(division_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                    else:
                        try:
                            os.remove(item_path)
                        except:
                            pass
    print("   舊 Wiki 結構已清理")

    # 3. 組織景點
    print(f"\n📊 組織景點數據...")
    organized_pois = defaultdict(lambda: defaultdict(list))
    unlocated = []

    for poi in kml_pois:
        division = get_nearest_division((poi['lng'], poi['lat']), country_config['divisions'])
        if division:
            organized_pois[division]['POI'].append(poi)
        else:
            unlocated.append(poi)

    print(f"   已分類: {sum(len(cities) for cities in organized_pois.values())} 個")
    print(f"   未分類: {len(unlocated)} 個")

    # 4. 建立檔案
    print(f"\n{'='*80}")
    print(f"📝 建立檔案")
    print(f"{'='*80}\n")

    total_created = 0
    for division_idx, division_name in enumerate(sorted(organized_pois.keys()), 1):
        cities = organized_pois[division_name]
        division_created = 0

        print(f"[{division_idx:2d}/{len(organized_pois)}] {division_name}")

        for city_name in sorted(cities.keys()):
            pois = cities[city_name]
            city_path = os.path.join(WIKI_BASE, country_name, division_name, city_name)
            os.makedirs(city_path, exist_ok=True)

            for poi in pois:
                clean_name = sanitize_filename(poi['name'])
                filename = f"{clean_name}.md"
                filepath = os.path.join(city_path, filename)

                try:
                    if not os.path.exists(filepath):
                        content = create_markdown(
                            poi['name'],
                            (poi['lng'], poi['lat']),
                            city_name,
                            division_name,
                            country_name,
                            poi['desc']
                        )
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        total_created += 1
                        division_created += 1
                except:
                    pass

            if division_created > 0:
                print(f"      {city_name}: {division_created:4d} 個")

    print(f"\n{'='*80}")
    print(f"✅ {country_name}景點完整提取完成！")
    print(f"   新建檔案: {total_created} 個")
    print(f"{'='*80}")

    return total_created

# 處理第二梯隊國家
print("🚀 第二梯隊國家完整提取開始")
print("="*80)

total_all = 0
for country_name, country_config in COUNTRIES.items():
    created = process_country(country_name, country_config)
    total_all += created

print(f"\n{'='*80}")
print(f"✅ 第二梯隊國家提取完成！")
print(f"   總計新建檔案: {total_all} 個")
print(f"{'='*80}")
