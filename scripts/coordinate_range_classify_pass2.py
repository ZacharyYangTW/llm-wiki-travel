#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pass 2: 分析 Pass 1 失敗的檔案，微調邊界
"""

import os
import sys
import csv
import io
import math
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"

# 微調後的邊界定義 (Pass 2)
COUNTRY_RANGES_V2 = {
    '台灣': {'lng': (120, 122), 'lat': (22, 25)},
    '日本': {'lng': (130, 146), 'lat': (30, 46)},  # 擴大範圍包括稚內和根室
    '中國': {'lng': (73, 135), 'lat': (18, 54)},
    '泰國': {'lng': (97, 106), 'lat': (5, 21)},
    '越南': {'lng': (102, 110), 'lat': (8, 24)},
    '柬埔寨': {'lng': (102, 108), 'lat': (10, 15)},
    '馬來西亞': {'lng': (100, 119), 'lat': (1, 7)},
    '新加坡': {'lng': (103.5, 104.5), 'lat': (1, 2)},
    '印尼': {'lng': (95, 141), 'lat': (-11, 6)},
    '菲律賓': {'lng': (117, 127), 'lat': (5, 19)},
    '韓國': {'lng': (124, 132), 'lat': (33, 43)},
    '香港': {'lng': (113.8, 114.4), 'lat': (22.2, 22.6)},
    '澳門': {'lng': (113.5, 113.6), 'lat': (22.1, 22.2)},
    '美國': {'lng': (-125, -66), 'lat': (25, 50)},
    '加拿大': {'lng': (-141, -52), 'lat': (42, 84)},
    '墨西哥': {'lng': (-117, -86), 'lat': (14, 33)},
    '秘魯': {'lng': (-82, -68), 'lat': (-18, 0)},
    '智利': {'lng': (-77, -66), 'lat': (-56, -17)},  # 擴大範圍包括復活節島
    '阿根廷': {'lng': (-76, -53), 'lat': (-56, -21)},
    '巴西': {'lng': (-74, -35), 'lat': (-34, 5)},
    '紐西蘭': {'lng': (166, 179), 'lat': (-47, -34)},
    '澳洲': {'lng': (113, 155), 'lat': (-47, -10)},
    '埃及': {'lng': (25, 36), 'lat': (22, 32)},
    '荷蘭': {'lng': (3, 7), 'lat': (50, 54)},
    '比利時': {'lng': (2, 6), 'lat': (49, 52)},
    '法國': {'lng': (-8, 8), 'lat': (42, 51)},
    '西班牙': {'lng': (-10, 4), 'lat': (36, 44)},
    '義大利': {'lng': (6, 20), 'lat': (37, 47)},
    '奧地利': {'lng': (9, 17), 'lat': (47, 49)},
    '瑞士': {'lng': (5, 11), 'lat': (45, 48)},
    '捷克': {'lng': (12, 19), 'lat': (48, 51)},
    '匈牙利': {'lng': (16, 23), 'lat': (46, 49)},
}

# 日本都道府県（Pass 2 微調）
JAPAN_PREFECTURES_V2 = {
    '北海道': {'lng': (139.5, 146), 'lat': (43.2, 46)},  # 擴大範圍
    '青森縣': {'lng': (139.5, 141.8), 'lat': (40.5, 41.6)},
    '岩手縣': {'lng': (141.1, 141.9), 'lat': (39.2, 40.6)},
    '宮城縣': {'lng': (140.6, 141.7), 'lat': (38.3, 40.6)},
    '秋田縣': {'lng': (139.5, 141.6), 'lat': (39.4, 41.0)},
    '山形縣': {'lng': (139.5, 140.9), 'lat': (38.1, 40.1)},
    '福島縣': {'lng': (140.4, 141.7), 'lat': (37.1, 39.7)},
    '茨城縣': {'lng': (139.8, 141.0), 'lat': (35.9, 36.8)},
    '栃木縣': {'lng': (139.4, 140.8), 'lat': (36.4, 37.2)},
    '群馬縣': {'lng': (138.2, 139.7), 'lat': (36.2, 37.3)},
    '埼玉縣': {'lng': (138.5, 140.5), 'lat': (35.9, 36.6)},
    '千葉縣': {'lng': (139.8, 141.1), 'lat': (35.1, 35.8)},
    '東京都': {'lng': (139.1, 140.9), 'lat': (35.1, 35.9)},
    '神奈川縣': {'lng': (139.0, 140.8), 'lat': (35.1, 35.6)},
    '新潟縣': {'lng': (138.2, 140.9), 'lat': (36.9, 38.3)},
    '富山縣': {'lng': (137.1, 138.6), 'lat': (36.5, 37.1)},
    '石川縣': {'lng': (136.6, 137.9), 'lat': (36.2, 37.5)},
    '福井縣': {'lng': (136.0, 136.9), 'lat': (35.5, 36.5)},
    '山梨縣': {'lng': (138.2, 139.2), 'lat': (35.3, 35.9)},
    '長野縣': {'lng': (137.2, 138.6), 'lat': (36.3, 37.4)},
    '岐阜縣': {'lng': (136.3, 138.2), 'lat': (35.2, 36.5)},
    '靜岡縣': {'lng': (137.8, 138.9), 'lat': (34.7, 35.4)},
    '愛知縣': {'lng': (136.5, 137.9), 'lat': (34.8, 35.3)},
    '三重縣': {'lng': (136.2, 137.7), 'lat': (34.1, 34.8)},
    '滋賀縣': {'lng': (135.8, 136.9), 'lat': (34.8, 35.4)},
    '京都府': {'lng': (135.4, 136.9), 'lat': (34.7, 35.6)},
    '大阪府': {'lng': (135.1, 136.0), 'lat': (34.3, 34.9)},
    '兵庫縣': {'lng': (134.8, 135.9), 'lat': (34.1, 35.2)},
    '奈良縣': {'lng': (135.6, 136.4), 'lat': (34.2, 34.8)},
    '和歌山縣': {'lng': (135.4, 136.3), 'lat': (33.5, 34.4)},
    '鳥取縣': {'lng': (133.7, 134.9), 'lat': (35.3, 35.6)},
    '島根縣': {'lng': (131.9, 133.1), 'lat': (34.8, 35.6)},
    '岡山縣': {'lng': (133.7, 134.7), 'lat': (34.4, 35.1)},
    '廣島縣': {'lng': (132.1, 133.0), 'lat': (34.1, 34.8)},
    '山口縣': {'lng': (130.9, 132.1), 'lat': (33.9, 34.6)},
    '德島縣': {'lng': (134.4, 135.0), 'lat': (33.8, 34.5)},
    '香川縣': {'lng': (133.9, 134.7), 'lat': (34.2, 34.6)},
    '愛媛縣': {'lng': (132.5, 133.9), 'lat': (33.0, 34.2)},
    '高知縣': {'lng': (133.6, 134.5), 'lat': (32.7, 33.7)},
    '福岡縣': {'lng': (130.2, 131.2), 'lat': (33.3, 34.0)},
    '佐賀縣': {'lng': (129.7, 130.6), 'lat': (33.1, 33.6)},
    '長崎縣': {'lng': (128.6, 130.6), 'lat': (32.6, 33.4)},
    '熊本縣': {'lng': (130.1, 131.2), 'lat': (32.3, 33.1)},
    '大分縣': {'lng': (131.1, 132.3), 'lat': (32.9, 33.6)},
    '宮崎縣': {'lng': (130.4, 131.7), 'lat': (31.6, 32.7)},
    '鹿兒島縣': {'lng': (130.2, 131.4), 'lat': (30.1, 31.8)},
    '沖繩縣': {'lng': (127.3, 128.3), 'lat': (26.0, 26.5)},
}

# 中國省份 (Pass 2)
CHINA_PROVINCES_V2 = {
    '北京': {'lng': (115.7, 117.4), 'lat': (39.7, 40.9)},
    '天津': {'lng': (116.7, 118.0), 'lat': (38.7, 39.9)},
    '河北省': {'lng': (113.4, 119.9), 'lat': (36.8, 42.6)},
    '山西省': {'lng': (110.2, 114.3), 'lat': (34.7, 40.4)},
    '內蒙古': {'lng': (97.1, 126.4), 'lat': (37.2, 53.4)},
    '遼寧省': {'lng': (118.4, 125.7), 'lat': (38.8, 43.3)},
    '吉林省': {'lng': (121.9, 131.3), 'lat': (42.2, 46.9)},
    '黑龍江': {'lng': (121.1, 135.1), 'lat': (43.8, 53.6)},
    '上海': {'lng': (120.8, 122.2), 'lat': (30.7, 31.8)},
    '江蘇省': {'lng': (118.4, 121.9), 'lat': (30.8, 35.1)},
    '浙江省': {'lng': (118.1, 123.1), 'lat': (27.2, 31.1)},
    '安徽省': {'lng': (114.9, 119.7), 'lat': (29.6, 34.8)},
    '福建省': {'lng': (116.0, 120.8), 'lat': (23.5, 28.3)},
    '江西省': {'lng': (114.2, 118.5), 'lat': (24.4, 29.9)},
    '山東省': {'lng': (114.7, 122.4), 'lat': (34.4, 38.3)},
    '河南省': {'lng': (110.2, 116.7), 'lat': (32.1, 36.4)},
    '湖北省': {'lng': (108.1, 116.5), 'lat': (29.0, 33.3)},
    '湖南省': {'lng': (108.7, 114.2), 'lat': (24.8, 30.1)},
    '廣東省': {'lng': (109.7, 117.3), 'lat': (20.1, 25.3)},
    '廣西自治區': {'lng': (104.5, 112.0), 'lat': (20.9, 26.4)},
    '海南省': {'lng': (108.6, 111.6), 'lat': (18.2, 20.4)},
    '重慶': {'lng': (105.2, 110.2), 'lat': (28.2, 32.4)},
    '四川省': {'lng': (97.2, 108.6), 'lat': (26.0, 34.3)},
    '貴州省': {'lng': (103.7, 109.8), 'lat': (24.7, 29.1)},
    '雲南省': {'lng': (97.3, 106.2), 'lat': (21.1, 29.3)},
    '西藏': {'lng': (78.4, 99.1), 'lat': (26.7, 36.5)},
    '陝西省': {'lng': (105.5, 111.9), 'lat': (31.8, 39.4)},
    '甘肅省': {'lng': (92.1, 108.5), 'lat': (32.3, 42.7)},
    '青海省': {'lng': (89.1, 104.5), 'lat': (31.4, 39.2)},
    '寧夏自治區': {'lng': (104.1, 107.7), 'lat': (35.1, 39.1)},
    '新疆': {'lng': (73.5, 96.4), 'lat': (34.3, 48.9)},
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def classify_by_coordinate_v2(lat, lng):
    """Pass 2: 改進的分類"""
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None, None

    # 判斷國家
    country = None
    for c, ranges in COUNTRY_RANGES_V2.items():
        lng_min, lng_max = ranges['lng']
        lat_min, lat_max = ranges['lat']
        if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
            country = c
            break

    if not country:
        return None, None

    # 判斷第二級
    city = None

    if country == '日本':
        min_dist = float('inf')
        for pref_name, data in JAPAN_PREFECTURES_V2.items():
            lng_min, lng_max = data['lng']
            lat_min, lat_max = data['lat']
            if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
                city = pref_name
                break

    elif country == '中國':
        min_dist = float('inf')
        for prov_name, data in CHINA_PROVINCES_V2.items():
            lng_min, lng_max = data['lng']
            lat_min, lat_max = data['lat']
            if lng_min <= lng <= lng_max and lat_min <= lat <= lat_max:
                city = prov_name
                break

    if not city and country in ['日本', '中國']:
        city = country  # 備用：至少有國家

    return country, city

print("=" * 70, flush=True)
print("🗺️  Pass 2: 微調邊界重新分類", flush=True)
print("=" * 70, flush=True)

# 讀取所有檔案
rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

total = len(rows)
print(f"📊 讀取 {total} 個檔案\n", flush=True)

success_count = 0
fail_count = 0
updated_from_pass1 = 0

for i, row in enumerate(rows, 1):
    # 如果 Pass 1 已經分類成功，跳過
    if row['國家'].strip():
        success_count += 1
        continue

    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    # 用改進的方法重新分類
    country, city = classify_by_coordinate_v2(lat, lng)

    if country:
        row['城市'] = city or ''
        row['國家'] = country
        success_count += 1
        updated_from_pass1 += 1
    else:
        fail_count += 1

    if i % 200 == 0 or i == 1:
        print(f"[{i:4d}/{total}] 進度: {i/total*100:5.1f}% | 成功: {success_count} | 失敗: {fail_count}", flush=True)

# 寫回 CSV
print("\n💾 寫入 CSV...", flush=True)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 70, flush=True)
print(f"✅ Pass 2 完成！", flush=True)
print(f"  成功分類（累計）: {success_count} 個 ({success_count*100//total}%)", flush=True)
print(f"  本輪新增分類: {updated_from_pass1} 個", flush=True)
print(f"  無法分類: {fail_count} 個 ({fail_count*100//total}%)", flush=True)
print("=" * 70, flush=True)
