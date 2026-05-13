#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併美國舊金山相關目錄
南舊金山 -> 舊金山
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\美國"

source_name = '南舊金山'
target_name = '舊金山'

source_path = os.path.join(WIKI_BASE, source_name)
target_path = os.path.join(WIKI_BASE, target_name)

print("=" * 70, flush=True)
print("🔧 合併美國舊金山", flush=True)
print("=" * 70, flush=True)

if not os.path.isdir(source_path):
    print(f"\n❌ {source_name} 不存在", flush=True)
    sys.exit(1)

if not os.path.isdir(target_path):
    os.makedirs(target_path, exist_ok=True)
    print(f"\n📁 創建目錄: {target_name}", flush=True)

# 列出來源目錄中的檔案
items = os.listdir(source_path)

if not items:
    print(f"\n✓ {source_name} 是空目錄，直接刪除", flush=True)
    os.rmdir(source_path)
else:
    print(f"\n🔀 合併 {source_name} → {target_name} ({len(items)} 項)", flush=True)

    files_moved = 0
    failed = []

    # 移動所有檔案
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
            failed.append((item, str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除空的來源目錄
    try:
        if os.path.isdir(source_path) and not os.listdir(source_path):
            os.rmdir(source_path)
    except Exception as e:
        failed.append((source_name, f"刪除失敗: {str(e)[:30]}"))

    print(f"\n{'='*70}", flush=True)
    print(f"✅ 完成！", flush=True)
    print(f"  已移動: {files_moved} 個項目", flush=True)
    if failed:
        print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
