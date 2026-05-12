#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 wiki/其他 提取所有檔案的坐標到 CSV
"""

import os
import sys
import csv
import io
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_OTHER_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\其他"
OUTPUT_CSV = r"h:\我的雲端硬碟\llm_wiki_travel\other_files_all.csv"

print("=" * 70, flush=True)
print("🔍 從 wiki/其他 提取坐標", flush=True)
print("=" * 70, flush=True)

# 正規表達式匹配坐標
coord_pattern = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

rows = []
total_files = 0
with_coords = 0
without_coords = 0

for md_file in Path(WIKI_OTHER_DIR).rglob('*.md'):
    total_files += 1

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取檔案名（不含路徑和.md）
        title = md_file.stem

        # 匹配坐標
        match = re.search(coord_pattern, content)

        if match:
            lng = match.group(1).strip()
            lat = match.group(2).strip()
            with_coords += 1

            rows.append({
                '標題': title,
                '經度': lng,
                '緯度': lat,
                '城市': '',
                '國家': '',
                '原始路徑': str(md_file.relative_to(WIKI_OTHER_DIR))
            })
        else:
            without_coords += 1

        if total_files % 20 == 0:
            print(f"[{total_files}] 處理中...", flush=True)

    except Exception as e:
        print(f"⚠️  錯誤 {md_file.name}: {str(e)[:50]}", flush=True)

# 寫入 CSV
print(f"\n💾 寫入 CSV ({len(rows)} 個)...", flush=True)
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家', '原始路徑'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 70, flush=True)
print(f"✅ 完成！", flush=True)
print(f"  總檔案數: {total_files}", flush=True)
print(f"  有坐標: {with_coords}", flush=True)
print(f"  無坐標: {without_coords}", flush=True)
print("=" * 70, flush=True)
