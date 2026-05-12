#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正巴西/Paraná 中剩餘的誤分類檔案
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 需要移動的檔案 (源路徑, 目標目錄)
FILES_TO_MOVE = [
    ('h:\我的雲端硬碟\llm_wiki_travel\wiki\巴西\Paraná\POI\庫斯科.md',
     os.path.join(WIKI_BASE, '祕魯', '庫斯科')),
    ('h:\我的雲端硬碟\llm_wiki_travel\wiki\巴西\Paraná\POI\阿雷基帕.md',
     os.path.join(WIKI_BASE, '祕魯', '阿雷基帕')),
    ('h:\我的雲端硬碟\llm_wiki_travel\wiki\巴西\Paraná\POI\Humberstone and Santa Laura Saltpeter Works.md',
     os.path.join(WIKI_BASE, '智利', '聖佩德羅德阿塔卡瑪')),
]

print("=" * 100)
print("修正巴西/Paraná 中剩餘的誤分類檔案")
print("=" * 100)

moved_count = 0

for source_file, target_dir in FILES_TO_MOVE:
    filename = os.path.basename(source_file)

    if not os.path.exists(source_file):
        print(f"⚠️  源檔案不存在: {filename}")
        continue

    # 建立目標目錄
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, filename)

    # 檢查目標檔案是否已存在
    if os.path.exists(target_file):
        print(f"已存在: {filename} (刪除源檔案)")
        try:
            os.remove(source_file)
            moved_count += 1
        except Exception as e:
            print(f"  刪除失敗: {e}")
        continue

    # 移動檔案
    try:
        shutil.move(source_file, target_file)
        print(f"✓ 已移動: {filename}")
        moved_count += 1
    except Exception as e:
        print(f"✗ 移動失敗: {filename} - {e}")

print(f"\n{'='*100}")
print(f"✅ 修正完成！")
print(f"  已移動: {moved_count} 個檔案")
print(f"{'='*100}\n")
