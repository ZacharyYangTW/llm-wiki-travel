#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新增瓦拉那西城市資料夾
並將所有 Varanasi 相關的檔案移過去
"""

import os
import sys
import shutil
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\印度"
DELHI_PATH = os.path.join(WIKI_BASE, '德里')
VARANASI_PATH = os.path.join(WIKI_BASE, '瓦拉那西')

print("=" * 70, flush=True)
print("🔧 新增瓦拉那西城市並重新分類檔案", flush=True)
print("=" * 70, flush=True)

# 創建瓦拉那西資料夾
os.makedirs(VARANASI_PATH, exist_ok=True)
print(f"\n📁 創建資料夾: 瓦拉那西", flush=True)

# 列出德里資料夾中的所有 Varanasi 相關檔案
varanasi_files = []
for file in os.listdir(DELHI_PATH):
    file_path = os.path.join(DELHI_PATH, file)
    if os.path.isfile(file_path) and file.endswith('.md'):
        if 'Varanasi' in file or 'varanasi' in file or 'Vishwanath' in file:
            varanasi_files.append(file)

if not varanasi_files:
    print("\n⚠️  沒有找到 Varanasi 相關檔案", flush=True)
else:
    print(f"\n🔀 將 {len(varanasi_files)} 個檔案移動到瓦拉那西:", flush=True)

    moved = 0
    failed = []

    for file in sorted(varanasi_files):
        source_file = os.path.join(DELHI_PATH, file)
        target_file = os.path.join(VARANASI_PATH, file)

        try:
            if os.path.exists(target_file):
                os.remove(target_file)

            shutil.move(source_file, target_file)
            moved += 1
            print(f"  ✓ {file}", flush=True)

        except Exception as e:
            failed.append((file, str(e)[:50]))
            print(f"  ❌ {file}: {str(e)[:50]}", flush=True)

    print(f"\n{'='*70}", flush=True)
    print(f"✅ 完成！", flush=True)
    print(f"  已移動: {moved} 個檔案", flush=True)
    if failed:
        print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
