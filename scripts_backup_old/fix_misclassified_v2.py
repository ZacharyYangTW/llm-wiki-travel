#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2: 改進版本，用距離計算來區分日本和韓國
並修復已移動到錯誤國家的檔案
"""

import os
import sys
import re
import shutil
import math
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
WIKI_CHINA = os.path.join(WIKI_BASE, "中國")
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 主要國家中心（用於精確判斷）
COUNTRY_CENTERS = {
    '日本': (138.2529, 36.2048),
    '韓國': (127.0995, 37.6011),
    '泰國': (101.1169, 15.8700),
    '越南': (106.3035, 16.1924),
    '柬埔寨': (104.9282, 12.5569),
    '馬來西亞': (109.5000, 4.2105),
    '新加坡': (104.0000, 1.3521),
    '印尼': (118.0000, -2.0000),
    '菲律賓': (121.7740, 12.8797),
    '香港': (114.1095, 22.3193),
    '澳門': (113.5549, 22.1987),
    '台灣': (121.5654, 25.0330),
    '印度': (77.0000, 20.0000),
    '埃及': (30.0000, 26.0000),
}

# 主要城市中心（第二級判斷）
CITY_CENTERS = {
    '日本': {
        '東京': (139.6917, 35.6895),
        '大阪': (135.5023, 34.6937),
        '京都': (135.7681, 35.0116),
        '沖繩': (127.6809, 26.2125),
        '長崎': (129.8707, 32.7513),
        '福岡': (130.4017, 33.5904),
        '札幌': (141.3469, 43.0642),
        '名古屋': (136.8822, 35.1815),
    },
    '韓國': {
        '首爾': (126.9780, 37.5665),
        '釜山': (129.0756, 35.1595),
        '大邱': (128.5626, 35.8714),
        '濟州': (126.5227, 33.5133),
        '仁川': (126.7345, 37.4563),
        '大田': (127.4240, 36.3504),
        '光州': (126.8793, 35.1603),
        '蔚山': (129.3159, 35.5380),
    },
    '泰國': {
        '曼谷': (100.5018, 13.7563),
        '清萊': (100.7932, 20.2749),
        '清邁': (98.9853, 18.7883),
    },
    '越南': {
        '河內': (105.8517, 21.0285),
        '胡志明市': (106.6669, 10.7769),
        '沙壩': (103.8343, 22.3402),
    },
    '印度': {
        '德里': (77.1025, 28.6139),
        '孟買': (72.8479, 19.0760),
        '班加羅爾': (77.5946, 12.9716),
        '加爾各答': (88.3639, 22.5726),
    },
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def extract_coordinates(md_file):
    """提取坐標"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(COORD_PATTERN, content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return lng, lat
    except:
        pass
    return None, None

def classify_by_distance(lat, lng):
    """用距離法判斷國家和城市（優先於範圍法）"""
    # 先找最近的國家
    min_dist = float('inf')
    best_country = None
    for country, (c_lng, c_lat) in COUNTRY_CENTERS.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            best_country = country

    if not best_country:
        return None, None

    # 再找該國家內最近的城市
    city = None
    if best_country in CITY_CENTERS:
        cities = CITY_CENTERS[best_country]
        min_city_dist = float('inf')
        for city_name, (c_lng, c_lat) in cities.items():
            dist = euclidean_distance(lat, lng, c_lat, c_lng)
            if dist < min_city_dist:
                min_city_dist = dist
                city = city_name

    return best_country, city

print("=" * 70, flush=True)
print("🔧 v2: 修復中國目錄裡的誤分類檔案（用距離法）", flush=True)
print("=" * 70, flush=True)

moved_count = 0
fixed_count = 0
stayed_in_china = 0
unclassified = 0
failed_list = []

# 掃描所有省份
for province in sorted(os.listdir(WIKI_CHINA)):
    province_path = os.path.join(WIKI_CHINA, province)

    if not os.path.isdir(province_path):
        continue

    # 列出根目錄的 .md 檔案
    root_files = [f for f in os.listdir(province_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(province_path, f))]

    if not root_files:
        continue

    print(f"\n🔍 檢查 {province} ({len(root_files)} 個根目錄檔案)", flush=True)

    for filename in root_files:
        file_path = os.path.join(province_path, filename)
        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            failed_list.append((title, f"{province}/×", "無坐標"))
            continue

        # 用距離法判斷國家和城市
        country, city = classify_by_distance(lat, lng)

        if not country:
            unclassified += 1
            failed_list.append((title, f"{province}/×", f"[{lng:.2f}, {lat:.2f}]"))
            continue

        # 如果判斷為中國，保留在原地
        if country == '中國':
            stayed_in_china += 1
            continue

        # 否則移動到對應國家/城市
        try:
            if city:
                target_dir = os.path.join(WIKI_BASE, country, city)
            else:
                target_dir = os.path.join(WIKI_BASE, country)

            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, filename)

            # 如果檔案已存在（被誤分類過），覆蓋
            if os.path.exists(target_file):
                os.remove(target_file)

            shutil.move(file_path, target_file)
            moved_count += 1

            if moved_count <= 50 or moved_count % 50 == 0:
                print(f"  ✓ {title[:35]:<35} → {country}/{city or '×'}", flush=True)

        except Exception as e:
            failed_list.append((title, f"{province}/{country}", str(e)[:30]))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動到正確國家: {moved_count} 個", flush=True)
print(f"  保留在中國: {stayed_in_china} 個", flush=True)
print(f"  無法分類: {unclassified} 個", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

if failed_list:
    print(f"\n⚠️  無法判斷或失敗的檔案（前 10 個）：", flush=True)
    for title, location, reason in failed_list[:10]:
        print(f"  - {title[:40]:<40} ({location}) {reason}", flush=True)
    if len(failed_list) > 10:
        print(f"  ... 及其他 {len(failed_list)-10} 個", flush=True)

print(f"{'='*70}", flush=True)
