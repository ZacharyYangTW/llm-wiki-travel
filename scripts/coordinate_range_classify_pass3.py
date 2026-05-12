#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pass 3: 最終優化 - 用距離法給失敗檔案找最近的國家/城市
也輸出「有疑慮」的檔案供人工檢查
"""

import os
import sys
import csv
import io
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
DOUBT_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\files_need_manual_check.csv"

# 主要國家/地區中心（用於距離計算）
WORLD_CENTERS = {
    '台灣': (121.5654, 25.0330),
    '日本': (138.2529, 36.2048),
    '中國': (105.0000, 35.0000),
    '泰國': (101.1169, 15.8700),
    '越南': (106.3035, 16.1924),
    '柬埔寨': (104.9282, 12.5569),
    '馬來西亞': (109.5000, 4.2105),
    '新加坡': (104.0000, 1.3521),
    '印尼': (118.0000, -2.0000),
    '菲律賓': (121.7740, 12.8797),
    '韓國': (127.1099, 37.5665),
    '香港': (114.1095, 22.3193),
    '澳門': (113.5549, 22.1987),
    '印度': (78.9629, 20.5937),
    '美國': (-95.7129, 37.0902),
    '加拿大': (-106.3468, 56.1304),
    '墨西哥': (-102.5528, 23.6345),
    '秘魯': (-75.7482, -9.1900),
    '智利': (-71.5430, -35.6751),
    '阿根廷': (-63.6167, -38.4161),
    '巴西': (-51.9253, -14.2350),
    '紐西蘭': (174.8860, -40.9006),
    '澳洲': (133.7751, -25.2744),
    '埃及': (30.8025, 26.8206),
    '荷蘭': (5.2913, 52.1326),
    '比利時': (4.4699, 50.5039),
    '法國': (2.2137, 46.2276),
    '西班牙': (-3.7492, 40.4637),
    '義大利': (12.5674, 41.8719),
    '奧地利': (14.5501, 47.5162),
    '瑞士': (8.2275, 46.8182),
    '捷克': (15.4730, 49.8175),
    '匈牙利': (19.5033, 47.1625),
    '葡萄牙': (-8.2245, 39.3999),
    '英國': (-3.4360, 55.3781),
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

print("=" * 70, flush=True)
print("🗺️  Pass 3: 最終優化 - 距離法", flush=True)
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
doubt_count = 0
updated_from_pass2 = 0
doubt_list = []

for i, row in enumerate(rows, 1):
    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    # 如果 Pass 2 已經分類成功，跳過
    if row['國家'].strip():
        success_count += 1
        continue

    # Pass 3: 用距離法找最近的國家
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except:
        fail_count += 1
        continue

    min_dist = float('inf')
    best_country = None

    for country, (c_lng, c_lat) in WORLD_CENTERS.items():
        dist = euclidean_distance(lat_f, lng_f, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            best_country = country

    if best_country:
        # 計算距離，如果超過 10 度以上，標記為「有疑慮」
        if min_dist > 10:
            doubt_count += 1
            title = row['標題']
            doubt_list.append({
                '標題': title,
                '經度': lng,
                '緯度': lat,
                '推薦國家': best_country,
                '距離': f"{min_dist:.2f}",
                '備註': '距離遠，需人工檢查'
            })
            # 先填上去，但標記為有疑慮
            row['城市'] = best_country
            row['國家'] = best_country + ' (?)'
        else:
            row['城市'] = ''
            row['國家'] = best_country
            updated_from_pass2 += 1
            success_count += 1
    else:
        fail_count += 1

    if i % 200 == 0 or i == 1:
        print(f"[{i:4d}/{total}] 進度: {i/total*100:5.1f}% | 成功: {success_count} | 有疑慮: {doubt_count} | 失敗: {fail_count}", flush=True)

# 寫回主 CSV
print("\n💾 寫入主 CSV...", flush=True)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

# 寫入「有疑慮」的檔案供人工檢查
if doubt_list:
    print(f"💾 寫入有疑慮清單 ({len(doubt_list)} 個)...", flush=True)
    with open(DOUBT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '推薦國家', '距離', '備註'], delimiter='\t')
        writer.writeheader()
        writer.writerows(doubt_list)

print("\n" + "=" * 70, flush=True)
print(f"✅ Pass 3 完成！", flush=True)
print(f"  成功分類（累計）: {success_count} 個 ({success_count*100//total}%)", flush=True)
print(f"  本輪新增分類: {updated_from_pass2} 個", flush=True)
print(f"  有疑慮（標記為？）: {doubt_count} 個", flush=True)
print(f"  完全失敗: {fail_count} 個", flush=True)
print("=" * 70, flush=True)

if doubt_list:
    print(f"\n💡 有疑慮的檔案已保存到: {DOUBT_FILE}", flush=True)
    print(f"   請檢查這 {len(doubt_list)} 個檔案是否正確", flush=True)
