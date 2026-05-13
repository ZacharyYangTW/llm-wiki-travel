#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據坐標自動分類澳門、香港、捷克的未知檔案
使用歐氏距離計算最近的城市/地區中心
"""

import os
import sys
import re
import shutil
import math
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 澳門地區中心坐標 (lng, lat)
MACAU_DISTRICTS = {
    "澳門半島": (113.545, 22.200),
    "氹仔": (113.565, 22.158),
    "路環": (113.565, 22.130),
}

# 香港地區中心坐標 (lng, lat)
HONGKONG_DISTRICTS = {
    "香港島": (114.170, 22.280),
    "九龍": (114.170, 22.330),
    "新界": (114.200, 22.420),
    "離島": (114.000, 22.250),
}

# 捷克城市中心坐標 (lng, lat)
CZECHIA_CITIES = {
    "布拉格": (14.4365, 50.0755),
}

def extract_coordinates(file_path):
    """從檔案中提取坐標 [lng, lat]"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return (lng, lat)
    except Exception:
        pass

    return None

def calculate_distance(coord1, coord2):
    """計算兩個坐標之間的歐氏距離"""
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def find_nearest_district(coords, districts_dict):
    """找到最近的地區/城市"""
    nearest_name = None
    min_distance = float('inf')

    for name, center_coords in districts_dict.items():
        distance = calculate_distance(coords, center_coords)
        if distance < min_distance:
            min_distance = distance
            nearest_name = name

    return nearest_name

def classify_files(unknown_dir, country, districts_dict):
    """根據坐標分類未知目錄中的檔案"""
    if not os.path.exists(unknown_dir):
        print(f"  ⚠️  路徑不存在: {unknown_dir}")
        return 0, 0, 0

    moved_count = 0
    failed_count = 0
    no_coords_count = 0

    for filename in os.listdir(unknown_dir):
        if not filename.endswith('.md'):
            continue

        file_path = os.path.join(unknown_dir, filename)

        try:
            # 提取坐標
            coords = extract_coordinates(file_path)
            if not coords:
                no_coords_count += 1
                print(f"  ⚠️  無坐標: {filename}")
                continue

            # 找到最近的地區/城市
            district = find_nearest_district(coords, districts_dict)

            if not district:
                no_coords_count += 1
                continue

            # 建立目標目錄
            target_dir = os.path.join(WIKI_DIR, country, district)
            os.makedirs(target_dir, exist_ok=True)

            # 移動檔案
            target_path = os.path.join(target_dir, filename)
            shutil.move(file_path, target_path)
            moved_count += 1
            print(f"  ✓ {filename} → {country}/{district}/")

        except Exception as e:
            failed_count += 1
            print(f"  ❌ 錯誤: {filename} - {e}")

    return moved_count, failed_count, no_coords_count

def main():
    print("=" * 70)
    print("🗂️ 根據坐標自動分類澳門、香港、捷克的未知檔案")
    print("=" * 70)
    print()

    total_moved = 0
    total_failed = 0
    total_no_coords = 0

    # 分類澳門
    print("📍 澳門:")
    macau_unknown = os.path.join(WIKI_DIR, "澳門", "未知")
    moved, failed, no_coords = classify_files(macau_unknown, "澳門", MACAU_DISTRICTS)
    total_moved += moved
    total_failed += failed
    total_no_coords += no_coords
    print()

    # 分類香港
    print("📍 香港:")
    hongkong_unknown = os.path.join(WIKI_DIR, "香港", "未知")
    moved, failed, no_coords = classify_files(hongkong_unknown, "香港", HONGKONG_DISTRICTS)
    total_moved += moved
    total_failed += failed
    total_no_coords += no_coords
    print()

    # 分類捷克
    print("📍 捷克:")
    czechia_unknown = os.path.join(WIKI_DIR, "捷克", "未知")
    moved, failed, no_coords = classify_files(czechia_unknown, "捷克", CZECHIA_CITIES)
    total_moved += moved
    total_failed += failed
    total_no_coords += no_coords
    print()

    # 統計
    print("=" * 70)
    print(f"✅ 已移動: {total_moved} 個檔案")
    print(f"⚠️  無坐標: {total_no_coords} 個檔案")
    print(f"❌ 失敗: {total_failed} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
