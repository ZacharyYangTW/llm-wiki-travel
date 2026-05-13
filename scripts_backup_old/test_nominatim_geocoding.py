#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 OpenStreetMap Nominatim 反向地理編碼
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

# 讀取 CSV 的前 5 個條目
rows = []
try:
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i >= 5:
                break
            lng = row['經度'].strip()
            lat = row['緯度'].strip()
            if lng and lat:
                rows.append({
                    'title': row['標題'].strip(),
                    'lng': lng,
                    'lat': lat
                })
except Exception as e:
    print(f"❌ 讀取 CSV 失敗: {e}")
    sys.exit(1)

print("=" * 70)
print("🔍 測試 OpenStreetMap Nominatim 反向地理編碼")
print("=" * 70)
print()

results = []

for i, item in enumerate(rows, 1):
    print(f"[{i}/5] 處理: {item['title']}")
    print(f"      坐標: ({item['lng']}, {item['lat']})")

    try:
        # 構建請求 URL
        params = {
            'format': 'json',
            'lat': item['lat'],
            'lon': item['lng'],
            'zoom': 10,
            'addressdetails': 1,
            'language': 'zh'  # 要求中文結果
        }

        # 設置 User-Agent（Nominatim 要求）
        headers = {
            'User-Agent': 'llm-wiki-travel-classifier'
        }

        # 發送請求
        url = f"{NOMINATIM_URL}?{urlencode(params)}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # 提取地址信息
            address = data.get('address', {})

            # 嘗試找到城市和國家
            city = (
                address.get('city') or
                address.get('town') or
                address.get('village') or
                address.get('county')
            )
            country = address.get('country', 'Unknown')

            print(f"      結果: {country} / {city or '未知'}")
            print(f"      詳細: {data.get('name', 'N/A')}")

            results.append({
                'title': item['title'],
                'coords': f"({item['lng']}, {item['lat']})",
                'country': country,
                'city': city or '未知',
                'name': data.get('name', 'N/A')
            })

        else:
            print(f"      ❌ API 錯誤: {response.status_code}")

    except Exception as e:
        print(f"      ❌ 錯誤: {e}")

    # 尊重速率限制
    if i < len(rows):
        time.sleep(1.5)
    print()

# 顯示摘要表格
print("=" * 70)
print("📊 結果摘要:")
print("=" * 70)
print()

if results:
    # 表頭
    print(f"{'標題':<30} | {'坐標':<25} | {'國家':<10} | {'城市':<15}")
    print("-" * 85)

    for r in results:
        title = r['title'][:28]
        coords = r['coords'][:23]
        country = r['country'][:10]
        city = r['city'][:15]
        print(f"{title:<30} | {coords:<25} | {country:<10} | {city:<15}")

print()
print("=" * 70)
print(f"✅ 成功: {len(results)}/5")
print("=" * 70)
