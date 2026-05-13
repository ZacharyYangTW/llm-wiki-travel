#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pass 2 (簡化版): 用距離法補救失敗的檔案，然後將所有檔案移動到 wiki
"""

import os
import sys
import csv
import io
import shutil
import math
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\other_files_all.csv"
WIKI_OTHER_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\其他"
WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 世界主要城市中心（距離法備用）
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
    '美國': (-95.7129, 37.0902),
    '加拿大': (-106.3468, 56.1304),
    '墨西哥': (-102.5528, 23.6345),
    '秘魯': (-75.7482, -9.1900),
    '智利': (-71.5430, -35.6751),
    '澳洲': (133.7751, -25.2744),
    '荷蘭': (5.2913, 52.1326),
    '比利時': (4.4699, 50.5039),
    '法國': (2.2137, 46.2276),
    '西班牙': (-3.7492, 40.4637),
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

print("=" * 70, flush=True)
print("🗂️  Pass 2: 補救 + 移動到 Wiki", flush=True)
print("=" * 70, flush=True)

rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

print(f"📊 讀取 {len(rows)} 個檔案\n", flush=True)

# Pass 2: 補救無國家的檔案
for row in rows:
    if not row['國家'].strip():
        try:
            lat = float(row['緯度'].strip())
            lng = float(row['經度'].strip())
        except:
            continue

        # 用距離法找最近的國家
        min_dist = float('inf')
        best_country = None
        for country, (c_lng, c_lat) in WORLD_CENTERS.items():
            dist = euclidean_distance(lat, lng, c_lat, c_lng)
            if dist < min_dist:
                min_dist = dist
                best_country = country

        if best_country:
            row['國家'] = best_country
            row['城市'] = ''

# 寫回 CSV
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家', '原始路徑'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

# 移動檔案到 wiki
print("🗂️  移動檔案到 Wiki...\n", flush=True)

moved_count = 0
failed_count = 0

for i, row in enumerate(rows, 1):
    title = row['標題'].strip()
    country = row['國家'].strip()
    city = row['城市'].strip()
    orig_path = row['原始路徑'].strip()

    if not country:
        failed_count += 1
        continue

    # 找到源檔案
    src_file = os.path.join(WIKI_OTHER_DIR, orig_path)

    if not os.path.exists(src_file):
        failed_count += 1
        if i % 50 == 0:
            print(f"[{i:3d}/{len(rows)}] ❌ 找不到: {title[:30]}", flush=True)
        continue

    # 建立目標目錄
    if city:
        target_dir = os.path.join(WIKI_BASE, country, city)
    else:
        target_dir = os.path.join(WIKI_BASE, country)

    try:
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, f"{title}.md")

        shutil.move(src_file, target_file)
        moved_count += 1

        if i % 50 == 0 or i == 1:
            print(f"[{i:3d}/{len(rows)}] ✓ {country}/{city or '×':<15} | {title[:30]}", flush=True)

    except Exception as e:
        failed_count += 1
        if i % 50 == 0:
            print(f"[{i:3d}/{len(rows)}] ❌ 錯誤: {str(e)[:50]}", flush=True)

print("\n" + "=" * 70, flush=True)
print(f"✅ Pass 2 完成！", flush=True)
print(f"  成功移動: {moved_count} 個", flush=True)
print(f"  失敗: {failed_count} 個", flush=True)
print("=" * 70, flush=True)
