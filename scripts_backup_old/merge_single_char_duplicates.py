#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併一字之差的重複目錄
保留帶 '市' 的版本
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# (短版本, 長版本, 國家, 省級)
DUPLICATES = [
    ('廣州', '廣州市', '中國', '廣東省'),
    ('蘭州', '蘭州市', '中國', '甘肅省'),
    ('福州', '福州市', '中國', '福建省'),
    ('拉薩', '拉薩市', '中國', '西藏自治區'),
    ('昆明', '昆明市', '中國', '雲南省'),
    ('麗江', '麗江市', '中國', '雲南省'),
]

print("=" * 70, flush=True)
print("🔧 合併一字之差的重複目錄", flush=True)
print("=" * 70, flush=True)

moved = 0
failed = []

for short, long, country, province in DUPLICATES:
    short_path = os.path.join(WIKI_BASE, country, province, short)
    long_path = os.path.join(WIKI_BASE, country, province, long)

    # 檢查短版本目錄是否存在
    if not os.path.isdir(short_path):
        print(f"\n⚠️  {country}/{province}/{short} 不存在", flush=True)
        continue

    # 確保長版本目錄存在
    os.makedirs(long_path, exist_ok=True)

    # 列出短版本目錄中的檔案
    items = os.listdir(short_path)

    if not items:
        # 如果短版本目錄為空，直接刪除
        try:
            os.rmdir(short_path)
            print(f"\n✓ {country}/{province}/{short}: 空目錄已刪除", flush=True)
        except:
            pass
        continue

    print(f"\n🔀 {country}/{province}/{short} → {long} ({len(items)} 項)", flush=True)

    for item in items:
        source_item = os.path.join(short_path, item)
        target_item = os.path.join(long_path, item)

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
            failed.append((f"{country}/{province}/{short}/{item}", str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除空的短版本目錄
    try:
        if os.path.isdir(short_path) and not os.listdir(short_path):
            os.rmdir(short_path)
    except:
        pass

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個項目", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
