#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終修正衢州和福州的誤分類檔案
1. 刪除衢州中所有不屬於衢州的景點
2. 移動福州中所有台灣馬祖景點到連江縣
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 衢州座標範圍（內部邊界）
QUZHOU_BOUNDS = {
    'lng': (118.0, 119.5),
    'lat': (28.5, 29.5)
}

# 馬祖座標範圍（台灣連江縣）
MATSU_BOUNDS = {
    'lng': (119.5, 120.5),
    'lat': (25.8, 26.5)
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

def is_in_bounds(coords, bounds):
    """檢查座標是否在邊界內"""
    lng, lat = coords
    return (bounds['lng'][0] <= lng <= bounds['lng'][1] and
            bounds['lat'][0] <= lat <= bounds['lat'][1])

def fix_quzhou():
    """刪除衢州中不屬於衢州的景點"""
    print("=" * 100)
    print("修正浙江/衢州 中被誤分類的景點")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '中國', '浙江省', '衢州')

    if not os.path.isdir(source_path):
        print(f"衢州目錄不存在")
        return 0

    files = sorted(os.listdir(source_path))
    to_delete = []

    print(f"\n掃描 中國/浙江省/衢州 中不屬於衢州的檔案...\n")

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"⚠️  無座標: {filename}")
            continue

        # 檢查是否在衢州範圍內
        if not is_in_bounds(coords, QUZHOU_BOUNDS):
            to_delete.append({
                'file': filename,
                'coords': coords
            })
            print(f"✓ {filename}")
            print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f} (不在衢州範圍內)")

    if not to_delete:
        print(f"無需刪除的檔案")
        return 0

    print(f"\n{'='*100}")
    print(f"開始刪除不屬於衢州的景點...\n")

    deleted_count = 0

    for item in to_delete:
        filename = item['file']
        filepath = os.path.join(source_path, filename)

        try:
            os.remove(filepath)
            print(f"✓ 已刪除: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"✗ 刪除失敗: {filename}")

    return deleted_count

def fix_fuzhou_to_matsu():
    """移動福州中的台灣馬祖景點到連江縣"""
    print(f"\n{'='*100}")
    print("修正福建/福州 中應屬於台灣的馬祖景點")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '中國', '福建省', '福州')
    target_path = os.path.join(WIKI_BASE, '台灣', '連江縣')

    if not os.path.isdir(source_path):
        print(f"福州目錄不存在")
        return 0

    os.makedirs(target_path, exist_ok=True)

    files = sorted(os.listdir(source_path))
    to_move = []

    print(f"\n掃描 中國/福建省/福州 中應屬於馬祖(台灣)的檔案...\n")

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"⚠️  無座標: {filename}")
            continue

        # 檢查是否在馬祖範圍內
        if is_in_bounds(coords, MATSU_BOUNDS):
            to_move.append({
                'file': filename,
                'coords': coords
            })
            print(f"✓ {filename}")
            print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f} (在馬祖範圍內)")

    if not to_move:
        print(f"無需移動的檔案")
        return 0

    print(f"\n{'='*100}")
    print(f"開始移動檔案到台灣/連江縣...\n")

    moved_count = 0

    for item in to_move:
        filename = item['file']
        source_file = os.path.join(source_path, filename)
        target_file = os.path.join(target_path, filename)

        # 檢查目標檔案是否已存在
        if os.path.exists(target_file):
            print(f"已存在: 刪除源檔案 {filename}")
            try:
                os.remove(source_file)
                moved_count += 1
            except:
                pass
            continue

        # 移動檔案
        try:
            shutil.move(source_file, target_file)
            print(f"✓ 已移動: {filename}")
            moved_count += 1
        except Exception as e:
            print(f"✗ 移動失敗: {filename}")

    return moved_count

if __name__ == '__main__':
    print("\n")

    deleted = fix_quzhou()

    moved = fix_fuzhou_to_matsu()

    print(f"\n{'='*100}")
    print("✅ 修正完成！")
    print(f"  衢州 - 已刪除: {deleted} 個檔案")
    print(f"  福州→連江縣 - 已移動: {moved} 個檔案")
    print(f"  總計: {deleted + moved} 個檔案已修正")
    print(f"{'='*100}\n")
