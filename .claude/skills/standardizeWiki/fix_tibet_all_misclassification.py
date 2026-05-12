#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正西藏自治區所有城市中被誤分類的檔案
主要是印度的城市檔案被誤分類到西藏
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 城市座標（包括真正的西藏城市和被誤分類的印度城市）
CITY_COORDS = {
    # 西藏城市
    'Lhasa': (91.1186, 29.6555),        # 拉薩
    'Shigatse': (88.8808, 28.7569),     # 日喀則
    'Nagqu': (91.9970, 31.4865),        # 那曲
    'Ali': (79.9244, 32.5014),          # 阿里
    # 印度城市
    'Delhi': (77.2090, 28.6139),        # 德里
    'Agra': (78.0421, 27.1751),         # 阿格拉
    'Varanasi': (83.0064, 25.2885),     # 瓦拉納西
    'Kolkata': (88.3511, 22.5579),      # 加爾各答
}

# 中文對應
CITY_TO_CHINESE = {
    'Lhasa': '拉薩',
    'Shigatse': '日喀則',
    'Nagqu': '那曲',
    'Ali': '阿里',
    'Delhi': 'Delhi',
    'Agra': 'Delhi',
    'Varanasi': '北方邦',  # 暫時用州名
    'Kolkata': 'West Bengal',
}

# 國家
CITY_TO_COUNTRY = {
    'Lhasa': '中國',
    'Shigatse': '中國',
    'Nagqu': '中國',
    'Ali': '中國',
    'Delhi': '印度',
    'Agra': '印度',
    'Varanasi': '印度',
    'Kolkata': '印度',
}

# 城市所在地區
CITY_TO_REGION = {
    'Lhasa': '西藏自治區',
    'Shigatse': '西藏自治區',
    'Nagqu': '西藏自治區',
    'Ali': '西藏自治區',
    'Delhi': 'Delhi',
    'Agra': 'Delhi',
    'Varanasi': 'Uttar Pradesh',
    'Kolkata': 'West Bengal',
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

def fix_tibet_misclassifications():
    """修正西藏中被誤分類的檔案"""
    print("=" * 100)
    print("修正西藏自治區中被誤分類的檔案")
    print("=" * 100)

    tibet_cities = ['拉薩', '日喀則', '那曲', '阿里']
    total_moved = 0
    total_failed = 0
    city_distribution = {}

    for tibet_city in tibet_cities:
        print(f"\n{'='*100}")
        print(f"掃描 中國/西藏自治區/{tibet_city} 中的誤分類檔案...\n")

        source_path = os.path.join(WIKI_BASE, '中國', '西藏自治區', tibet_city)

        if not os.path.isdir(source_path):
            print(f"目錄不存在")
            continue

        files = sorted(os.listdir(source_path))
        to_move = []

        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(source_path, filename)
            coords = extract_coordinates_from_file(filepath)

            if not coords:
                continue

            # 找到最近的城市
            nearest_city, distance = get_nearest_city(coords)

            # 只移動非西藏城市（距離遠於最近的西藏城市）
            if nearest_city not in ['Lhasa', 'Shigatse', 'Nagqu', 'Ali']:
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
            continue

        print(f"\n開始移動檔案...\n")

        for item in to_move:
            filename = item['file']
            target_city = item['target_city']
            target_country = CITY_TO_COUNTRY[target_city]
            target_region = CITY_TO_REGION[target_city]

            # 建立目標目錄
            if target_country == '中國':
                target_path = os.path.join(WIKI_BASE, target_country, target_region, target_region, 'POI')
            else:
                target_path = os.path.join(WIKI_BASE, target_country, target_region, 'POI')

            os.makedirs(target_path, exist_ok=True)

            source_file = os.path.join(source_path, filename)
            target_file = os.path.join(target_path, filename)

            # 檢查目標檔案是否已存在
            if os.path.exists(target_file):
                print(f"已存在: 刪除源檔案 {filename}")
                try:
                    os.remove(source_file)
                    total_moved += 1
                except:
                    pass
                continue

            # 移動檔案
            try:
                shutil.move(source_file, target_file)
                print(f"✓ {target_region}/POI/{filename}")
                total_moved += 1
            except Exception as e:
                print(f"✗ {filename}")
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
    fix_tibet_misclassifications()
