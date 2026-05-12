#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正西藏/阿里中被誤分類的印度檔案
將德里和阿格拉的景點從 中國/西藏自治區/阿里 移到 印度/Delhi/POI
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 印度城市中心座標
INDIA_CITY_COORDS = {
    'Delhi': (77.2090, 28.6139),  # 新德里
    'Agra': (78.0421, 27.1751),   # 阿格拉
}

# 中文對應
CITY_TO_CHINESE = {
    'Delhi': 'Delhi',
    'Agra': 'Delhi',  # 阿格拉在德里分類下
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
    """根據座標找到最近的印度城市"""
    lng, lat = coords
    min_distance = float('inf')
    best_city = None

    for city_name, (city_lng, city_lat) in INDIA_CITY_COORDS.items():
        distance = ((lng - city_lng) ** 2 + (lat - city_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_city = city_name

    return best_city, min_distance

def fix_tibet_ali_misclassification():
    """修正西藏/阿里中被誤分類的印度檔案"""
    print("=" * 100)
    print("修正西藏/阿里中被誤分類的印度檔案")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '中國', '西藏自治區', '阿里')

    if not os.path.isdir(source_path):
        print(f"源目錄不存在")
        return

    files = sorted(os.listdir(source_path))
    to_move = []
    city_distribution = {}

    print(f"\n掃描 中國/西藏自治區/阿里 中應屬於印度的檔案...\n")

    # India bounds for verification
    india_bounds = {'lng': (68, 97), 'lat': (8, 35)}

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"無座標: {filename}")
            continue

        # Check if in India region
        if not (india_bounds['lng'][0] <= coords[0] <= india_bounds['lng'][1] and \
                india_bounds['lat'][0] <= coords[1] <= india_bounds['lat'][1]):
            continue

        # 根據座標找到最近的印度城市
        nearest_city, distance = get_nearest_city(coords)

        to_move.append({
            'file': filename,
            'coords': coords,
            'target_city': nearest_city,
            'distance': distance
        })
        city_distribution[nearest_city] = city_distribution.get(nearest_city, 0) + 1
        print(f"✓ {filename}")
        print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f} → {CITY_TO_CHINESE[nearest_city]}")

    if not to_move:
        print(f"無需移動的檔案")
        return

    print(f"\n{'='*100}")
    print(f"開始移動檔案到印度...\n")

    total_moved = 0
    total_failed = 0

    for item in to_move:
        filename = item['file']
        target_city = item['target_city']

        # 建立目標目錄
        target_path = os.path.join(WIKI_BASE, '印度', target_city, 'POI')
        os.makedirs(target_path, exist_ok=True)

        source_file = os.path.join(source_path, filename)
        target_file = os.path.join(target_path, filename)

        # 檢查目標檔案是否已存在
        if os.path.exists(target_file):
            print(f"已存在: {target_city}/POI/{filename} (刪除源檔案)")
            try:
                os.remove(source_file)
                total_moved += 1
            except:
                pass
            continue

        # 移動檔案
        try:
            shutil.move(source_file, target_file)
            print(f"✓ {target_city}/POI/{filename}")
            total_moved += 1
        except Exception as e:
            print(f"失敗: {filename}")
            total_failed += 1

    print(f"\n{'='*100}")
    print(f"修正完成！")
    print(f"  成功移動: {total_moved} 個檔案")
    print(f"  移動失敗: {total_failed} 個檔案")
    if city_distribution:
        print(f"\n  分佈:")
        for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"    {city}: {count} 個檔案")
    print(f"{'='*100}")

if __name__ == '__main__':
    fix_tibet_ali_misclassification()
