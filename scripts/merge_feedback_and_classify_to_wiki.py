#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併 feedback、更新 CSV，然後分類進 wiki
"""

import os
import sys
import csv
import io
import shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
DOUBT_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\files_need_manual_check.csv"
WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
UNKNOWN_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\未知\未分類"

print("=" * 70, flush=True)
print("🔄 合併 Feedback 並分類進 Wiki", flush=True)
print("=" * 70, flush=True)

# 讀取 feedback
feedback = {}
try:
    with open(DOUBT_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['標題'].strip()
            feedback[title] = {
                '城市': row.get('城市', '').strip(),
                '國家': row.get('國家', '').strip(),
            }
    print(f"📖 讀取 Feedback: {len(feedback)} 個修正\n", flush=True)
except Exception as e:
    print(f"⚠️  無法讀取 feedback: {e}\n", flush=True)

# 讀取原始 CSV
rows = []
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

print(f"📊 讀取 CSV: {len(rows)} 個檔案\n", flush=True)

# 合併 feedback
updated_count = 0
for row in rows:
    title = row['標題'].strip()
    if title in feedback:
        row['城市'] = feedback[title]['城市']
        row['國家'] = feedback[title]['國家']
        updated_count += 1

print(f"✅ 合併完成: {updated_count} 個檔案已更新\n", flush=True)

# 寫回 CSV
print("💾 寫入更新的 CSV...", flush=True)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

# 現在分類進 wiki
print("\n" + "=" * 70, flush=True)
print("🗂️  分類進 Wiki", flush=True)
print("=" * 70 + "\n", flush=True)

moved_count = 0
failed_count = 0
skipped_count = 0

for i, row in enumerate(rows, 1):
    title = row['標題'].strip()
    country = row['國家'].strip()
    city = row['城市'].strip()

    # 跳過沒有國家的
    if not country:
        skipped_count += 1
        continue

    # 移除末尾的 (?)
    country = country.replace(' (?)', '').strip()

    # 找到源檔案
    src_file = os.path.join(UNKNOWN_DIR, f"{title}.md")

    if not os.path.exists(src_file):
        failed_count += 1
        if i % 500 == 0:
            print(f"[{i:4d}/{len(rows)}] ❌ 找不到: {title[:30]}", flush=True)
        continue

    # 建立目標目錄
    if city:
        target_dir = os.path.join(WIKI_BASE, country, city)
    else:
        target_dir = os.path.join(WIKI_BASE, country)

    try:
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, f"{title}.md")

        # 移動檔案
        shutil.move(src_file, target_file)
        moved_count += 1

        if i % 500 == 0 or i == 1:
            print(f"[{i:4d}/{len(rows)}] ✓ {country}/{city or '×':<15} | {title[:30]}", flush=True)

    except Exception as e:
        failed_count += 1
        if i % 500 == 0:
            print(f"[{i:4d}/{len(rows)}] ❌ 錯誤: {str(e)[:50]}", flush=True)

print("\n" + "=" * 70, flush=True)
print(f"✅ 分類完成！", flush=True)
print(f"  成功移動: {moved_count} 個", flush=True)
print(f"  跳過（無國家）: {skipped_count} 個", flush=True)
print(f"  失敗: {failed_count} 個", flush=True)
print("=" * 70, flush=True)
