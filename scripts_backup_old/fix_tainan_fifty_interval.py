#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正台南市「五十間」目錄 - 將檔案根據名稱分類到正確的行政區
"""

import os
import sys
import shutil
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 根據檔名分類到正確的行政區
FILENAME_MAPPING = {
    # 善化相關
    "台南-善化老家(已拆).md": "善化區",
    "台南-善化家(已遷).md": "善化區",
    "善化-最早阿嬤家(已拆).md": "善化區",
    "統一星巴克 - 善化門市.md": "善化區",

    # 新市相關
    "台南-新市家(已遷).md": "新市區",

    # 山上相關
    "台南-山上家(已遷).md": "山上區",

    # 南科相關（應在新市或善化）
    "南科迎曦湖.md": "新市區",
    "統一星巴克 - 南科.md": "新市區",

    # 不確定的歸到善化
    "大成國小.md": "善化區",
    "台南-宗諭家.md": "善化區",
    "麥當勞.md": "善化區",
    "愛媽廚房.md": "善化區",
    "全聯福利中心.md": "善化區",
    "米亞食尚館.md": "善化區",
    "上宇林.md": "善化區",
}

def reclassify_files():
    """重新分類五十間中的檔案"""
    fifty_interval_path = os.path.join(WIKI_DIR, "台灣", "台南市", "五十間")
    tainan_path = os.path.join(WIKI_DIR, "台灣", "台南市")

    moved_count = 0

    if not os.path.exists(fifty_interval_path):
        print(f"❌ 目錄不存在: {fifty_interval_path}")
        return 0

    # 列出五十間中的所有檔案
    files = os.listdir(fifty_interval_path)

    for filename in files:
        if not filename.endswith('.md'):
            continue

        src_path = os.path.join(fifty_interval_path, filename)

        # 根據檔名找到目標行政區
        target_district = FILENAME_MAPPING.get(filename)

        if not target_district:
            print(f"  ⚠️  未知檔案: {filename}")
            continue

        # 建立目標目錄
        target_dir = os.path.join(tainan_path, target_district)
        os.makedirs(target_dir, exist_ok=True)

        # 移動檔案
        target_path = os.path.join(target_dir, filename)
        try:
            shutil.move(src_path, target_path)
            moved_count += 1
            print(f"  ✓ {filename} → {target_district}/")
        except Exception as e:
            print(f"  ❌ 錯誤: {filename} - {e}")

    # 刪除空的五十間目錄
    try:
        if not os.listdir(fifty_interval_path):
            os.rmdir(fifty_interval_path)
            print(f"\n  ✓ 已刪除空的「五十間」目錄")
    except:
        pass

    return moved_count

def main():
    print("=" * 70)
    print("🔧 修正台南市「五十間」目錄分類")
    print("=" * 70)
    print()

    moved = reclassify_files()
    print()

    print("=" * 70)
    print(f"✅ 完成！{moved} 個檔案已重新分類")
    print("=" * 70)

if __name__ == "__main__":
    main()
