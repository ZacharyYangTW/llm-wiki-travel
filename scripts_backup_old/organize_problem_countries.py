#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理有問題的國家：印度、埃及、奧地利、捷克、智利
將直接檔案根據坐標移到城市子目錄
無法判斷的留在根目錄，列出清單供人工檢查
"""

import os
import sys
import re
import shutil
import math
from pathlib import Path
from collections import defaultdict
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 各國的城市中心坐標
CITY_CENTERS = {
    '印度': {
        '德里': (77.1025, 28.6139),
        '孟買': (72.8479, 19.0760),
        '加爾各答': (88.3639, 22.5726),
        '清奈': (80.2809, 13.0827),
    },
    '埃及': {
        '開羅': (31.2357, 30.0444),
        '亞斯文': (32.8872, 24.0881),
        '路克索': (32.6421, 25.6872),
        '蓋亞拉': (30.8755, 27.0845),
        '貝拉特': (31.3157, 30.4779),
    },
    '奧地利': {
        '維也納': (16.3738, 48.2082),
        '薩爾茨堡': (13.0550, 47.8095),
        '伊施爾': (13.6192, 47.7197),
        '哈爾施塔特': (13.6490, 47.5329),
        '哈萊因': (14.4167, 48.3167),
    },
    '捷克': {
        '布拉格': (14.4378, 50.0755),
        '卡羅維瓦利': (12.8742, 50.2334),
        '庫倫洛夫': (14.1550, 48.8129),
    },
    '智利': {
        '聖地亞哥': (-70.6693, -33.4489),
        '復活節島': (-109.3667, -27.1167),
        '漢加羅亞': (-109.2963, -27.1452),
        '普達烏埃爾': (-70.1894, -33.7500),
    },
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def extract_coordinates(md_file):
    """從 .md 檔案提取坐標"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(COORD_PATTERN, content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return lng, lat
    except:
        pass
    return None, None

def find_nearest_city(lng, lat, country):
    """根據坐標找最近的城市"""
    if country not in CITY_CENTERS:
        return None

    cities = CITY_CENTERS[country]
    min_dist = float('inf')
    nearest_city = None

    for city_name, (c_lng, c_lat) in cities.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            nearest_city = city_name

    # 只有距離小於 10 度才認為可靠
    if min_dist < 10:
        return nearest_city

    return None

def organize_country(country_name):
    """整理一個國家的檔案"""
    country_path = os.path.join(WIKI_BASE, country_name)

    if not os.path.exists(country_path):
        print(f"❌ {country_name}: 目錄不存在", flush=True)
        return

    # 列出根目錄的 .md 檔案
    root_files = [f for f in os.listdir(country_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(country_path, f))]

    if not root_files:
        print(f"✓ {country_name}: 沒有根目錄直接檔案", flush=True)
        return

    print(f"\n{'='*70}", flush=True)
    print(f"🔧 整理 {country_name} ({len(root_files)} 個檔案)", flush=True)
    print(f"{'='*70}", flush=True)

    moved_count = 0
    failed_list = []

    for filename in root_files:
        file_path = os.path.join(country_path, filename)
        title = filename[:-3]  # 去掉 .md

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            failed_list.append((filename, "無坐標"))
            continue

        # 找最近的城市
        city = find_nearest_city(lng, lat, country_name)

        if not city:
            failed_list.append((filename, f"距離遠 ({lng:.2f}, {lat:.2f})"))
            continue

        # 移動檔案
        try:
            city_dir = os.path.join(country_path, city)
            os.makedirs(city_dir, exist_ok=True)
            target_file = os.path.join(city_dir, filename)

            shutil.move(file_path, target_file)
            moved_count += 1
            print(f"✓ {title[:40]:<40} → {city}", flush=True)

        except Exception as e:
            failed_list.append((filename, f"移動失敗: {str(e)[:30]}"))

    print(f"\n✅ {country_name} 完成：", flush=True)
    print(f"  成功移動: {moved_count} 個", flush=True)
    print(f"  無法判斷: {len(failed_list)} 個", flush=True)

    # 輸出無法判斷的檔案清單
    if failed_list:
        print(f"\n⚠️  無法判斷的檔案（保留在根目錄）：", flush=True)
        for filename, reason in failed_list[:10]:
            print(f"  - {filename[:50]:<50} ({reason})", flush=True)
        if len(failed_list) > 10:
            print(f"  ... 及其他 {len(failed_list)-10} 個", flush=True)

    return moved_count, len(failed_list)

# 主程序
print("=" * 70, flush=True)
print("🔧 整理有問題的國家", flush=True)
print("=" * 70, flush=True)

countries = ['印度', '埃及', '奧地利', '捷克', '智利']

total_moved = 0
total_failed = 0

for country in countries:
    moved, failed = organize_country(country)
    if moved is not None:
        total_moved += moved
        total_failed += failed

print(f"\n{'='*70}", flush=True)
print(f"📊 全部完成！", flush=True)
print(f"  總共移動: {total_moved} 個", flush=True)
print(f"  待人工檢查: {total_failed} 個", flush=True)
print(f"{'='*70}", flush=True)
