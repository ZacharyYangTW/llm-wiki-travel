#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反向地理編碼 - 限制版本（前 100 個檔案）
"""

import os
import sys
import csv
import requests
import time
import io
from urllib.parse import urlencode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
LIMIT = 100  # 只處理前 100 個

def reverse_geocode(lat, lng):
    try:
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lng,
            'zoom': 10,
            'addressdetails': 1,
            'language': 'zh'
        }
        headers = {'User-Agent': 'llm-wiki-travel'}
        url = f"{NOMINATIM_URL}?{urlencode(params)}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
            country = address.get('country', '')
            if city and country:
                return city, country, True
        return '', '', False
    except:
        return '', '', False

print("=" * 70)
print(f"🌍 批量反向地理編碼（前 {LIMIT} 個）")
print("=" * 70)
print()

# 讀取 CSV
rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for i, row in enumerate(reader):
        if i >= LIMIT:
            break
        rows.append(row)

print(f"📊 讀取 {len(rows)} 個檔案\n")

success_count = 0
updated_rows = []

for i, row in enumerate(rows, 1):
    title = row['標題'].strip()
    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    # 進度指示
    if i % 10 == 1:
        print(f"[{i:3d}/{len(rows)}]", end=' ')

    # 如果已有城市和國家，跳過
    if row['城市'].strip() and row['國家'].strip():
        updated_rows.append(row)
        print(".", end='', flush=True)
        continue

    # 反向地理編碼
    city, country, result = reverse_geocode(lat, lng)

    if result:
        row['城市'] = city
        row['國家'] = country
        success_count += 1
        print("✓", end='', flush=True)
    else:
        print("✗", end='', flush=True)

    updated_rows.append(row)
    time.sleep(1.5)

    if i % 10 == 0:
        print(f" ({success_count}/{i} ✓)")

print(f"\n\n✅ 完成！")
print(f"  成功編碼: {success_count} 個")
print(f"  已有地理編碼: {len(rows) - success_count} 個")
print()

# 寫回 CSV
print("💾 寫入 CSV...")
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
    writer.writeheader()
    writer.writerows(updated_rows)

print("✅ CSV 已更新！")
print()
print("=" * 70)
