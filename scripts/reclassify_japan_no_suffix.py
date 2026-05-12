#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新分類日本目錄中沒有"市"或"町"後綴的目錄
- 30 個目錄需要特殊映射到正確的市/町
- 1 個目錄（奈良）需要坐標計算來確定最近的奈良県市町
"""

import os
import sys
import re
import shutil
import math
import io
from pathlib import Path
from collections import defaultdict

# UTF-8 編碼支援
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
JAPAN_DIR = os.path.join(WIKI_DIR, "日本")

def euclidean_distance(coord1, coord2):
    """計算兩個坐標之間的歐氏距離"""
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

# ============================================================================
# 奈良県主要市町中心坐標
# ============================================================================
NARA_CITIES = {
    "奈良市": (135.8048, 34.6852),
    "大和郡山市": (135.7497, 34.6011),
    "天理市": (135.8450, 34.5980),
    "橿原市": (135.7942, 34.5007),
    "桜井市": (135.8620, 34.5089),
    "五條市": (135.7281, 34.3308),
    "御所市": (135.7342, 34.3833),
    "香芝市": (135.7208, 34.4584),
    "広陵町": (135.7758, 34.5222),
    "河合町": (135.7381, 34.5639),
    "吉野町": (135.8533, 34.2978),
}

# ============================================================================
# 29 個目錄的特殊映射
# ============================================================================
JAPAN_SPECIAL_MAP = {
    # 東京相關（9 個）
    "新宿": "東京都",
    "涉谷": "東京都",
    "新宿Airbnb": "東京都",
    "都營新宿線": "東京都",
    "池袋": "東京都",
    "原宿": "東京都",
    "千代田区": "東京都",

    # 大阪相關（1 個）
    "大阪心齋橋": "大阪市",

    # 沖繩相關（7 個）
    "沖繩": "那覇市",  # 沖繩本島主要城市
    "名護": "名護市",
    "北谷": "北谷町",
    "美麗海水族館": "本部町",
    "牧志": "那覇市",
    "玉泉洞": "南城市",  # 玉泉洞在南城市
    "國際通": "那覇市",

    # 其他地標和城市（10 個）
    "富士山": "富士市",  # 富士山在靜岡県
    "黑部水壩": "黑部市",  # 黑部在富山県
    "信濃大町": "大町市",  # 信濃大町是大町市的舊名
    "兵庫姬路": "姫路市",  # 已有重複，但保留
    "倉敷 Ario": "倉敷市",
    "松本": "松本市",
    "和歌山": "和歌山市",
    "新浦安": "浦安市",
    "江之島": "藤沢市",
    "伊勢": "伊勢市",
    "伊勢內宮前": "伊勢市",
    "中部國際機場": "名古屋市",
    "室堂": "立山町",  # 室堂在富山県立山町
    "京都": "京都市",
}

def extract_coordinates(file_path):
    """從檔案中提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尋找 coordinates: [lng, lat] 格式
        match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return (lng, lat)
    except Exception as e:
        pass

    return None

def find_nearest_nara_city(coordinates):
    """找到最近的奈良県市町"""
    if not coordinates:
        return "奈良市"  # 預設值

    min_distance = float('inf')
    nearest_city = "奈良市"

    for city, city_coords in NARA_CITIES.items():
        distance = euclidean_distance(coordinates, city_coords)
        if distance < min_distance:
            min_distance = distance
            nearest_city = city

    return nearest_city

def reclassify_directory(old_dir, new_city):
    """將一個目錄的所有檔案移動到新位置"""
    if not os.path.exists(old_dir):
        return 0

    new_dir = os.path.join(JAPAN_DIR, new_city)
    moved_count = 0

    try:
        # 建立新目錄
        os.makedirs(new_dir, exist_ok=True)

        # 移動所有檔案
        for filename in os.listdir(old_dir):
            old_file = os.path.join(old_dir, filename)
            new_file = os.path.join(new_dir, filename)

            if os.path.isfile(old_file):
                shutil.move(old_file, new_file)
                moved_count += 1

        # 刪除空目錄
        try:
            os.rmdir(old_dir)
        except:
            pass
    except Exception as e:
        print(f"❌ 錯誤移動 {os.path.basename(old_dir)}: {e}")

    return moved_count

def process_nara_directory():
    """處理奈良目錄 - 根據坐標分類到最近的市町"""
    nara_dir = os.path.join(JAPAN_DIR, "奈良")

    if not os.path.exists(nara_dir):
        return 0

    moved_count = 0
    file_stats = defaultdict(int)

    for filename in os.listdir(nara_dir):
        file_path = os.path.join(nara_dir, filename)

        if os.path.isfile(file_path) and filename.endswith('.md'):
            # 提取座標
            coords = extract_coordinates(file_path)
            nearest_city = find_nearest_nara_city(coords)

            # 建立目標目錄
            target_dir = os.path.join(JAPAN_DIR, nearest_city)
            os.makedirs(target_dir, exist_ok=True)

            # 移動檔案
            target_file = os.path.join(target_dir, filename)
            try:
                shutil.move(file_path, target_file)
                moved_count += 1
                file_stats[nearest_city] += 1
            except Exception as e:
                print(f"❌ 錯誤移動 {filename}: {e}")

    # 刪除空的奈良目錄
    try:
        os.rmdir(nara_dir)
    except:
        pass

    return moved_count

def main():
    print("=" * 60)
    print("🔄 重新分類日本目錄（無\"市\"或\"町\"後綴）")
    print("=" * 60)
    print()

    # 1. 先處理奈良（特殊坐標計算）
    print("📍 第 1 步：處理奈良縣（坐標計算）...")
    nara_moved = process_nara_directory()
    print(f"   ✅ 奈良縣：移動 {nara_moved} 個檔案")
    print()

    # 2. 處理其他 29 個目錄
    print("📍 第 2 步：處理其他 29 個目錄（特殊映射）...")
    total_moved = nara_moved

    for old_dir_name, new_city in JAPAN_SPECIAL_MAP.items():
        old_dir = os.path.join(JAPAN_DIR, old_dir_name)

        if os.path.exists(old_dir):
            moved = reclassify_directory(old_dir, new_city)
            if moved > 0:
                print(f"   ✅ {old_dir_name} → {new_city}: {moved} 個檔案")
                total_moved += moved

    print()
    print("=" * 60)
    print(f"✅ 完成！總共移動 {total_moved} 個檔案")
    print("=" * 60)

if __name__ == "__main__":
    main()
