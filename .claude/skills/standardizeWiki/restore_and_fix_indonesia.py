#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢復並正確修正印尼檔案分類
包含巴淡（Batam）和其他印尼城市
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 所有城市中心座標（包括印尼城市）
CITY_COORDS = {
    # 馬來西亞
    'Penang': (100.3333, 5.3667),
    'Kuala Lumpur': (101.6964, 3.1390),
    'Malacca': (102.2381, 2.1896),
    'Johor': (103.7472, 1.4854),
    # 印尼
    'Jakarta': (106.8456, -6.2088),
    'Bandung': (107.6191, -6.9147),
    'Surabaya': (112.7380, -7.2575),
    'Medan': (98.6722, 3.5952),
    'Palembang': (104.7458, -2.9181),
    'Semarang': (110.4158, -6.9667),
    'Makassar': (119.4026, -5.1477),
    'Yogyakarta': (110.3722, -7.7956),
    'Bali': (115.2125, -8.6705),
    'Batam': (104.2067, 1.1333),  # 關鍵：巴淡座標
    # 新加坡
    'Singapore': (103.8500, 1.3500),
}

COUNTRY_BY_CITY = {
    # 馬來西亞
    'Penang': '馬來西亞',
    'Kuala Lumpur': '馬來西亞',
    'Malacca': '馬來西亞',
    'Johor': '馬來西亞',
    # 印尼
    'Jakarta': '印尼',
    'Bandung': '印尼',
    'Surabaya': '印尼',
    'Medan': '印尼',
    'Palembang': '印尼',
    'Semarang': '印尼',
    'Makassar': '印尼',
    'Yogyakarta': '印尼',
    'Bali': '印尼',
    'Batam': '印尼',
    # 新加坡
    'Singapore': '新加坡',
}

# 景點名稱關鍵詞映射到城市
KEYWORD_TO_CITY = {
    'nagoya': 'Batam',
    'batam': 'Batam',
    'island': 'Singapore',
    'marina': 'Singapore',
    'changi': 'Singapore',
    'orchard': 'Singapore',
    'sentosa': 'Singapore',
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

def get_city_from_filename(filename):
    """根據檔案名提取城市提示"""
    filename_lower = filename.lower()
    for keyword, city in KEYWORD_TO_CITY.items():
        if keyword in filename_lower:
            return city
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

def restore_and_fix():
    """恢復並正確修正印尼檔案"""
    print("=" * 100)
    print("🔧 恢復並正確修正印尼檔案分類")
    print("=" * 100)

    # 掃描新加坡中所有檔案，檢查是否應該在印尼
    source_path = os.path.join(WIKI_BASE, '新加坡', 'Singapore', 'POI')
    target_country = '印尼'

    print(f"\n📊 掃描 新加坡/Singapore/POI 中應屬於印尼的檔案...\n")

    if not os.path.isdir(source_path):
        print(f"   ❌ 源目錄不存在")
        return

    files = sorted(os.listdir(source_path))
    to_move = []
    city_distribution = {}

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            continue

        # 首先檢查檔案名中的關鍵詞
        keyword_city = get_city_from_filename(filename)
        if keyword_city:
            nearest_city = keyword_city
            distance = 0
        else:
            nearest_city, distance = get_nearest_city(coords)

        # 如果最近的城市是印尼的，就需要移動
        if COUNTRY_BY_CITY.get(nearest_city) == target_country:
            to_move.append({
                'file': filename,
                'coords': coords,
                'target_city': nearest_city,
                'distance': distance
            })
            city_distribution[nearest_city] = city_distribution.get(nearest_city, 0) + 1
            print(f"✅ {filename}")
            print(f"   座標: {coords[0]:.4f}, {coords[1]:.4f} → {nearest_city}")

    if not to_move:
        print(f"   無需移動的檔案")
        return

    print(f"\n{'='*100}")
    print(f"📝 開始移動檔案到印尼...\n")

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
            print(f"ℹ️  已存在: {target_city}/{filename}")
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
            print(f"❌ 移動失敗: {filename}")
            total_failed += 1

    print(f"\n{'='*100}")
    print(f"✅ 修正完成！")
    print(f"   成功移動: {total_moved} 個檔案")
    print(f"   移動失敗: {total_failed} 個檔案")
    if city_distribution:
        print(f"\n   📊 移動到印尼的分佈:")
        for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"      {city}: {count} 個檔案")
    print(f"{'='*100}")

if __name__ == '__main__':
    restore_and_fix()
