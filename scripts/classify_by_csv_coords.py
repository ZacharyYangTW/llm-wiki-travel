#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 CSV 座標資料分類 wiki/未知 中的檔案
建立二級目錄：wiki/{國家}/{完整城市代碼}/
例如：wiki/台灣/連江縣南竿鄉/
"""

import os
import sys
import re
import shutil
import csv
import io
from pathlib import Path

# UTF-8 編碼支援
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

def extract_coordinates(file_path):
    """從檔案中提取座標 [lng, lat]"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尋找 coordinates: [lng, lat] 格式
        match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return (lng, lat)
    except Exception:
        pass

    return None

def load_csv_mapping(csv_path):
    """讀取 CSV 檔案，建立坐標 → (國家, 城市) 的映射"""
    coord_map = {}

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    lng = float(row['經度'].strip())
                    lat = float(row['緯度'].strip())
                    country = row['國家'].strip()
                    city = row['城市代碼'].strip()

                    key = f"{lng},{lat}"
                    coord_map[key] = {
                        'country': country,
                        'city': city,
                        'location': row['位置名'].strip() if '位置名' in row else ''
                    }
                except ValueError:
                    continue

    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return {}

    return coord_map

def classify_files(csv_path, tolerance=0.0001):
    """
    根據 CSV 座標分類 wiki/未知 中的檔案
    tolerance: 座標匹配的容差度（防止浮點數誤差）
    """
    print("=" * 70)
    print("🗂️ 根據座標資料分類 wiki/未知 中的檔案")
    print("=" * 70)
    print()

    # 讀取 CSV 映射
    coord_map = load_csv_mapping(csv_path)
    if not coord_map:
        print("❌ CSV 映射表為空")
        return

    print(f"✅ 已讀取 {len(coord_map)} 個座標映射")
    print()

    # 掃描 wiki/未知
    unknown_path = os.path.join(WIKI_DIR, "未知", "未分類")
    if not os.path.exists(unknown_path):
        print(f"❌ 路徑不存在: {unknown_path}")
        return

    moved_count = 0
    not_found_count = 0
    failed_count = 0
    process_count = 0

    print(f"🔍 掃描 {unknown_path}...")
    print()

    for filename in os.listdir(unknown_path):
        if not filename.endswith('.md'):
            continue

        file_path = os.path.join(unknown_path, filename)
        process_count += 1

        if process_count % 100 == 0:
            print(f"  進度: {process_count} 個檔案...")

        try:
            # 提取座標
            coords = extract_coordinates(file_path)
            if not coords:
                failed_count += 1
                continue

            lng, lat = coords
            coord_key = f"{lng},{lat}"

            # 嘗試精確匹配
            mapping = coord_map.get(coord_key)

            # 如果精確匹配失敗，嘗試容差匹配
            if not mapping:
                for stored_key, stored_mapping in coord_map.items():
                    stored_lng, stored_lat = map(float, stored_key.split(','))
                    if abs(lng - stored_lng) < tolerance and abs(lat - stored_lat) < tolerance:
                        mapping = stored_mapping
                        break

            if mapping:
                country = mapping['country']
                city = mapping['city']

                # 建立目標目錄
                target_dir = os.path.join(WIKI_DIR, country, city)
                os.makedirs(target_dir, exist_ok=True)

                # 移動檔案
                target_path = os.path.join(target_dir, filename)
                shutil.move(file_path, target_path)
                moved_count += 1

                print(f"  ✅ {filename} → {country}/{city}/")
            else:
                not_found_count += 1

        except Exception as e:
            failed_count += 1
            print(f"  ❌ 錯誤: {filename} - {e}")

    print()
    print("=" * 70)
    print(f"✅ 已移動: {moved_count} 個檔案")
    print(f"⚠️  座標未找到: {not_found_count} 個檔案")
    print(f"❌ 失敗: {failed_count} 個檔案")
    print(f"📊 總計: {process_count} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    csv_path = r"h:\我的雲端硬碟\llm_wiki_travel\batch3_geocoding_sample.csv"
    classify_files(csv_path)
