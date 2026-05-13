#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超簡單版本 - 只做前 50 個檔案，每個檔案都顯示進度
"""

import os
import sys
import csv
import requests
import time
import io
from urllib.parse import urlencode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
LIMIT = 50  # 只處理前 50 個

def reverse_geocode(lat, lng):
    try:
        params = {'format': 'json', 'lat': lat, 'lon': lng, 'zoom': 10, 'addressdetails': 1, 'language': 'zh'}
        response = requests.get(f"{NOMINATIM_URL}?{urlencode(params)}", headers={'User-Agent': 'llm'}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
            country = address.get('country', '')
            return city, country, True
        return '', '', False
    except:
        return '', '', False

print("=" * 70, flush=True)
print(f"🌍 簡單反向地理編碼 (前 {LIMIT} 個檔案)", flush=True)
print("=" * 70, flush=True)

# 讀取前 50 個
rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for i, row in enumerate(reader):
        if i >= LIMIT:
            break
        rows.append(row)

print(f"📊 讀取 {len(rows)} 個檔案\n", flush=True)

success_count = 0
updated_rows = []

for i, row in enumerate(rows, 1):
    title = row['標題'][:20]
    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    # 反向地理編碼
    city, country, result = reverse_geocode(lat, lng)

    if result:
        row['城市'] = city
        row['國家'] = country
        success_count += 1
        status = "✓"
    else:
        status = "✗"

    # 每個檔案都輸出一行進度
    print(f"[{i:2d}/{len(rows)}] {status} {title:<20} → {country}/{city if city else '?'}", flush=True)

    updated_rows.append(row)
    time.sleep(1.5)

# 寫回 CSV
print("\n💾 寫入 CSV...", flush=True)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
    writer.writeheader()
    writer.writerows(updated_rows)

print(f"\n✅ 完成！成功: {success_count}/{len(rows)}", flush=True)
