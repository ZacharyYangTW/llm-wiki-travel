#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 batch4_classification_data.csv 分類 wiki/未知 中的檔案
- 台灣、日本、中國：二級結構（省/縣 + 市/區）
- 其他國家：一級結構（國家 + 城市）
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
CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\batch4_classification_data.csv"

# 台灣省份對應（二級結構）
TAIWAN_MAPPING = {
    "台北市中正區": ("台灣", "台北市", "中正區"),
    "台北市大安區": ("台灣", "台北市", "大安區"),
    "新北市中和區": ("台灣", "新北市", "中和區"),
    "新北市三芝區": ("台灣", "新北市", "三芝區"),
    "台南市山上區": ("台灣", "台南市", "山上區"),
    "台東縣成功鎮": ("台灣", "台東縣", "成功鎮"),
    "宜蘭縣羅東鎮": ("台灣", "宜蘭縣", "羅東鎮"),
}

# 日本都道府縣對應（二級結構）
JAPAN_MAPPING = {
    "東京都武藏野市": ("日本", "東京都", "武藏野市"),
    "東京都新宿區": ("日本", "東京都", "新宿區"),
    "沖繩縣恩納村": ("日本", "沖繩縣", "恩納村"),
    "沖繩縣名護市": ("日本", "沖繩縣", "名護市"),
    "沖繩縣那霸市": ("日本", "沖繩縣", "那霸市"),
    "山梨縣富士河口湖町": ("日本", "山梨縣", "富士河口湖町"),
    "兵庫縣神戶市": ("日本", "兵庫縣", "神戶市"),
}

# 中國省份對應（二級結構）
CHINA_MAPPING = {
    "香港中西區": ("中國", "香港", "中西區"),
    "河南省鄭州市": ("中國", "河南省", "鄭州市"),
    "北京市海淀區": ("中國", "北京市", "海淀區"),
    "北京市朝陽區": ("中國", "北京市", "朝陽區"),
    "河南省安陽市": ("中國", "河南省", "安陽市"),
}

# 澳門（特別行政區）
MACAU_MAPPING = {
    "澳門": ("澳門", "澳門"),
}

# 其他國家映射（一級結構：國家 + 城市）
OTHER_MAPPING = {
    "費爾班克斯": ("美國", "費爾班克斯"),
    "拉斯維加斯": ("美國", "拉斯維加斯"),
    "亞利桑那大峽谷": ("美國", "亞利桑那大峽谷"),
    "洛杉磯": ("美國", "洛杉磯"),
    "黃刀鎮": ("加拿大", "黃刀鎮"),
    "吉隆坡": ("馬來西亞", "吉隆坡"),
    "新山市": ("馬來西亞", "新山市"),
    "新加坡": ("新加坡", "新加坡"),
    "廣寧省下龍市": ("越南", "下龍市"),
    "加爾各答": ("印度", "加爾各答"),
    "首爾特別市": ("南韓", "首爾特別市"),
}

def load_csv_mapping():
    """從 CSV 讀取坐標和城市映射"""
    title_map = {}

    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                title = row['標題'].strip()
                city = row['城市'].strip()
                country = row['國家'].strip()

                # 建立標題映射
                title_map[title] = (city, country)
    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return {}

    return title_map

def classify_file(filename, title_map):
    """
    根據檔名將檔案分類
    返回：(是否需要移動, 國家, 第一層目錄, 第二層目錄)
    """
    # 嘗試標題匹配
    for title, (city, country) in title_map.items():
        if title in filename:
            # 根據國家決定目錄層級
            if country == "台灣":
                if city in TAIWAN_MAPPING:
                    _, c1, c2 = TAIWAN_MAPPING[city]
                    return True, "台灣", c1, c2
            elif country == "日本":
                if city in JAPAN_MAPPING:
                    _, c1, c2 = JAPAN_MAPPING[city]
                    return True, "日本", c1, c2
            elif country == "中國":
                if city in CHINA_MAPPING:
                    _, c1, c2 = CHINA_MAPPING[city]
                    return True, "中國", c1, c2
            elif country == "澳門":
                if city in MACAU_MAPPING:
                    c, c2 = MACAU_MAPPING[city]
                    return True, c, c2, None
            else:
                if city in OTHER_MAPPING:
                    c, c2 = OTHER_MAPPING[city]
                    return True, c, c2, None

    return False, None, None, None

def move_file(src_path, dst_dir, filename):
    """移動檔案到目標目錄"""
    try:
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, filename)
        shutil.move(src_path, dst_path)
        return True, dst_path
    except Exception as e:
        print(f"  ❌ 移動失敗: {e}")
        return False, None

def main():
    print("=" * 70)
    print("🗂️ 根據 batch4 數據分類 wiki/未知 中的檔案")
    print("=" * 70)
    print()

    # 讀取 CSV 映射
    title_map = load_csv_mapping()
    print(f"✅ 已讀取 {len(title_map)} 個標題映射")
    print()

    # 掃描 wiki/未知
    unknown_path = os.path.join(WIKI_DIR, "未知")
    if not os.path.exists(unknown_path):
        print(f"❌ 路徑不存在: {unknown_path}")
        return

    moved_count = 0
    unmatched_count = 0
    failed_count = 0

    print(f"🔍 掃描 {unknown_path}...")
    print()

    for root, dirs, files in os.walk(unknown_path):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            file_path = os.path.join(root, filename)

            # 分類檔案
            result = classify_file(filename, title_map)

            if result[0]:  # 是否需要移動
                country = result[1]
                level1 = result[2]
                level2 = result[3]

                # 建立目標目錄
                if level2:  # 二級結構
                    target_dir = os.path.join(WIKI_DIR, country, level1, level2)
                    location_str = f"{country}/{level1}/{level2}/"
                else:  # 一級結構
                    target_dir = os.path.join(WIKI_DIR, country, level1)
                    location_str = f"{country}/{level1}/"

                # 移動檔案
                success, new_path = move_file(file_path, target_dir, filename)
                if success:
                    moved_count += 1
                    print(f"  ✓ {filename} → {location_str}")
                else:
                    failed_count += 1
            else:
                unmatched_count += 1
                print(f"  ⚠️  未匹配: {filename}")

    print()
    print("=" * 70)
    print(f"✅ 已移動: {moved_count} 個檔案")
    print(f"⚠️  未匹配: {unmatched_count} 個檔案")
    print(f"❌ 失敗: {failed_count} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
