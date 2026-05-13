#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描並合併所有重複的城市目錄（X 和 X市）
保留有「市」字的版本
"""

import os
import sys
import shutil
from collections import defaultdict
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\中國"

print("=" * 70, flush=True)
print("🔧 掃描並合併所有重複的城市目錄", flush=True)
print("=" * 70, flush=True)

merged_count = 0
files_moved = 0
failed_list = []

# 掃描所有省份
for province in sorted(os.listdir(WIKI_BASE)):
    province_path = os.path.join(WIKI_BASE, province)

    if not os.path.isdir(province_path):
        continue

    # 找出該省份的所有城市
    cities = {}  # 基礎名稱 -> [完整名稱列表]

    for city_name in os.listdir(province_path):
        city_path = os.path.join(province_path, city_name)
        if not os.path.isdir(city_path):
            continue

        # 提取基礎名稱（去掉「市」字）
        base_name = city_name.replace('市', '').replace('縣', '')

        if base_name not in cities:
            cities[base_name] = []
        cities[base_name].append(city_name)

    # 找出有重複的城市
    duplicates = {k: v for k, v in cities.items() if len(v) > 1}

    if not duplicates:
        continue

    print(f"\n📍 {province} (發現 {len(duplicates)} 個重複)", flush=True)

    for base_name, city_names in sorted(duplicates.items()):
        # 優先選擇有「市」字的版本
        has_shi = [c for c in city_names if '市' in c]
        target = has_shi[0] if has_shi else city_names[0]
        sources = [c for c in city_names if c != target]

        target_path = os.path.join(province_path, target)

        for source in sources:
            source_path = os.path.join(province_path, source)

            print(f"  🔀 {source} → {target}", flush=True)

            # 建立目標目錄
            os.makedirs(target_path, exist_ok=True)

            # 列出來源目錄中的項目
            try:
                items = os.listdir(source_path)
                for item in items:
                    src_item = os.path.join(source_path, item)
                    tgt_item = os.path.join(target_path, item)

                    # 如果目標已存在，刪除後再移動
                    if os.path.exists(tgt_item):
                        if os.path.isdir(tgt_item):
                            shutil.rmtree(tgt_item)
                        else:
                            os.remove(tgt_item)

                    shutil.move(src_item, tgt_item)
                    files_moved += 1

                # 刪除空的來源目錄
                try:
                    os.rmdir(source_path)
                    merged_count += 1
                except:
                    pass

            except Exception as e:
                failed_list.append((f"{province}/{source}", str(e)[:50]))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已合併: {merged_count} 對目錄", flush=True)
print(f"  已移動: {files_moved} 個項目", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)
    for item, error in failed_list[:5]:
        print(f"    - {item}: {error}", flush=True)

print(f"{'='*70}", flush=True)
