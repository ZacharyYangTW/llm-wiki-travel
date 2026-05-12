#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正所有印尼中的誤分類景點
包括 Medan、Palembang、Jakarta
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 城市中心座標
CITY_COORDS = {
    # 馬來西亞
    'Penang': (100.3333, 5.3667),
    'Kuala Lumpur': (101.6964, 3.1390),
    'Malacca': (102.2381, 2.1896),
    # 印尼
    'Medan': (98.6722, 3.5952),
    'Palembang': (104.7458, -2.9181),
    'Jakarta': (106.8456, -6.2088),
    # 新加坡
    'Singapore': (103.8500, 1.3500),
}

COUNTRY_BY_CITY = {
    'Penang': '馬來西亞',
    'Kuala Lumpur': '馬來西亞',
    'Malacca': '馬來西亞',
    'Medan': '印尼',
    'Palembang': '印尼',
    'Jakarta': '印尼',
    'Singapore': '新加坡',
}

def extract_coordinates_from_file(filepath):
    """從 markdown 檔案提取座標"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def get_nearest_city(coords):
    """根據座標找到最近的城市"""
    lng, lat = coords
    min_distance = float('inf')
    best_city = None

    for city_name, (city_lng, city_lat) in CITY_COORDS.items():
        distance = ((lng - city_lng) ** 2 + (lat - city_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_city = city_name

    return best_city, min_distance

def fix_all_misclassified():
    """修正所有誤分類景點"""
    print("=" * 100)
    print("🔧 修正所有印尼中的誤分類景點")
    print("=" * 100)

    source_cities = ['Medan', 'Palembang', 'Jakarta']
    total_moved = 0
    total_skipped = 0
    total_failed = 0

    for source_city in source_cities:
        print(f"\n{'='*100}")
        print(f"🔍 檢查 印尼/{source_city}/POI")
        print(f"{'='*100}\n")

        source_path = os.path.join(WIKI_BASE, '印尼', source_city, 'POI')

        if not os.path.isdir(source_path):
            print(f"   ❌ 目錄不存在")
            continue

        files = sorted(os.listdir(source_path))
        city_distribution = {}
        misclassified_count = 0

        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(source_path, filename)
            coords = extract_coordinates_from_file(filepath)

            if not coords:
                print(f"⚠️  無座標: {filename}")
                continue

            # 根據最近的城市判斷
            nearest_city, distance = get_nearest_city(coords)

            # 如果不是該城市，就需要移動
            if nearest_city != source_city:
                misclassified_count += 1
                target_country = COUNTRY_BY_CITY.get(nearest_city, '未知')
                city_distribution[nearest_city] = city_distribution.get(nearest_city, 0) + 1

                # 檢查是否需要移動
                if target_country == '未知':
                    print(f"❌ 未知城市: {filename} ({nearest_city})")
                    total_failed += 1
                    continue

                # 建立目標目錄
                target_path = os.path.join(WIKI_BASE, target_country, nearest_city, 'POI')
                os.makedirs(target_path, exist_ok=True)

                source_file = filepath
                target_file = os.path.join(target_path, filename)

                # 檢查目標檔案是否已存在
                if os.path.exists(target_file):
                    # 刪除源檔案
                    try:
                        os.remove(source_file)
                        total_skipped += 1
                    except:
                        pass
                    continue

                # 移動檔案
                try:
                    shutil.move(source_file, target_file)
                    print(f"✅ {target_country}/{nearest_city}/{filename}")
                    total_moved += 1
                except Exception as e:
                    print(f"❌ 移動失敗: {filename} ({str(e)})")
                    total_failed += 1

        if misclassified_count > 0:
            print(f"\n   📊 誤分類統計:")
            for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True):
                print(f"      {city}: {count} 個檔案")
        else:
            print(f"   ✅ 無誤分類檔案")

    print(f"\n{'='*100}")
    print(f"✅ 全面修正完成！")
    print(f"   成功移動: {total_moved} 個檔案")
    print(f"   已存在跳過: {total_skipped} 個檔案")
    print(f"   移動失敗: {total_failed} 個檔案")
    print(f"{'='*100}")

if __name__ == '__main__':
    fix_all_misclassified()
