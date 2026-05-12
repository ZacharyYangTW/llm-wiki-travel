#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併日本剩餘的重複目錄
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\日本"

# 剩餘的合併對應
MERGE_MAP = {
    '山梨縣': '山梨県',
    '富山縣': '富山県',
    '埼玉縣': '埼玉県',
    '宮崎縣': '宮崎県',
}

print("=" * 70, flush=True)
print("🔧 合併日本剩餘重複目錄", flush=True)
print("=" * 70, flush=True)

merged_count = 0
files_moved = 0
failed_list = []

for chinese_name, japanese_name in sorted(MERGE_MAP.items()):
    chinese_path = os.path.join(WIKI_BASE, chinese_name)
    japanese_path = os.path.join(WIKI_BASE, japanese_name)

    # 檢查繁體中文版本是否存在
    if not os.path.isdir(chinese_path):
        continue

    # 如果日文版本不存在，創建它
    if not os.path.isdir(japanese_path):
        os.makedirs(japanese_path, exist_ok=True)
        print(f"\n📁 創建目錄: {japanese_name}", flush=True)

    # 列出繁體中文版本中的檔案
    items = os.listdir(chinese_path)

    if not items:
        print(f"\n✓ {chinese_name} 是空目錄，直接刪除", flush=True)
        try:
            os.rmdir(chinese_path)
            merged_count += 1
        except Exception as e:
            failed_list.append((chinese_name, str(e)[:50]))
        continue

    print(f"\n🔀 合併 {chinese_name} → {japanese_name} ({len(items)} 項)", flush=True)

    # 移動所有檔案和子目錄
    for item in items:
        chinese_item = os.path.join(chinese_path, item)
        japanese_item = os.path.join(japanese_path, item)

        try:
            # 如果目標已存在，刪除後再移動
            if os.path.exists(japanese_item):
                if os.path.isdir(japanese_item):
                    shutil.rmtree(japanese_item)
                else:
                    os.remove(japanese_item)

            shutil.move(chinese_item, japanese_item)
            files_moved += 1
            print(f"  ✓ {item}", flush=True)

        except Exception as e:
            failed_list.append((f"{chinese_name}/{item}", str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除空的繁體中文版本目錄
    try:
        if os.path.isdir(chinese_path) and not os.listdir(chinese_path):
            os.rmdir(chinese_path)
            merged_count += 1
    except Exception as e:
        failed_list.append((chinese_name, f"刪除失敗: {str(e)[:30]}"))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已合併: {merged_count} 對目錄", flush=True)
print(f"  已移動: {files_moved} 個項目", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)

print(f"{'='*70}", flush=True)
