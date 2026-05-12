#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修正誤分類景點
根據座標和檔案內容判斷正確位置
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 地理坐標範圍定義
COUNTRY_COORDS = {
    '印尼': {'lng': (95, 141), 'lat': (-11, 6)},
    '馬來西亞': {'lng': (99.6, 119.3), 'lat': (0.85, 6.7)},
}

# 城市中心座標
CITY_COORDS = {
    'Penang': (100.3333, 5.3667),
    'Kuala Lumpur': (101.6964, 3.1390),
    'Malacca': (102.2381, 2.1896),
    'Medan': (98.6722, 3.5952),
    'Palembang': (104.7458, -2.9181),
}

def extract_coordinates_from_file(filepath):
    """從 markdown 檔案提取座標"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # 尋找 coordinates: [lng, lat] 格式
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def is_within_bounds(coords, bounds):
    """檢查座標是否在範圍內"""
    lng, lat = coords
    lng_min, lng_max = bounds['lng']
    lat_min, lat_max = bounds['lat']
    return lng_min <= lng <= lng_max and lat_min <= lat <= lat_max

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

def fix_misclassifications_comprehensive():
    """全面修正誤分類景點"""
    print("=" * 100)
    print("🔧 全面修正誤分類景點（根據座標和檔案內容）")
    print("=" * 100)

    source_country = '印尼'
    source_city = 'Medan'
    target_country = '馬來西亞'

    source_path = os.path.join(WIKI_BASE, source_country, source_city, 'POI')

    if not os.path.isdir(source_path):
        print(f"   ❌ 源目錄不存在: {source_path}")
        return

    files = sorted(os.listdir(source_path))
    to_move = []
    city_distribution = {}

    print(f"\n📊 掃描 {source_country}/{source_city}/POI 中的所有檔案...\n")

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"⚠️  無座標: {filename}")
            continue

        # 根據最近的城市判斷是否需要移動
        nearest_city, distance = get_nearest_city(coords)

        # 如果最近的城市不是 Medan，就需要移動
        if nearest_city and nearest_city != 'Medan':
            to_move.append({
                'file': filename,
                'coords': coords,
                'target_city': nearest_city,
                'distance': distance
            })
            city_distribution[nearest_city] = city_distribution.get(nearest_city, 0) + 1
            print(f"✅ {filename}")
            print(f"   座標: {coords[0]:.4f}, {coords[1]:.4f} → {nearest_city} (距離: {distance:.2f}°)")

    if not to_move:
        print(f"   ℹ️  無需移動的檔案")
        return

    print(f"\n{'='*100}")
    print(f"📝 開始移動檔案...\n")

    total_moved = 0
    total_failed = 0

    for item in to_move:
        filename = item['file']
        target_city = item['target_city']

        # 建立目標目錄
        target_path = os.path.join(WIKI_BASE, target_country, target_city, 'POI')
        os.makedirs(target_path, exist_ok=True)

        source_file = os.path.join(source_path, filename)
        target_file = os.path.join(target_path, filename)

        # 檢查目標檔案是否已存在
        if os.path.exists(target_file):
            print(f"ℹ️  已存在: {target_city}/{filename} (刪除源檔案)")
            try:
                os.remove(source_file)
                total_moved += 1
            except:
                pass
            continue

        # 移動檔案
        try:
            shutil.move(source_file, target_file)
            print(f"✅ {target_city}/{filename}")
            total_moved += 1
        except Exception as e:
            print(f"❌ 移動失敗: {filename} ({str(e)})")
            total_failed += 1

    print(f"\n{'='*100}")
    print(f"✅ 修正完成！")
    print(f"   成功移動: {total_moved} 個檔案")
    print(f"   移動失敗: {total_failed} 個檔案")
    if city_distribution:
        print(f"\n   📊 分佈:")
        for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"      {city}: {count} 個檔案")
    print(f"{'='*100}")

if __name__ == '__main__':
    fix_misclassifications_comprehensive()
