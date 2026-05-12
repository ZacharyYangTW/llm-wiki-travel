#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Wiki 景點分類腳本
根據 coordinates 映射表，將 wiki/其他 中的景點移到正確的國家/城市目錄
"""

import os
import re
import json
import shutil
from pathlib import Path

# 設定路徑
WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
OTHER_DIR = os.path.join(WIKI_DIR, "其他")
UNKNOWN_CSV = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_coordinates.csv"

# 國家對應表（為了標準化）
COUNTRY_NAME_MAP = {
    "China": "中國",
    "Taiwan": "台灣",
    "Japan": "日本",
    "Thailand": "泰國",
    "Vietnam": "越南",
    "Cambodia": "柬埔寨",
    "Malaysia": "馬來西亞",
    "Singapore": "新加坡",
    "United States": "美國",
    "Canada": "加拿大",
    "Hong Kong": "香港",
    "Macao": "澳門",
    "South Korea": "韓國",
    "India": "印度",
    "Egypt": "埃及",
    "Netherlands": "荷蘭",
    "New Zealand": "紐西蘭",
}

def load_coordinates_map():
    """從 CSV 讀取 coordinates 映射"""
    coords_map = {}

    try:
        with open(UNKNOWN_CSV, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 跳過 header
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    title = parts[0].strip('"')
                    lng = parts[1].strip()
                    lat = parts[2].strip()
                    city = parts[3].strip('"')
                    country = parts[4].strip()

                    key = f"{lng},{lat}"
                    coords_map[key] = {
                        'title': title,
                        'city': city,
                        'country': country,
                    }
    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return {}

    return coords_map

def extract_coordinates(content):
    """從檔案內容中提取座標"""
    match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
    if match:
        lng = match.group(1).strip()
        lat = match.group(2).strip()
        return f"{lng},{lat}"
    return None

def move_file(old_path, new_country, new_city, new_filename):
    """移動檔案到新位置"""
    try:
        # 建立新目錄
        new_dir = os.path.join(WIKI_DIR, new_country, new_city)
        os.makedirs(new_dir, exist_ok=True)

        # 新路徑
        new_path = os.path.join(new_dir, new_filename)

        # 移動檔案
        if old_path != new_path:
            shutil.move(old_path, new_path)
            return True, new_path
        return False, old_path
    except Exception as e:
        print(f"  ❌ 移動失敗: {e}")
        return False, old_path

def main():
    print("=" * 60)
    print("修正 Wiki 景點分類")
    print("=" * 60)

    # 讀取映射表
    coords_map = load_coordinates_map()
    print(f"\n✅ 已讀取 {len(coords_map)} 個座標映射")

    if not coords_map:
        print("❌ 無法讀取座標映射，終止")
        return

    # 掃描 wiki/其他 目錄
    moved_count = 0
    failed_count = 0
    unknown_count = 0

    print(f"\n🔍 掃描 {OTHER_DIR}...")

    for root, dirs, files in os.walk(OTHER_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)

                try:
                    # 讀取檔案
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取座標
                    coords_key = extract_coordinates(content)
                    if not coords_key:
                        continue

                    # 查詢映射
                    if coords_key not in coords_map:
                        print(f"  ⚠️ 未找到映射: {file}")
                        unknown_count += 1
                        continue

                    mapping = coords_map[coords_key]
                    new_country = mapping['country']
                    new_city = mapping['city']

                    # 標準化國家名稱
                    if new_country in COUNTRY_NAME_MAP:
                        new_country = COUNTRY_NAME_MAP[new_country]

                    # 移動檔案
                    success, new_path = move_file(file_path, new_country, new_city, file)

                    if success:
                        print(f"✅ {file}")
                        print(f"   → {new_country}/{new_city}")
                        moved_count += 1
                    else:
                        print(f"⚠️ {file} (已在正確位置)")

                except Exception as e:
                    print(f"❌ {file}: {e}")
                    failed_count += 1

    # 統計
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
    print(f"✅ 已移動: {moved_count}")
    print(f"⚠️ 未知座標: {unknown_count}")
    print(f"❌ 失敗: {failed_count}")

if __name__ == "__main__":
    main()
