#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正廣西崇左中的越南河內景點誤分類
將所有河內景點從 中國/廣西壯族自治區/崇左 移到 越南/河內
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 河內座標範圍
HANOI_BOUNDS = {
    'lng': (105.7, 106.0),
    'lat': (20.9, 21.1)
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

def fix_chongzuo_hanoi():
    """修正崇左中被誤分類的河內景點"""
    print("=" * 100)
    print("修正廣西壯族自治區/崇左 中被誤分類的越南河內景點")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '中國', '廣西壯族自治區', '崇左')
    target_path = os.path.join(WIKI_BASE, '越南', '河內')

    if not os.path.isdir(source_path):
        print(f"崇左目錄不存在")
        return 0

    os.makedirs(target_path, exist_ok=True)

    files = sorted(os.listdir(source_path))
    to_move = []
    in_hanoi = 0
    no_coords = 0

    print(f"\n掃描 中國/廣西壯族自治區/崇左 中應屬於越南河內的景點...\n")

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"⚠️  無座標: {filename}")
            no_coords += 1
            continue

        # 檢查是否在河內範圍內
        if is_in_bounds(coords, HANOI_BOUNDS):
            in_hanoi += 1
            to_move.append({
                'file': filename,
                'coords': coords
            })
            print(f"✓ {filename}")
            print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f} (河內)")
        else:
            print(f"⚠️  不在河內範圍: {filename} - 座標: {coords[0]:.4f}, {coords[1]:.4f}")

    print(f"\n統計:")
    print(f"  河內景點: {in_hanoi} 個")
    print(f"  無座標: {no_coords} 個")
    print(f"  總檔案: {len(files)} 個\n")

    if not to_move:
        print(f"無需移動的檔案")
        return 0

    print(f"{'='*100}")
    print(f"開始移動檔案到越南/河內...\n")

    moved_count = 0
    failed_count = 0

    for item in to_move:
        filename = item['file']
        source_file = os.path.join(source_path, filename)
        target_file = os.path.join(target_path, filename)

        # 檢查目標檔案是否已存在
        if os.path.exists(target_file):
            print(f"已存在: {filename} (刪除源檔案)")
            try:
                os.remove(source_file)
                moved_count += 1
            except Exception as e:
                print(f"  刪除失敗: {e}")
                failed_count += 1
            continue

        # 移動檔案
        try:
            shutil.move(source_file, target_file)
            print(f"✓ 已移動: {filename}")
            moved_count += 1
        except Exception as e:
            print(f"✗ 移動失敗: {filename} - {e}")
            failed_count += 1

    print(f"\n{'='*100}")
    print("✅ 修正完成！")
    print(f"  已移動: {moved_count} 個檔案")
    print(f"  移動失敗: {failed_count} 個檔案")
    print(f"  總計: {moved_count + failed_count} 個檔案已處理")
    print(f"{'='*100}\n")

    return moved_count

if __name__ == '__main__':
    fix_chongzuo_hanoi()
