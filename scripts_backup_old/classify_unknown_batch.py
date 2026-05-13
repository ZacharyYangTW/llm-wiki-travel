#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 CSV 的地理編碼結果重新分類 wiki/未知 中的檔案
"""

import os
import sys
import csv
import shutil
import re
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"

# 國家名稱標準化對應表
COUNTRY_MAPPING = {
    "中國": "中國",
    "台灣": "台灣",
    "日本": "日本",
    "泰國": "泰國",
    "越南": "越南",
    "柬埔寨": "柬埔寨",
    "馬來西亞": "馬來西亞",
    "新加坡": "新加坡",
    "美國": "美國",
    "加拿大": "加拿大",
    "香港": "香港",
    "澳門": "澳門",
    "南韓": "南韓",
    "韓國": "韓國",
    "印度": "印度",
    "埃及": "埃及",
    "荷蘭": "荷蘭",
    "法國": "法國",
    "西班牙": "西班牙",
    "匈牙利": "匈牙利",
    "比利時": "比利時",
    "盧森堡": "盧森堡",
    "紐西蘭": "紐西蘭",
    # 英文映射
    "China": "中國",
    "Taiwan": "台灣",
    "Japan": "日本",
    "Thailand": "泰國",
    "Vietnam": "越南",
    "Cambodia": "柬埔寨",
    "Malaysia": "馬來西亞",
    "Singapore": "新加坡",
    "United States": "美國",
    "USA": "美國",
    "Canada": "加拿大",
    "Hong Kong": "香港",
    "Macao": "澳門",
    "South Korea": "南韓",
    "Korea": "韓國",
    "India": "印度",
    "Egypt": "埃及",
    "Netherlands": "荷蘭",
    "France": "法國",
    "Spain": "西班牙",
    "Hungary": "匈牙利",
    "Belgium": "比利時",
    "Luxembourg": "盧森堡",
    "New Zealand": "紐西蘭",
}

def load_csv_mapping():
    """從 CSV 讀取地理編碼結果"""
    title_map = {}

    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                title = row['標題'].strip()
                city = row['城市'].strip()
                country = row['國家'].strip()

                # 標準化國家名稱
                if country in COUNTRY_MAPPING:
                    country = COUNTRY_MAPPING[country]

                # 只保存有效的條目（有城市和國家）
                if city and country:
                    title_map[title] = (city, country)

    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return {}

    return title_map

def move_file(src_path, dst_dir, filename):
    """移動檔案到目標目錄"""
    try:
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, filename)

        # 如果目標檔案已存在，跳過
        if os.path.exists(dst_path):
            return False, "已存在"

        shutil.move(src_path, dst_path)
        return True, dst_path
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("🗂️ 根據 CSV 地理編碼結果重新分類 wiki/未知 中的檔案")
    print("=" * 70)
    print()

    # 讀取 CSV 映射
    title_map = load_csv_mapping()
    print(f"✅ 已讀取 {len(title_map)} 個有效地理編碼")
    print()

    # 掃描 wiki/未知
    unknown_path = os.path.join(WIKI_DIR, "未知")
    if not os.path.exists(unknown_path):
        print(f"❌ 路徑不存在: {unknown_path}")
        return

    moved_count = 0
    unmatched_count = 0
    failed_count = 0
    existed_count = 0

    print(f"🔍 掃描 {unknown_path}...")
    print()

    for root, dirs, files in os.walk(unknown_path):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            file_path = os.path.join(root, filename)
            # 移除 .md 副檔名
            title = filename[:-3]

            # 在映射表中查詢
            if title in title_map:
                city, country = title_map[title]

                # 建立目標目錄（國家/城市）
                target_dir = os.path.join(WIKI_DIR, country, city)
                location_str = f"{country}/{city}/"

                # 移動檔案
                success, result = move_file(file_path, target_dir, filename)
                if success:
                    moved_count += 1
                    print(f"  ✓ {filename} → {location_str}")
                elif result == "已存在":
                    existed_count += 1
                    # 刪除源檔案（因為目標已存在）
                    try:
                        os.remove(file_path)
                    except:
                        pass
                else:
                    failed_count += 1
                    print(f"  ❌ {filename} - {result}")
            else:
                unmatched_count += 1

    print()
    print("=" * 70)
    print(f"✅ 已移動: {moved_count} 個檔案")
    print(f"📌 已存在（已刪除源檔案）: {existed_count} 個")
    print(f"⚠️  未匹配: {unmatched_count} 個檔案")
    print(f"❌ 失敗: {failed_count} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
