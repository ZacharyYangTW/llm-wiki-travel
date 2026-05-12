#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將阿格拉相關的檔案從德里移到阿格拉
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\印度"
DELHI_PATH = os.path.join(WIKI_BASE, '德里')
AGRA_PATH = os.path.join(WIKI_BASE, '阿格拉')

# 阿格拉相關的檔案（根據名稱或已知的坐標）
AGRA_FILES = [
    '泰姬瑪哈陵.md',        # Taj Mahal - 明確的阿格拉景點
    '阿格拉堡.md',         # Agra Fort - 明確的阿格拉景點
    'Itmad-ud-Daula.md',   # 坐標在阿格拉
]

print("=" * 70, flush=True)
print("🔧 將阿格拉檔案從德里移至阿格拉", flush=True)
print("=" * 70, flush=True)

# 創建阿格拉資料夾
os.makedirs(AGRA_PATH, exist_ok=True)
print(f"\n📁 確保阿格拉資料夾存在", flush=True)

moved = 0
failed = []

print(f"\n🔀 移動 {len(AGRA_FILES)} 個檔案:\n", flush=True)

for filename in AGRA_FILES:
    source_file = os.path.join(DELHI_PATH, filename)
    target_file = os.path.join(AGRA_PATH, filename)

    # 檢查來源檔案是否存在
    if not os.path.exists(source_file):
        print(f"⚠️  {filename} 不存在於德里", flush=True)
        continue

    # 如果目標已存在，刪除
    if os.path.exists(target_file):
        os.remove(target_file)

    try:
        shutil.move(source_file, target_file)
        moved += 1
        print(f"✓ {filename}", flush=True)
    except Exception as e:
        failed.append((filename, str(e)[:50]))
        print(f"❌ {filename}: {str(e)[:50]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個檔案", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

# 驗證阿格拉資料夾
print(f"\n📍 阿格拉資料夾現在包含:", flush=True)
agra_files = [f for f in os.listdir(AGRA_PATH) if f.endswith('.md')]
for f in sorted(agra_files):
    print(f"  - {f}", flush=True)

print(f"{'='*70}", flush=True)
