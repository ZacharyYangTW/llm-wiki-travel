#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正巴西/Paraná 中被誤分類的祕魯庫斯科景點
將所有庫斯科景點從 巴西/Paraná 移到 祕魯/庫斯科
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 庫斯科座標範圍（秘魯安第斯山脈）
CUSCO_BOUNDS = {
    'lng': (-72.7, -71.8),
    'lat': (-13.6, -13.0)
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

def is_in_cusco_bounds(coords):
    """檢查座標是否在庫斯科範圍內"""
    lng, lat = coords
    return (CUSCO_BOUNDS['lng'][0] <= lng <= CUSCO_BOUNDS['lng'][1] and
            CUSCO_BOUNDS['lat'][0] <= lat <= CUSCO_BOUNDS['lat'][1])

def fix_parana_cusco():
    """修正巴西Paraná中被誤分類的庫斯科景點"""
    print("=" * 100)
    print("修正巴西/Paraná 中被誤分類的祕魯庫斯科景點")
    print("=" * 100)

    source_path = os.path.join(WIKI_BASE, '巴西', 'Paraná', 'POI')
    target_path = os.path.join(WIKI_BASE, '祕魯', '庫斯科')

    if not os.path.isdir(source_path):
        print(f"巴西/Paraná/POI 目錄不存在")
        return 0

    os.makedirs(target_path, exist_ok=True)

    files = sorted(os.listdir(source_path))
    to_move = []
    in_cusco = 0
    no_coords = 0

    print(f"\n掃描 巴西/Paraná/POI 中應屬於祕魯庫斯科的景點...\n")

    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(source_path, filename)
        coords = extract_coordinates_from_file(filepath)

        if not coords:
            print(f"⚠️  無座標: {filename}")
            no_coords += 1
            continue

        # 檢查是否在庫斯科範圍內
        if is_in_cusco_bounds(coords):
            in_cusco += 1
            to_move.append({
                'file': filename,
                'coords': coords
            })
            print(f"✓ {filename}")
            print(f"  座標: {coords[0]:.4f}, {coords[1]:.4f} (庫斯科)")
        else:
            print(f"⚠️  不在庫斯科範圍: {filename} - 座標: {coords[0]:.4f}, {coords[1]:.4f}")

    print(f"\n統計:")
    print(f"  庫斯科景點: {in_cusco} 個")
    print(f"  無座標: {no_coords} 個")
    print(f"  總檔案: {len(files)} 個\n")

    if not to_move:
        print(f"無需移動的檔案")
        return 0

    print(f"{'='*100}")
    print(f"開始移動檔案到祕魯/庫斯科...\n")

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
    fix_parana_cusco()
