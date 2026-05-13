#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將日本/北海道札幌市 目錄合併到日本/北海道
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
HOKKAIDO_DIR = os.path.join(WIKI_DIR, "日本", "北海道")
HOKKAIDO_SAPPORO_DIR = os.path.join(WIKI_DIR, "日本", "北海道札幌市")

def main():
    print("=" * 70)
    print("🗂️ 合併日本/北海道札幌市 到日本/北海道")
    print("=" * 70)
    print()

    # 檢查目錄是否存在
    if not os.path.exists(HOKKAIDO_SAPPORO_DIR):
        print(f"❌ 來源目錄不存在: {HOKKAIDO_SAPPORO_DIR}")
        return

    if not os.path.exists(HOKKAIDO_DIR):
        print(f"❌ 目標目錄不存在: {HOKKAIDO_DIR}")
        return

    # 移動所有檔案和子目錄
    moved_count = 0
    failed_count = 0

    print(f"📂 掃描 {HOKKAIDO_SAPPORO_DIR}...")
    print()

    for item in os.listdir(HOKKAIDO_SAPPORO_DIR):
        src_path = os.path.join(HOKKAIDO_SAPPORO_DIR, item)
        dst_path = os.path.join(HOKKAIDO_DIR, item)

        try:
            if os.path.isfile(src_path):
                # 如果目標檔案已存在，跳過
                if os.path.exists(dst_path):
                    print(f"  ⚠️  檔案已存在，跳過: {item}")
                else:
                    shutil.move(src_path, dst_path)
                    moved_count += 1
                    print(f"  ✓ 移動檔案: {item}")
            elif os.path.isdir(src_path):
                # 如果目標目錄已存在，合併內容
                if os.path.exists(dst_path):
                    print(f"  ℹ️  合併子目錄: {item}")
                    # 遞迴複製所有檔案
                    for root, dirs, files in os.walk(src_path):
                        for file in files:
                            src_file = os.path.join(root, file)
                            rel_path = os.path.relpath(src_file, src_path)
                            dst_file = os.path.join(dst_path, rel_path)
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            if not os.path.exists(dst_file):
                                shutil.copy2(src_file, dst_file)
                                moved_count += 1
                else:
                    shutil.move(src_path, dst_path)
                    moved_count += 1
                    print(f"  ✓ 移動子目錄: {item}")
        except Exception as e:
            failed_count += 1
            print(f"  ❌ 錯誤: {item} - {e}")

    print()

    # 刪除空的來源目錄
    try:
        if not os.listdir(HOKKAIDO_SAPPORO_DIR):
            shutil.rmtree(HOKKAIDO_SAPPORO_DIR)
            print(f"✅ 已刪除空的來源目錄: 北海道札幌市")
        else:
            print(f"⚠️  來源目錄仍有內容，未刪除")
    except Exception as e:
        print(f"❌ 刪除來源目錄失敗: {e}")

    print()
    print("=" * 70)
    print(f"✅ 已移動: {moved_count} 個項目")
    if failed_count > 0:
        print(f"❌ 失敗: {failed_count} 個項目")
    print("=" * 70)

if __name__ == "__main__":
    main()
