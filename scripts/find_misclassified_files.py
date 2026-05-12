#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描 Wiki 找出可能誤分類的檔案
基於檔名中的地名與實際位置不符
"""

import os
import sys
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 常見地名及其對應國家/城市
LOCATION_MAP = {
    'Kolkata': ('印度', '加爾各答'),
    'Calcutta': ('印度', '加爾各答'),
    'Delhi': ('印度', '德里'),
    'Mumbai': ('印度', '孟買'),
    'Bombay': ('印度', '孟買'),
    'Bangkok': ('泰國', '曼谷'),
    'Pattaya': ('泰國', '芭達雅'),
    'Chiang': ('泰國', '清邁'),
    'Tarragona': ('西班牙', '塔拉戈納'),
    'Barcelona': ('西班牙', '巴塞隆納'),
    'Madrid': ('西班牙', '馬德里'),
    'Tokyo': ('日本', '東京都'),
    'Osaka': ('日本', '大阪府'),
    'Kyoto': ('日本', '京都府'),
    'Taipei': ('台灣', '台北市'),
    'Taichung': ('台灣', '台中市'),
    'Kaohsiung': ('台灣', '高雄市'),
    'Shanghai': ('中國', '上海市'),
    'Beijing': ('中國', '北京'),
    'Guangzhou': ('中國', '廣州'),
}

print("=" * 70, flush=True)
print("🔍 掃描可能誤分類的檔案", flush=True)
print("=" * 70, flush=True)

misclassified = []

# 掃描所有檔案
for country in os.listdir(WIKI_BASE):
    country_path = os.path.join(WIKI_BASE, country)
    if not os.path.isdir(country_path):
        continue

    for city in os.listdir(country_path):
        city_path = os.path.join(country_path, city)
        if not os.path.isdir(city_path):
            continue

        for file in os.listdir(city_path):
            if not file.endswith('.md'):
                continue

            file_path = os.path.join(city_path, file)

            # 檢查檔名中的地名
            for location_name, (expected_country, expected_city) in LOCATION_MAP.items():
                if location_name.lower() in file.lower():
                    # 檢查是否在正確的位置
                    if country != expected_country or city != expected_city:
                        misclassified.append({
                            'file': file,
                            'current_location': f"{country}/{city}",
                            'correct_location': f"{expected_country}/{expected_city}",
                            'location_name': location_name,
                        })
                    break

if not misclassified:
    print("\n✅ 沒有找到明顯的誤分類檔案", flush=True)
else:
    print(f"\n⚠️  找到 {len(misclassified)} 個誤分類檔案\n", flush=True)

    for item in sorted(misclassified, key=lambda x: (x['current_location'], x['file'])):
        print(f"❌ {item['file']}", flush=True)
        print(f"   目前位置: {item['current_location']}", flush=True)
        print(f"   應該位置: {item['correct_location']}", flush=True)
        print()

print(f"{'='*70}", flush=True)
