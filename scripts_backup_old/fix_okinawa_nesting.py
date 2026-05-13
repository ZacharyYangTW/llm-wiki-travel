#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正：把沖縌縣下的市町村目錄提升到沖縄県根目錄
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\日本"

okinawa_path = os.path.join(WIKI_BASE, '沖縄県')
nested_path = os.path.join(okinawa_path, '沖繍縣')

print("=" * 70, flush=True)
print("🔧 修正：提升沖繍縣下的市町村目錄", flush=True)
print("=" * 70, flush=True)

if not os.path.isdir(nested_path):
    print("沖繍縣 不存在", flush=True)
    sys.exit(1)

# 列出沖繍縣中的項目
items = os.listdir(nested_path)

print(f"\n🔀 將 {len(items)} 個市町村從 沖繍縣 提升到 沖縄県", flush=True)

moved = 0
failed = []

for item in items:
    nested_item = os.path.join(nested_path, item)
    target_item = os.path.join(okinawa_path, item)

    try:
        # 如果目標已存在，刪除後再移動
        if os.path.exists(target_item):
            if os.path.isdir(target_item):
                shutil.rmtree(target_item)
            else:
                os.remove(target_item)

        shutil.move(nested_item, target_item)
        moved += 1
        print(f"  ✓ {item}", flush=True)

    except Exception as e:
        failed.append((item, str(e)[:50]))
        print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

# 刪除空的沖繍縣目錄
try:
    if os.path.isdir(nested_path) and not os.listdir(nested_path):
        os.rmdir(nested_path)
        print(f"\n✓ 刪除空目錄: 沖繍縣", flush=True)
except Exception as e:
    failed.append(('沖繍縣', f"刪除失敗: {str(e)[:30]}"))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個項目", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
