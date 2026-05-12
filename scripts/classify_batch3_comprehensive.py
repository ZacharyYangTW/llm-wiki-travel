#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 batch3_classification_data.csv 分類 wiki/未知 中的檔案
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
CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\batch3_classification_data.csv"

# 台灣省份對應（二級結構）
TAIWAN_MAPPING = {
    "金門縣金湖鎮": ("台灣", "金門縣", "金湖鎮"),
    "連江縣東引鄉": ("台灣", "連江縣", "東引鄉"),
    "新北市永和區": ("台灣", "新北市", "永和區"),
    "台東縣成功鎮": ("台灣", "台東縣", "成功鎮"),
    "台南市東區": ("台灣", "台南市", "東區"),
    "台南市善化區": ("台灣", "台南市", "善化區"),
}

# 日本都道府縣對應（二級結構）
JAPAN_MAPPING = {
    "北海道斜里郡斜里町": ("日本", "北海道", "斜里郡斜里町"),
    "東京都港區": ("日本", "東京都", "港區"),
    "靜岡縣伊東市": ("日本", "靜岡縣", "伊東市"),
    "神奈川縣橫濱市": ("日本", "神奈川縣", "橫濱市"),
    "神奈川縣鎌倉市": ("日本", "神奈川縣", "鎌倉市"),
    "佐賀縣鹿島市": ("日本", "佐賀縣", "鹿島市"),
    "福岡縣小郡市": ("日本", "福岡縣", "小郡市"),
    "福岡縣福岡市": ("日本", "福岡縣", "福岡市"),
    "長崎縣對馬市": ("日本", "長崎縣", "對馬市"),
    "福井縣福井市": ("日本", "福井縣", "福井市"),
    "福井縣坂井市": ("日本", "福井縣", "坂井市"),
    "石川縣小松市": ("日本", "石川縣", "小松市"),
    "石川縣金澤市": ("日本", "石川縣", "金澤市"),
    "沖繩縣那霸市": ("日本", "沖繩縣", "那霸市"),
    "沖繩縣宜野灣市": ("日本", "沖繩縣", "宜野灣市"),
    "沖繩縣宇流麻市": ("日本", "沖繩縣", "宇流麻市"),
    "沖繩縣國頭郡宜野座村": ("日本", "沖繩縣", "國頭郡宜野座村"),
    "沖繩縣浦添市": ("日本", "沖繩縣", "浦添市"),
    "沖繩縣南城市": ("日本", "沖繩縣", "南城市"),
    "沖繩縣豐見城市": ("日本", "沖繩縣", "豐見城市"),
    "沖繩縣糸滿市": ("日本", "沖繩縣", "糸滿市"),
    "青森縣弘前市": ("日本", "青森縣", "弘前市"),
    "青森縣八戶市": ("日本", "青森縣", "八戶市"),
    "岩手縣西磐井郡平泉町": ("日本", "岩手縣", "西磐井郡平泉町"),
}

# 中國省份對應（二級結構）
CHINA_MAPPING = {
    "上海市浦東新區": ("中國", "上海市", "浦東新區"),
    "上海市黃浦區": ("中國", "上海市", "黃浦區"),
    "黑龍江省哈爾濱市": ("中國", "黑龍江省", "哈爾濱市"),
    "湖南省岳陽市": ("中國", "湖南省", "岳陽市"),
}

# 其他國家映射（一級結構：國家 + 城市）
OTHER_MAPPING = {
    "光州廣域市": ("南韓", "光州廣域市"),
    "忠清南道論山市": ("南韓", "論山市"),
    "首爾特別市": ("南韓", "首爾特別市"),
    "首爾特別市江西區": ("南韓", "首爾特別市"),
    "京畿道廣州市": ("南韓", "廣州市"),
    "仁川廣域市中區": ("南韓", "仁川廣域市"),
    "慶尚南道金海市": ("南韓", "金海市"),
    "蔚山廣域市": ("南韓", "蔚山廣域市"),
    "慶尚北道浦項市": ("南韓", "浦項市"),
    "釜山廣域市": ("南韓", "釜山廣域市"),
    "德里": ("印度", "德里"),
    "加爾各答": ("印度", "加爾各答"),
    "孟買": ("印度", "孟買"),
    "清奈": ("印度", "清奈"),
    "曼谷": ("泰國", "曼谷"),
    "北欖府": ("泰國", "北欖府"),
    "檳城": ("馬來西亞", "檳城"),
    "胡志明市": ("越南", "胡志明市"),
    "河內": ("越南", "河內"),
    "廣寧省下龍市": ("越南", "下龍市"),
    "暹粒省": ("柬埔寨", "暹粒"),
    "菩薩省": ("柬埔寨", "菩薩"),
    "開羅省": ("埃及", "開羅"),
    "亞斯文省": ("埃及", "亞斯文"),
    "路克索省": ("埃及", "路克索"),
    "黃刀鎮": ("加拿大", "黃刀鎮"),
    "溫哥華": ("加拿大", "溫哥華"),
    "西雅圖": ("美國", "西雅圖"),
}

def load_csv_mapping():
    """從 CSV 讀取坐標和城市映射"""
    coord_map = {}
    title_map = {}

    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                title = row['標題'].strip()
                lng = row['經度'].strip()
                lat = row['緯度'].strip()
                city = row['城市'].strip()
                country = row['國家'].strip()

                # 建立坐標映射
                coord_key = f"{lng},{lat}"
                coord_map[coord_key] = (title, city, country)

                # 建立標題映射
                title_map[title] = (city, country)
    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return {}, {}

    return coord_map, title_map

def extract_coordinates(file_path):
    """從檔案中提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
        if match:
            lng = match.group(1).strip()
            lat = match.group(2).strip()
            return f"{lng},{lat}"
    except Exception:
        pass

    return None

def classify_file(file_path, filename, coord_map, title_map):
    """
    根據坐標或標題將檔案分類
    返回：(是否需要移動, 國家, 第一層目錄, 第二層目錄)
    第二層目錄：台灣/日本/中國 使用，其他國家為 None
    """
    # 1. 先嘗試標題匹配
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
            else:
                if city in OTHER_MAPPING:
                    c, c2 = OTHER_MAPPING[city]
                    return True, c, c2, None

    # 2. 嘗試坐標匹配
    coords = extract_coordinates(file_path)
    if coords and coords in coord_map:
        title, city, country = coord_map[coords]

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
    print("🗂️ 根據 batch3 數據分類 wiki/未知 中的檔案")
    print("=" * 70)
    print()

    # 讀取 CSV 映射
    coord_map, title_map = load_csv_mapping()
    print(f"✅ 已讀取 {len(title_map)} 個標題映射和 {len(coord_map)} 個坐標映射")
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
            result = classify_file(file_path, filename, coord_map, title_map)

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

    print()
    print("=" * 70)
    print(f"✅ 已移動: {moved_count} 個檔案")
    print(f"⚠️  未匹配: {unmatched_count} 個檔案")
    print(f"❌ 失敗: {failed_count} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
