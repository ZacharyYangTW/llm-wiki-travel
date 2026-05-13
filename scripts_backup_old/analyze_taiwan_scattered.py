#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import sys
import io
from pathlib import Path
from collections import defaultdict

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

def find_nearest_city(coords, county):
    """根據座標和縣市找到最近的城市（簡單實現）"""
    lng, lat = coords
    
    # 簡化版：根據座標範圍判斷
    # 這是一個粗略的實現，實際應該用更精確的地理資料庫
    
    # 台北市各區
    if county == '台北市':
        if lng >= 121.44 and lng <= 121.63 and lat >= 24.95 and lat <= 25.20:
            if lng >= 121.53 and lat >= 25.08:
                return '松山區' if lng >= 121.58 else '內湖區'
            return '大安區'
        return '中正區'
    
    # 其他縣市：返回主要城市（簡化版）
    return None

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')
taiwan_path = wiki_path / '台灣'

print("=" * 80)
print("掃描台灣散落檔案")
print("=" * 80)

scattered_by_county = defaultdict(list)

# 掃描所有散落檔案
for county_dir in sorted(taiwan_path.iterdir()):
    if not county_dir.is_dir() or county_dir.name.startswith('.'):
        continue
    
    county = county_dir.name
    
    # 檢查縣市下直接的檔案
    for md_file in county_dir.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            coords = extract_coordinates(content)
            
            if coords:
                city = find_nearest_city(coords, county)
                scattered_by_county[county].append({
                    'file': md_file.name,
                    'coords': coords,
                    'target_city': city if city else '待分類'
                })
        except:
            pass

# 顯示結果
for county in sorted(scattered_by_county.keys()):
    items = scattered_by_county[county]
    if items:
        print(f"\n{county} ({len(items)} 個):")
        for item in items[:3]:
            print(f"  • {item['file']}")
            print(f"    座標: {item['coords']}")
            if item['target_city'] != '待分類':
                print(f"    目標: {item['target_city']}")
        if len(items) > 3:
            print(f"  ... 還有 {len(items)-3} 個")

print("\n" + "=" * 80)
print(f"總計: {sum(len(v) for v in scattered_by_county.values())} 個散落檔案")
print("=" * 80)
