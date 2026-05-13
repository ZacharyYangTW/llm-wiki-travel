#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正誤分類的檔案位置
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# (檔名, 目前位置, 目標位置)
MISCLASSIFIED_FILES = [
    ('Parc Central.md', ('印度', '加爾各答'), ('西班牙', '塔拉戈納')),
    ('CCU Kolkata airport.md', ('印度', '德里'), ('印度', '加爾各答')),
    ('聖保羅座堂 St. Paul\'s Cathedral Kolkata.md', ('印度', '德里'), ('印度', '加爾各答')),
    ('Bombay Lassi.md', ('印度', '清奈'), ('印度', '孟買')),
    ('PaPaLewis 大坂珈琲 osaka.md', ('台灣', '新北市'), ('日本', '大阪府')),
    ('KoKuMiN Do Raggushinosakaekiten.md', ('日本', '京都府'), ('日本', '大阪府')),
    ('Bombay Bistro.md', ('美國', '洛杉磯'), ('印度', '孟買')),
    ('Estacion Buses Tarragona.md', ('西班牙', '巴塞隆納'), ('西班牙', '塔拉戈納')),
    ('Teatro Romano de Tarragona.md', ('西班牙', '巴塞隆納'), ('西班牙', '塔拉戈納')),
]

print("=" * 70, flush=True)
print("🔧 修正誤分類的檔案", flush=True)
print("=" * 70, flush=True)

moved = 0
failed = []

for filename, current_loc, target_loc in MISCLASSIFIED_FILES:
    current_country, current_city = current_loc
    target_country, target_city = target_loc

    current_path = os.path.join(WIKI_BASE, current_country, current_city, filename)
    target_dir = os.path.join(WIKI_BASE, target_country, target_city)
    target_path = os.path.join(target_dir, filename)

    # 檢查來源檔案是否存在
    if not os.path.exists(current_path):
        print(f"\n⚠️  {filename} 不存在於 {current_country}/{current_city}", flush=True)
        continue

    # 創建目標目錄
    os.makedirs(target_dir, exist_ok=True)

    # 如果目標已存在，刪除
    if os.path.exists(target_path):
        os.remove(target_path)

    # 移動檔案
    try:
        shutil.move(current_path, target_path)
        moved += 1
        print(f"\n✓ {filename}", flush=True)
        print(f"  {current_country}/{current_city} → {target_country}/{target_city}", flush=True)
    except Exception as e:
        failed.append((filename, str(e)[:50]))
        print(f"\n❌ {filename}: {str(e)[:50]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個檔案", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

print(f"{'='*70}", flush=True)
