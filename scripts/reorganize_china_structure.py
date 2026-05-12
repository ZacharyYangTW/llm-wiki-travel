#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正中國目錄結構
將城市移到對應的省級目錄下作為第二級
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\中國"

# (城市, 應該屬於的省)
CITY_PROVINCE_MAP = [
    ('廣州', '廣東省'),
    ('成都', '四川省'),
    ('昆明', '雲南省'),
    ('麗江', '雲南省'),
    ('敦煌', '甘肅省'),
    ('蘭州', '甘肅省'),
    ('福州', '福建省'),
    ('拉薩', '西藏自治區'),
    ('西安', '陝西省'),
]

print("=" * 70, flush=True)
print("🔧 修正中國目錄結構", flush=True)
print("=" * 70, flush=True)

moved = 0
failed = []

for city, province in CITY_PROVINCE_MAP:
    city_path = os.path.join(WIKI_BASE, city)
    province_path = os.path.join(WIKI_BASE, province)
    target_city_path = os.path.join(province_path, city)

    # 檢查城市目錄是否存在
    if not os.path.isdir(city_path):
        continue

    # 建立省級目錄和城市目錄
    os.makedirs(target_city_path, exist_ok=True)

    # 列出城市目錄中的項目
    items = os.listdir(city_path)

    if not items:
        # 如果城市目錄為空，直接刪除
        try:
            os.rmdir(city_path)
            print(f"\n✓ {city}: 空目錄已刪除", flush=True)
        except:
            pass
        continue

    print(f"\n🔀 {city} → {province}/{city} ({len(items)} 項)", flush=True)

    for item in items:
        source_item = os.path.join(city_path, item)
        target_item = os.path.join(target_city_path, item)

        try:
            # 如果目標已存在，刪除
            if os.path.exists(target_item):
                if os.path.isdir(target_item):
                    shutil.rmtree(target_item)
                else:
                    os.remove(target_item)

            shutil.move(source_item, target_item)
            moved += 1
            print(f"  ✓ {item}", flush=True)

        except Exception as e:
            failed.append((f"{city}/{item}", str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除空的城市目錄
    try:
        if os.path.isdir(city_path) and not os.listdir(city_path):
            os.rmdir(city_path)
    except:
        pass

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個項目", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
