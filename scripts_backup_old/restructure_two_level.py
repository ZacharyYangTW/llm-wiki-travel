#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將台灣和日本的檔案重新組織為二級目錄結構
wiki/{主要城市}/{次要城市}/
"""

import os
import sys
import re
import shutil
import io
from pathlib import Path
from collections import defaultdict

# UTF-8 編碼支援
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

def extract_location_info(file_path):
    """從檔案中提取位置信息（city 和 location 字段）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 city 字段
        city_match = re.search(r'city:\s*([^\n]+)', content)
        city = city_match.group(1).strip() if city_match else None

        # 提取 location 字段
        location_match = re.search(r'location:\s*([^\n]+)', content)
        location = location_match.group(1).strip() if location_match else None

        return city, location
    except Exception:
        pass

    return None, None

def restructure_country(country_name):
    """重新組織一個國家的檔案"""
    country_path = os.path.join(WIKI_DIR, country_name)

    if not os.path.exists(country_path):
        print(f"❌ 路徑不存在: {country_path}")
        return 0

    # 統計和移動檔案
    moved_count = 0
    file_stats = defaultdict(lambda: defaultdict(int))

    # 掃描所有一級目錄（主要城市）
    main_cities = [d for d in os.listdir(country_path)
                   if os.path.isdir(os.path.join(country_path, d))]

    for main_city in main_cities:
        main_city_path = os.path.join(country_path, main_city)

        # 掃描主要城市下的所有檔案
        files_in_root = [f for f in os.listdir(main_city_path)
                        if os.path.isfile(os.path.join(main_city_path, f)) and f.endswith('.md')]

        for filename in files_in_root:
            file_path = os.path.join(main_city_path, filename)

            try:
                # 提取位置信息
                city, location = extract_location_info(file_path)

                # 決定次級城市名稱
                # 優先使用 city，如果沒有則使用 location，都沒有則使用 main_city
                secondary_city = city or location or main_city

                # 清理次級城市名稱
                secondary_city = secondary_city.strip()
                if secondary_city == '未分類' or not secondary_city:
                    secondary_city = main_city

                # 建立次級目錄
                secondary_path = os.path.join(main_city_path, secondary_city)
                os.makedirs(secondary_path, exist_ok=True)

                # 移動檔案
                target_path = os.path.join(secondary_path, filename)
                if target_path != file_path:  # 確保不會複製到自己
                    shutil.move(file_path, target_path)
                    moved_count += 1
                    file_stats[main_city][secondary_city] += 1

            except Exception as e:
                print(f"  ❌ 錯誤: {filename} - {e}")

    return moved_count, file_stats

def main():
    print("=" * 70)
    print("🗂️ 重新組織為二級目錄結構")
    print("=" * 70)
    print()

    # 處理台灣
    print("🇹🇼 台灣")
    print("  組織為: wiki/台灣/{縣市}/{鎮鄉市}/")
    print()
    taiwan_moved, taiwan_stats = restructure_country("台灣")

    if taiwan_stats:
        for main_city, secondary_cities in sorted(taiwan_stats.items()):
            print(f"  {main_city}:")
            for secondary_city, count in sorted(secondary_cities.items()):
                print(f"    └─ {secondary_city}: {count} 個檔案")

    print(f"  📊 台灣小計: {taiwan_moved} 個檔案")
    print()

    # 處理日本
    print("🇯🇵 日本")
    print("  組織為: wiki/日本/{市町}/{詳細地點}/")
    print()
    japan_moved, japan_stats = restructure_country("日本")

    if japan_stats:
        city_count = 0
        for main_city in sorted(japan_stats.keys()):
            if city_count >= 10:  # 只顯示前 10 個主要城市
                print(f"  ... 及其他 {len(japan_stats) - 10} 個市町")
                break
            secondary_cities = japan_stats[main_city]
            print(f"  {main_city}: {sum(secondary_cities.values())} 個檔案")
            city_count += 1

    print(f"  📊 日本小計: {japan_moved} 個檔案")
    print()

    print("=" * 70)
    print(f"✅ 完成！")
    print(f"  台灣: {taiwan_moved} 個檔案")
    print(f"  日本: {japan_moved} 個檔案")
    print(f"  總計: {taiwan_moved + japan_moved} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
