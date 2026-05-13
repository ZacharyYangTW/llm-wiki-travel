#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化越南城市名稱為中文
大部分地點實際上是河內或胡志明市的區，應歸類到這兩個主要城市
"""

import os
import sys
import re
import shutil
import io
from pathlib import Path

# UTF-8 編碼支援
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# ============================================================================
# 越南城市英文 → 中文映射表
# ============================================================================
VIETNAM_CITY_MAP = {
    # 胡志明市（西貢）相關 - 31 個檔案
    "Saigon": "胡志明市",  # 28 個檔案
    "Sài Gòn": "胡志明市",  # 1 個檔案
    "Saigon Centre": "胡志明市",  # 1 個檔案

    # 河內相關 - 22 個檔案
    # 機場
    "Nội Bài": "河內",  # Nội Bài 是河內機場

    # 河內的西湖區（Tây Hồ）及周邊
    "Tây Hồ": "河內",
    "Tây Hoa Lư": "河內",
    "Trần Nhân Tông": "河內",

    # 河北市（Hải Phòng）相關
    "Hải Châu": "河北市",  # Hải Châu 是河北市的一個區
    "Hòa Cường": "河北市",
    "Cửa Nam": "河北市",

    # 河防市（Quảng Ninh）- 實際上是宁平省附近
    "Quynh Luu": "寧平省",  # Quỳnh Lưu 是寧平省的一個區

    # 南方其他地區 - 分散的小區
    "An Hội": "胡志明市",
    "An Khánh": "胡志明市",
    "An Nhon Tay": "胡志明市",
    "An Nhơn Tây": "胡志明市",
    "Long Hoa": "河北市",
    "Ninh Thạnh": "河北市",
    "Phu Khuong": "河北市",
    "Phú Khương": "河北市",  # 同上，不同拼法
    "Phu Tuc": "河北市",
    "Tan Son": "胡志明市",
}

def merge_directories(src_dir, dest_dir):
    """將 src_dir 的所有檔案移動到 dest_dir，然後刪除 src_dir"""
    if not os.path.exists(src_dir):
        return 0

    os.makedirs(dest_dir, exist_ok=True)
    moved_count = 0

    try:
        for filename in os.listdir(src_dir):
            src_file = os.path.join(src_dir, filename)
            dest_file = os.path.join(dest_dir, filename)

            if os.path.isfile(src_file):
                shutil.move(src_file, dest_file)
                moved_count += 1

        # 刪除空目錄
        try:
            os.rmdir(src_dir)
        except:
            pass
    except Exception as e:
        print(f"❌ 錯誤移動 {os.path.basename(src_dir)}: {e}")

    return moved_count

def main():
    print("=" * 70)
    print("🇻🇳 標準化越南城市名稱")
    print("=" * 70)
    print()

    vietnam_dir = os.path.join(WIKI_DIR, "越南")

    if not os.path.exists(vietnam_dir):
        print("❌ 越南目錄不存在")
        return

    print("📍 越南城市標準化")
    vietnam_moved = 0

    for old_name, new_name in VIETNAM_CITY_MAP.items():
        old_dir = os.path.join(vietnam_dir, old_name)

        if os.path.exists(old_dir) and old_name != new_name:
            new_dir = os.path.join(vietnam_dir, new_name)
            moved = merge_directories(old_dir, new_dir)
            if moved > 0:
                print(f"   ✅ {old_name} → {new_name}: {moved} 個檔案")
                vietnam_moved += moved

    print()
    print("=" * 70)
    print(f"✅ 完成！總共移動 {vietnam_moved} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
