#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終合併：把沖繩縣的子目錄併入沖縄県
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\日本"

chinese_path = os.path.join(WIKI_BASE, '沖繩縣')
japanese_path = os.path.join(WIKI_BASE, '沖縄県')

print("=" * 70, flush=True)
print("🔧 最終合併：沖繩縣 → 沖縄県", flush=True)
print("=" * 70, flush=True)

if not os.path.isdir(chinese_path):
    print("沖繩縣 不存在", flush=True)
    sys.exit(1)

if not os.path.isdir(japanese_path):
    print("沖縄県 不存在，創建中...", flush=True)
    os.makedirs(japanese_path, exist_ok=True)

# 列出沖繩縣中的項目
items = os.listdir(chinese_path)

print(f"\n🔀 合併 沖繩縣 → 沖縄県 ({len(items)} 項)", flush=True)

moved = 0
failed = []

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
        moved += 1
        print(f"  ✓ {item}", flush=True)

    except Exception as e:
        failed.append((item, str(e)[:50]))
        print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

# 刪除空的沖繩縣目錄
try:
    if os.path.isdir(chinese_path) and not os.listdir(chinese_path):
        os.rmdir(chinese_path)
        print(f"\n✓ 刪除空目錄: 沖繩縣", flush=True)
except Exception as e:
    failed.append(('沖繩縣', f"刪除失敗: {str(e)[:30]}"))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個項目", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
