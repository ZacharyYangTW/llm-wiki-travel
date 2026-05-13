#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試反向地理編碼 - 只處理前 10 個檔案
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

def reverse_geocode(lat, lng):
    """反向地理編碼"""
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
            return city, country, True
        return '', '', False
    except:
        return '', '', False

print("=" * 70)
print("🧪 測試反向地理編碼（前 10 個檔案）")
print("=" * 70)
print()

# 讀取前 10 個
rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for i, row in enumerate(reader):
        if i >= 10:
            break
        rows.append(row)

print(f"讀取 {len(rows)} 個檔案\n")

success = 0
for i, row in enumerate(rows, 1):
    title = row['標題'][:30]
    lng = row['經度'].strip()
    lat = row['緯度'].strip()

    city, country, result = reverse_geocode(lat, lng)

    if result:
        print(f"[{i:2d}] ✓ {title:<30} → {country}/{city}")
        success += 1
    else:
        print(f"[{i:2d}] ✗ {title:<30} → 無結果")

    time.sleep(1.5)

print()
print(f"成功: {success}/{len(rows)}")
