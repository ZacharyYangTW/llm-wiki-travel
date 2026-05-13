#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終清理：刪除空的重複目錄
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\日本"

# 要刪除的空目錄
EMPTY_DIRS = [
    '沖繩縣',  # 空目錄，併入到沖縄県
    '靜岡縣',  # 空目錄，保留静岡県（日文正確寫法）
]

print("=" * 70, flush=True)
print("🔧 最終清理：刪除空的重複目錄", flush=True)
print("=" * 70, flush=True)

deleted = 0
failed = []

for dir_name in EMPTY_DIRS:
    dir_path = os.path.join(WIKI_BASE, dir_name)

    if not os.path.isdir(dir_path):
        print(f"\n✓ {dir_name} 不存在", flush=True)
        continue

    # 檢查目錄是否為空
    items = os.listdir(dir_path)

    if items:
        print(f"\n⚠️  {dir_name} 不是空目錄 ({len(items)} 項)，跳過", flush=True)
        continue

    # 刪除空目錄
    try:
        os.rmdir(dir_path)
        deleted += 1
        print(f"\n✓ 刪除空目錄: {dir_name}", flush=True)
    except Exception as e:
        failed.append((dir_name, str(e)[:50]))
        print(f"\n❌ 刪除失敗: {dir_name} - {str(e)[:50]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已刪除: {deleted} 個空目錄", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
