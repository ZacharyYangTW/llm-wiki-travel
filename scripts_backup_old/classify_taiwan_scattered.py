#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import sys
import io
from pathlib import Path
from collections import defaultdict
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_coordinates(md_content):
    """提取座標"""
    match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', md_content)
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except:
            return None
    return None

# 台灣主要城市座標（鄉鎮市區中心）
TAIWAN_CITIES = {
    '台北市': {
        '中正區': (121.5086, 25.0319),
        '大安區': (121.5332, 25.0330),
        '松山區': (121.5766, 25.0447),
        '信義區': (121.5686, 25.0333),
    },
    '新北市': {
        '中和區': (121.4930, 24.9929),
        '永和區': (121.5120, 24.9847),
        '三重區': (121.4846, 25.0628),
        '新莊區': (121.4327, 25.0646),
    },
    '基隆市': {
        '中正區': (121.7393, 25.1357),
        '七堵區': (121.7359, 25.0816),
        '仁愛區': (121.6761, 25.1252),
    },
    '台南市': {
        '中西區': (120.2037, 22.9965),
        '東區': (120.2163, 22.9819),
        '安平區': (120.1645, 23.0629),
    },
    '台東縣': {
        '台東市': (121.1501, 22.7561),
        '卑南鄉': (121.1032, 22.6772),
    },
    '花蓮縣': {
        '花蓮市': (121.5902, 23.9868),
        '吉安鄉': (121.5494, 23.9306),
    },
    '桃園市': {
        '桃園區': (121.3155, 25.0044),
        '中壢區': (121.2181, 24.9629),
    },
    '新竹市': {
        '東區': (120.9880, 24.8072),
        '北區': (121.0101, 24.8318),
    },
    '彰化縣': {
        '彰化市': (120.5386, 24.0799),
        '鹿港鎮': (120.4334, 24.0603),
    },
    '苗栗縣': {
        '大湖鄉': (120.8689, 24.4279),
        '苗栗市': (120.8218, 24.5664),
    },
    '高雄市': {
        '左營區': (120.3092, 22.6880),
        '前金區': (120.2880, 22.6307),
    },
}

def find_nearest_city(coords, county):
    """找到最近的城市"""
    if county not in TAIWAN_CITIES:
        return None
    
    lng, lat = coords
    cities = TAIWAN_CITIES[county]
    
    min_dist = float('inf')
    nearest = None
    
    for city, (city_lng, city_lat) in cities.items():
        dist = math.sqrt((lng - city_lng)**2 + (lat - city_lat)**2)
        if dist < min_dist:
            min_dist = dist
            nearest = city
    
    return nearest

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
taiwan_path = wiki_path / '台灣'

print("=" * 80)
print("分類台灣散落檔案到各鄉鎮市區")
print("=" * 80)

moved = 0

# 掃描並移動
for county_dir in sorted(taiwan_path.iterdir()):
    if not county_dir.is_dir() or county_dir.name.startswith('.'):
        continue
    
    county = county_dir.name
    
    # 檢查縣市下直接的檔案
    files = list(county_dir.glob('*.md'))
    
    for md_file in files:
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)
            
            if coords:
                city = find_nearest_city(coords, county)
                
                if city:
                    # 建立目標目錄
                    target_dir = county_dir / city
                    target_dir.mkdir(exist_ok=True)
                    
                    # 移動檔案
                    target_file = target_dir / md_file.name
                    shutil.move(str(md_file), str(target_file))
                    
                    print(f"  ✓ {county}/{city}: {md_file.name}")
                    moved += 1
                else:
                    print(f"  ⚠️ {county}: {md_file.name} - 無法判斷城市")
        except Exception as e:
            print(f"  ❌ {md_file.name}: {e}")

print(f"\n" + ("=" * 80))
print(f"完成: 移動 {moved} 個檔案")
print("=" * 80)
