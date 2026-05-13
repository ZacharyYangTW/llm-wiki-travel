#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復靜岡県/靜岡縣/伊東市 的結構
應該是：靜岡県/伊東市
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

def main():
    print("=" * 70)
    print("🔧 修復靜岡県 結構")
    print("=" * 70)
    print()

    # 來源和目標路徑
    src_path = os.path.join(WIKI_DIR, "日本", "靜岡県", "靜岡縣", "伊東市")
    dst_path = os.path.join(WIKI_DIR, "日本", "靜岡県", "伊東市")
    extra_dir = os.path.join(WIKI_DIR, "日本", "靜岡県", "靜岡縣")

    # 移動所有檔案
    moved_count = 0
    if os.path.exists(src_path):
        os.makedirs(dst_path, exist_ok=True)

        for item in os.listdir(src_path):
            src_item = os.path.join(src_path, item)
            dst_item = os.path.join(dst_path, item)

            if os.path.isfile(src_item):
                shutil.move(src_item, dst_item)
                print(f"  ✓ 移動: {item}")
                moved_count += 1

    # 刪除多餘的子目錄
    try:
        shutil.rmtree(extra_dir)
        print(f"  ✓ 已刪除多餘目錄: 靜岡縣")
    except Exception as e:
        print(f"  ❌ 刪除失敗: {e}")

    print()
    print("=" * 70)
    print(f"✅ 修復完成，已移動 {moved_count} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
