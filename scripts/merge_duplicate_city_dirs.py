#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併重複的城市目錄
例如：廣州 + 廣州市 → 合併為 廣州市
"""

import os
import sys
import shutil
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 需要合併的目錄對（舊名, 新名）
MERGE_PAIRS = [
    # 廣東省
    ('廣東省/中山', '廣東省/中山市'),
    ('廣東省/廣州', '廣東省/廣州市'),
    ('廣東省/深圳', '廣東省/深圳市'),
    ('廣東省/珠海', '廣東省/珠海市'),
]

print("=" * 70, flush=True)
print("🔧 合併重複的城市目錄", flush=True)
print("=" * 70, flush=True)

merged_count = 0
files_moved = 0
failed_list = []

for old_name, new_name in MERGE_PAIRS:
    old_path = os.path.join(WIKI_BASE, old_name)
    new_path = os.path.join(WIKI_BASE, new_name)

    # 檢查舊目錄是否存在
    if not os.path.isdir(old_path):
        print(f"\n⚠️  {old_name} 不存在，跳過", flush=True)
        continue

    # 檢查新目錄是否存在
    if not os.path.isdir(new_path):
        print(f"\n⚠️  {new_name} 不存在，創建中...", flush=True)
        os.makedirs(new_path, exist_ok=True)

    # 列出舊目錄中的檔案
    items = os.listdir(old_path)

    if not items:
        print(f"\n✓ {old_name} 是空目錄，直接刪除", flush=True)
        try:
            os.rmdir(old_path)
            merged_count += 1
        except Exception as e:
            failed_list.append((old_name, str(e)[:50]))
        continue

    print(f"\n🔀 合併 {old_name} → {new_name} ({len(items)} 個項目)", flush=True)

    # 移動舊目錄中的所有檔案和子目錄到新目錄
    for item in items:
        old_item_path = os.path.join(old_path, item)
        new_item_path = os.path.join(new_path, item)

        try:
            if os.path.isfile(old_item_path):
                # 檔案直接移動
                if os.path.exists(new_item_path):
                    os.remove(new_item_path)
                shutil.move(old_item_path, new_item_path)
                files_moved += 1
                print(f"  ✓ {item}", flush=True)

            elif os.path.isdir(old_item_path):
                # 子目錄合併（遞迴）
                if os.path.exists(new_item_path):
                    # 目標子目錄已存在，移動其檔案
                    for subitem in os.listdir(old_item_path):
                        old_subitem = os.path.join(old_item_path, subitem)
                        new_subitem = os.path.join(new_item_path, subitem)
                        if os.path.exists(new_subitem):
                            if os.path.isfile(new_subitem):
                                os.remove(new_subitem)
                            else:
                                shutil.rmtree(new_subitem)
                        shutil.move(old_subitem, new_subitem)
                    shutil.rmtree(old_item_path)
                else:
                    # 目標子目錄不存在，整個移動
                    shutil.move(old_item_path, new_item_path)
                print(f"  ✓ {item}/ (子目錄)", flush=True)

        except Exception as e:
            failed_list.append((f"{old_name}/{item}", str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除舊目錄
    try:
        if os.path.isdir(old_path) and not os.listdir(old_path):
            os.rmdir(old_path)
            merged_count += 1
            print(f"  → 刪除空目錄 {old_name}", flush=True)
    except Exception as e:
        failed_list.append((old_name, f"刪除失敗: {str(e)[:30]}"))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已合併: {merged_count} 對目錄", flush=True)
print(f"  已移動: {files_moved} 個檔案", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)
    print(f"\n⚠️  失敗清單：", flush=True)
    for item, error in failed_list[:10]:
        print(f"  - {item}: {error}", flush=True)
    if len(failed_list) > 10:
        print(f"  ... 及其他 {len(failed_list)-10} 個", flush=True)

print(f"{'='*70}", flush=True)
