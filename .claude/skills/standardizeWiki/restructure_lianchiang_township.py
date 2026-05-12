#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立台灣/連江縣的二級鄉鎮結構
將景點根據座標分類到南竿鎮、北竿鎮、莒光鎮、東引鎮
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 馬祖各鄉鎮座標中心
TOWNSHIP_COORDS = {
    '南竿鎮': (105.9274, 26.1411),    # 南竿遊客中心
    '北竿鎮': (119.9972, 26.2246),    # 北竿
    '莒光鎮': (106.0200, 26.2800),    # 東莒、西莒
    '東引鎮': (106.1100, 26.3800),    # 東引
}

# 馬祖各鄉鎮座標邊界
TOWNSHIP_BOUNDS = {
    '南竿鎮': {'lng': (105.90, 105.96), 'lat': (26.12, 26.16)},
    '北竿鎮': {'lng': (105.96, 106.00), 'lat': (26.20, 26.25)},
    '莒光鎮': {'lng': (106.00, 106.04), 'lat': (26.25, 26.30)},
    '東引鎮': {'lng': (106.08, 106.13), 'lat': (26.35, 26.40)},
}

# 非馬祖檔案（應刪除）
NON_MATSU_FILES = [
    '福州長樂機場.md',
    'long乐荣华快捷公寓.md',
    'FOC-KMG.md',  # 福州到馬祖航班代碼
]

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

def get_nearest_township(coords):
    """根據座標找到最近的鄉鎮"""
    lng, lat = coords
    min_distance = float('inf')
    best_township = None

    for township_name, (center_lng, center_lat) in TOWNSHIP_COORDS.items():
        distance = ((lng - center_lng) ** 2 + (lat - center_lat) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            best_township = township_name

    return best_township, min_distance

def restructure_lianchiang():
    """建立連江縣的鄉鎮結構"""
    print("=" * 100)
    print("建立台灣/連江縣的二級鄉鎮結構")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '台灣', '連江縣')

    if not os.path.isdir(source_path):
        print(f"連江縣目錄不存在")
        return

    # 創建鄉鎮目錄
    township_paths = {}
    for township in TOWNSHIP_COORDS.keys():
        township_path = os.path.join(source_path, township)
        os.makedirs(township_path, exist_ok=True)
        township_paths[township] = township_path

    files = sorted(os.listdir(source_path))

    # 第一步：清理非馬祖檔案
    print(f"\n{'='*100}")
    print("步驟1: 刪除非馬祖檔案\n")
    deleted_count = 0

    for filename in NON_MATSU_FILES:
        filepath = os.path.join(source_path, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"✓ 已刪除: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ 刪除失敗: {filename} - {e}")
        else:
            print(f"⚠️  檔案不存在: {filename}")

    # 重新讀取檔案列表（刪除非馬祖檔案後）
    files = sorted(os.listdir(source_path))

    # 第二步：分類馬祖景點到各鄉鎮
    print(f"\n{'='*100}")
    print("步驟2: 分類景點到各鄉鎮\n")

    township_distribution = {t: [] for t in TOWNSHIP_COORDS.keys()}
    unclassified = []

    for filename in files:
        # 跳過目錄
        filepath = os.path.join(source_path, filename)
        if os.path.isdir(filepath):
            continue

        if not filename.endswith('.md'):
            continue

        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"⚠️  無座標: {filename}")
            unclassified.append(filename)
            continue

        # 找到最近的鄉鎮
        nearest_township, distance = get_nearest_township(coords)
        township_distribution[nearest_township].append({
            'file': filename,
            'coords': coords,
            'distance': distance
        })

    # 輸出分類結果
    print("分類結果:")
    total_files = 0
    for township, items in township_distribution.items():
        count = len(items)
        total_files += count
        print(f"  {township}: {count} 個檔案")
    print(f"  未分類: {len(unclassified)} 個檔案")
    print(f"  共計: {total_files + len(unclassified)} 個檔案\n")

    # 第三步：移動檔案到鄉鎮目錄
    print(f"{'='*100}")
    print("步驟3: 移動檔案到鄉鎮目錄\n")

    moved_count = 0

    for township, items in township_distribution.items():
        if not items:
            continue

        target_path = township_paths[township]

        for item in items:
            filename = item['file']
            source_file = os.path.join(source_path, filename)
            target_file = os.path.join(target_path, filename)

            # 檢查目標檔案是否已存在
            if os.path.exists(target_file):
                print(f"已存在: {township}/{filename}")
                try:
                    os.remove(source_file)
                    moved_count += 1
                except:
                    pass
                continue

            # 移動檔案
            try:
                shutil.move(source_file, target_file)
                moved_count += 1
            except Exception as e:
                print(f"✗ 移動失敗: {filename} -> {township}/")

    # 輸出統計
    print(f"已移動: {moved_count} 個檔案\n")

    print(f"{'='*100}")
    print("✅ 連江縣鄉鎮結構重組完成！")
    print(f"  已刪除: {deleted_count} 個非馬祖檔案")
    print(f"  已分類: {moved_count} 個馬祖景點")
    print(f"  鄉鎮結構: 南竿鎮 / 北竿鎮 / 莒光鎮 / 東引鎮")
    print(f"{'='*100}\n")

if __name__ == '__main__':
    restructure_lianchiang()
