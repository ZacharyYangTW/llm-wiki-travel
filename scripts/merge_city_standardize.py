#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化城市目錄名稱
保留「市」版本，合併短名稱版本
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 合併對應 (來源 -> 目標)
MERGE_MAP = {
    ('台灣', '台北', '台北市'),
    ('台灣', '台中', '台中市'),
    ('台灣', '高雄', '高雄市'),
    ('中國', '上海', '上海市'),
}

print("=" * 70, flush=True)
print("🔧 標準化城市目錄名稱", flush=True)
print("=" * 70, flush=True)

merged_count = 0
files_moved = 0
failed_list = []

for country, source_name, target_name in sorted(MERGE_MAP):
    country_path = os.path.join(WIKI_BASE, country)
    source_path = os.path.join(country_path, source_name)
    target_path = os.path.join(country_path, target_name)

    # 檢查來源是否存在
    if not os.path.isdir(source_path):
        continue

    # 如果目標不存在，創建它
    if not os.path.isdir(target_path):
        os.makedirs(target_path, exist_ok=True)

    # 列出來源目錄中的檔案
    items = os.listdir(source_path)

    if not items:
        print(f"\n✓ {country}/{source_name} 是空目錄，直接刪除", flush=True)
        try:
            os.rmdir(source_path)
            merged_count += 1
        except Exception as e:
            failed_list.append((f"{country}/{source_name}", str(e)[:50]))
        continue

    print(f"\n🔀 {country}: {source_name} → {target_name} ({len(items)} 項)", flush=True)

    # 移動所有檔案和子目錄
    for item in items:
        source_item = os.path.join(source_path, item)
        target_item = os.path.join(target_path, item)

        try:
            # 如果目標已存在，刪除後再移動
            if os.path.exists(target_item):
                if os.path.isdir(target_item):
                    shutil.rmtree(target_item)
                else:
                    os.remove(target_item)

            shutil.move(source_item, target_item)
            files_moved += 1
            print(f"  ✓ {item}", flush=True)

        except Exception as e:
            failed_list.append((f"{country}/{source_name}/{item}", str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除空的來源目錄
    try:
        if os.path.isdir(source_path) and not os.listdir(source_path):
            os.rmdir(source_path)
            merged_count += 1
    except Exception as e:
        failed_list.append((f"{country}/{source_name}", f"刪除失敗: {str(e)[:30]}"))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已合併: {merged_count} 對目錄", flush=True)
print(f"  已移動: {files_moved} 個項目", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

print(f"{'='*70}", flush=True)
