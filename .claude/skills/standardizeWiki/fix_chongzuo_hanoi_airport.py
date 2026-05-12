#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正崇左中的河內機場檔案（座標超出常規河內範圍但仍屬河內）
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 需要移動的河內機場檔案（名稱包含特定關鍵詞）
AIRPORT_FILES = [
    'Noi Bai International Airport.md',
    'HAN-TPE.md',
    'HAN國內航廈T1.md',
    'HAN國際航廈T2.md',
    'Vietnam Airlines Lotus Lounge.md',
    'Cửa hàng Xăng dầu Hoàng Tân.md',
]

def move_airport_files():
    """移動河內機場檔案"""
    print("=" * 100)
    print("移動廣西崇左中的河內機場檔案")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '中國', '廣西壯族自治區', '崇左')
    target_path = os.path.join(WIKI_BASE, '越南', '河內')

    if not os.path.isdir(source_path):
        print(f"崇左目錄不存在")
        return 0

    os.makedirs(target_path, exist_ok=True)

    print(f"\n開始移動河內機場檔案...\n")

    moved_count = 0

    for filename in AIRPORT_FILES:
        source_file = os.path.join(source_path, filename)
        target_file = os.path.join(target_path, filename)

        if not os.path.exists(source_file):
            print(f"⚠️  源檔案不存在: {filename}")
            continue

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
    print(f"✅ 機場檔案移動完成！")
    print(f"  已移動: {moved_count} 個檔案")
    print(f"{'='*100}\n")

    return moved_count

if __name__ == '__main__':
    move_airport_files()
