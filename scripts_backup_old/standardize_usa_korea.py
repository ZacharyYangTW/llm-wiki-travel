#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化美國和韓國城市名稱
- 美國：英文城市名 → 台灣常見的中文翻譯
- 韓國：合併重複目錄、標準化行政區名稱、分類未知位置
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
# 美國城市英文 → 中文（台灣常見翻譯）
# ============================================================================
USA_CITY_MAP = {
    # LA 和 Los Angeles 要合併
    "LA": "洛杉磯",
    "Los Angeles": "洛杉磯",
    "Santa Monica": "聖塔莫尼卡",
    "South San Francisco": "南舊金山",

    # Seattle 要合併到 西雅圖
    "Seattle": "西雅圖",

    # 其他城市
    "San Francisco": "舊金山",
    "San Antonio": "聖安東尼奧",
    "San Marcos": "聖馬科斯",
    "Austin": "奧斯汀",
    "Houston": "休斯頓",
    "Las Vegas": "拉斯維加斯",
    "Fairbanks": "費爾班克斯",
    "Anchorage": "安克雷奇",
    "North Pole": "北極",
    "Paradise": "天堂鎮",
    "Round Rock": "圓石鎮",
    "Concord": "康科德",
    "FAI": "費班克國際機場",  # Fairbanks International Airport
    "Suffolk County": "薩福克郡",
}

# ============================================================================
# 韓國城市標準化和分類
# ============================================================================
# 需要改名為廣域市的
KOREA_RENAME = {
    "釜山": "釜山廣域市",
    "大邱": "大邱廣域市",
    "首爾": "首爾特別市",  # 首爾的正式名稱是特別市
}

# 韓國/未知 中的檔案分類
# 基於地點名稱和地理知識
KOREA_UNKNOWN_MAP = {
    # 釜山相關（9 個）
    "Amnam-dong Community Service Center.md": "釜山廣域市",
    "Centum City.md": "釜山廣域市",
    "海雲臺.md": "釜山廣域市",
    "釜山站.md": "釜山廣域市",
    "南浦站.md": "釜山廣域市",
    "金海國際機場 PUS.md": "釜山廣域市",  # 金海是釜山附近
    "자갈치역札嘎其站.md": "釜山廣域市",
    "토성역.아미동입구.md": "釜山廣域市",
    "흰여울문화마을.md": "釜山廣域市",
    "서부정류장.md": "釜山廣域市",

    # 大邱相關（9 個）
    "TAE Daegu International Airport.md": "大邱廣域市",
    "Dalseong Park 達成公園.md": "大邱廣域市",
    "大邱站.md": "大邱廣域市",
    "東大邱站.md": "大邱廣域市",
    "東大邱綜合換乘中心 동대구터미널.md": "大邱廣域市",
    "Hamjigol Training Center.md": "大邱廣域市",
    "Oriental Medicine Market (Dongseong-ro Entrance).md": "大邱廣域市",
    "반월당.md": "大邱廣域市",
    "半月堂.md": "大邱廣域市",
    "석두령역.md": "大邱廣域市",
    "石頭嶺站.md": "大邱廣域市",
    "良洞市場 양동시장.md": "大邱廣域市",

    # 首爾相關（4 個）
    "Seonleung 宣陵站.md": "首爾特別市",
    "상수 上水.md": "首爾特別市",
    "Yaksu.md": "首爾特別市",
    "궁전라벤더.md": "首爾特別市",
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

def move_file(src_file, dest_dir):
    """移動單個檔案到目錄"""
    os.makedirs(dest_dir, exist_ok=True)
    dest_file = os.path.join(dest_dir, os.path.basename(src_file))

    try:
        shutil.move(src_file, dest_file)
        return True
    except Exception as e:
        print(f"❌ 錯誤移動 {os.path.basename(src_file)}: {e}")
        return False

def main():
    print("=" * 70)
    print("🌎 標準化美國和韓國城市")
    print("=" * 70)
    print()

    # ========================================================================
    # 美國城市標準化
    # ========================================================================
    print("🇺🇸 第 1 步：標準化美國城市名稱...")
    usa_dir = os.path.join(WIKI_DIR, "美國")
    usa_moved = 0

    for old_name, new_name in USA_CITY_MAP.items():
        old_dir = os.path.join(usa_dir, old_name)

        if os.path.exists(old_dir) and old_name != new_name:
            new_dir = os.path.join(usa_dir, new_name)
            moved = merge_directories(old_dir, new_dir)
            if moved > 0:
                print(f"   ✅ {old_name} → {new_name}: {moved} 個檔案")
                usa_moved += moved

    print()

    # ========================================================================
    # 韓國城市標準化（改名廣域市）
    # ========================================================================
    print("🇰🇷 第 2 步：標準化韓國城市名稱...")
    korea_dir = os.path.join(WIKI_DIR, "韓國")
    korea_moved = 0

    for old_name, new_name in KOREA_RENAME.items():
        old_dir = os.path.join(korea_dir, old_name)

        if os.path.exists(old_dir) and old_name != new_name:
            new_dir = os.path.join(korea_dir, new_name)
            moved = merge_directories(old_dir, new_dir)
            if moved > 0:
                print(f"   ✅ {old_name} → {new_name}: {moved} 個檔案")
                korea_moved += moved

    print()

    # ========================================================================
    # 韓國/未知 中的檔案分類
    # ========================================================================
    print("🇰🇷 第 3 步：分類韓國/未知 中的檔案...")
    korea_unknown_dir = os.path.join(korea_dir, "未知")
    unknown_moved = 0
    unmapped = []

    if os.path.exists(korea_unknown_dir):
        for filename in os.listdir(korea_unknown_dir):
            file_path = os.path.join(korea_unknown_dir, filename)

            if os.path.isfile(file_path):
                # 在映射表中查找
                if filename in KOREA_UNKNOWN_MAP:
                    dest_city = KOREA_UNKNOWN_MAP[filename]
                    dest_dir = os.path.join(korea_dir, dest_city)
                    if move_file(file_path, dest_dir):
                        unknown_moved += 1
                else:
                    unmapped.append(filename)

        # 刪除空的未知目錄
        try:
            os.rmdir(korea_unknown_dir)
        except:
            pass

    if unknown_moved > 0:
        print(f"   ✅ 分類 {unknown_moved} 個檔案")

    if unmapped:
        print(f"   ⚠️ {len(unmapped)} 個檔案無法映射：")
        for f in unmapped:
            print(f"      - {f}")

    print()
    print("=" * 70)
    print(f"✅ 完成！")
    print(f"   🇺🇸 美國：移動 {usa_moved} 個檔案")
    print(f"   🇰🇷 韓國：重命名 {korea_moved} 個目錄")
    print(f"   🇰🇷 韓國/未知：分類 {unknown_moved} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
