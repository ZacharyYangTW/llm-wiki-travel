#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Arunachal Pradesh 中被誤分類的西藏檔案
將它們從 印度/Arunachal Pradesh/POI 移到 中國/西藏自治區/適當城市
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 西藏城市中心座標
TIBET_CITY_COORDS = {
    'Lhasa': (91.1186, 29.6555),  # 拉薩
    'Shigatse': (88.8808, 28.7569),  # 日喀則
    'Nagqu': (91.9970, 31.4865),  # 那曲
    'Ali': (79.9244, 32.5014),  # 阿里
}

# 中文對應
CITY_TO_CHINESE = {
    'Lhasa': '拉薩',
    'Shigatse': '日喀則',
    'Nagqu': '那曲',
    'Ali': '阿里',
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
    """根據座標找到最近的西藏城市"""
    lng, lat = coords
    min_distance = float('inf')
    best_city = None

    for city_name, (city_lng, city_lat) in TIBET_CITY_COORDS.items():
        distance = ((lng - city_lng) ** 2 + (lat - city_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_city = city_name

    return best_city, min_distance

def fix_arunachal_pradesh():
    """修正 Arunachal Pradesh 中的誤分類檔案"""
    print("=" * 100)
    print("修正 Arunachal Pradesh 中被誤分類的西藏檔案")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '印度', 'Arunachal Pradesh', 'POI')

    if not os.path.isdir(source_path):
        print(f"源目錄不存在")
        return

    files = sorted(os.listdir(source_path))
    to_move = []
    city_distribution = {}

    print(f"\n掃描 印度/Arunachal Pradesh/POI 中應屬於西藏的檔案...\n")

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"無座標: {filename}")
            continue

        # 根據座標找到最近的西藏城市
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
    print(f"開始移動檔案到中國/西藏自治區...\n")

    total_moved = 0
    total_failed = 0

    for item in to_move:
        filename = item['file']
        target_city = item['target_city']
        target_city_cn = CITY_TO_CHINESE[target_city]

        # 建立目標目錄
        target_path = os.path.join(WIKI_BASE, '中國', '西藏自治區', target_city_cn)
        os.makedirs(target_path, exist_ok=True)

        source_file = os.path.join(source_path, filename)
        target_file = os.path.join(target_path, filename)

        # 檢查目標檔案是否已存在
        if os.path.exists(target_file):
            print(f"已存在: {target_city_cn}/{filename} (刪除源檔案)")
            try:
                os.remove(source_file)
                total_moved += 1
            except:
                pass
            continue

        # 移動檔案
        try:
            shutil.move(source_file, target_file)
            print(f"✓ {target_city_cn}/{filename}")
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
            city_cn = CITY_TO_CHINESE[city]
            print(f"    {city_cn}: {count} 個檔案")
    print(f"{'='*100}")

if __name__ == '__main__':
    fix_arunachal_pradesh()
