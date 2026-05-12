#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化泰國城市名稱為中文
大部分地點是主要城市（曼谷、普吉、清邁、芭堤雅等）的區域名
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
# 泰國城市英文/泰文 → 中文映射表
# ============================================================================
THAILAND_CITY_MAP = {
    # 普吉市（Phuket）相關 - 8 個檔案
    "Amphoe Mueang Phuket": "普吉市",
    "Chalong": "普吉市",  # Chalong 在普吉
    "Tambon Rawai": "普吉市",  # Rawai 在普吉
    "Tambon Wichit": "普吉市",  # Wichit 在普吉
    "Na Chom Thian": "普吉市",  # Na Chom Thian 在普吉
    "ตำบล ไม้ขาว": "普吉市",  # 泰文 ไม้ขาว (白木) 在普吉附近

    # 芭堤雅（Pattaya）及周邊 - 11 個檔案
    "Muang Pattaya": "芭堤雅",  # 6 個檔案
    "Si Racha District": "芭堤雅",  # Si Racha 在芭堤雅附近
    "Tambon Ta Khram En": "芭堤雅",
    "Tambon Bang Sare": "芭堤雅",
    "Bang Kachao": "芭堤雅",  # Bang Kachao 在曼谷-芭堤雅之間
    "Bang Mueang Mai": "芭堤雅",  # Bang Mueang Mai 在Eastern Seaboard
    "Bueng Yitho": "芭堤雅",

    # 清邁（Chiang Mai）相關 - 1 個檔案
    "Mueang Chiang Mai District": "清邁",

    # 中部（曼谷周邊）- 3 個檔案
    "Amphoe Bang Lamung": "曼谷",  # Bang Lamung 在曼谷附近
    "Amphoe Mueang Nonthaburi": "暖武里",  # Nonthaburi 是曼谷附近的府
    "Laem Sak": "曼谷",  # Laem Sak 在曼谷東方

    # 其他
    "Tambon Damnoen Saduak": "沙都克",  # 丹嫩沙多克水上市場在坤敬
    "Tambon Krasom": "拉廉",  # Krasom 在拉廉府
    "Krasom": "拉廉",
    "Tambon Lum Sum": "北欖",  # Lum Sum 在北欖府
    "Wiang": "清邁",  # Wiang 在清邁周邊
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
    print("🇹🇭 標準化泰國城市名稱")
    print("=" * 70)
    print()

    thailand_dir = os.path.join(WIKI_DIR, "泰國")

    if not os.path.exists(thailand_dir):
        print("❌ 泰國目錄不存在")
        return

    print("📍 泰國城市標準化")
    thailand_moved = 0

    for old_name, new_name in THAILAND_CITY_MAP.items():
        old_dir = os.path.join(thailand_dir, old_name)

        if os.path.exists(old_dir) and old_name != new_name:
            new_dir = os.path.join(thailand_dir, new_name)
            moved = merge_directories(old_dir, new_dir)
            if moved > 0:
                print(f"   ✅ {old_name} → {new_name}: {moved} 個檔案")
                thailand_moved += moved

    # 處理未知目錄 - 預設到主要城市
    unknown_dir = os.path.join(thailand_dir, "未知")
    if os.path.exists(unknown_dir):
        files = os.listdir(unknown_dir)
        if len(files) > 0:
            # 將未知位置分配到曼谷（泰國最大城市）
            bangkok_dir = os.path.join(thailand_dir, "曼谷")
            moved = merge_directories(unknown_dir, bangkok_dir)
            if moved > 0:
                print(f"   ✅ 未知 → 曼谷: {moved} 個檔案")
                thailand_moved += moved

    print()
    print("=" * 70)
    print(f"✅ 完成！總共移動 {thailand_moved} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
