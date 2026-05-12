#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描瑞芳區檔案，識別並移動日本景點到對應日本目錄
"""

import os
import sys
import shutil
import re
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
RUIFANG_PATH = os.path.join(WIKI_BASE, "台灣", "新北市", "瑞芳區")

# 導入日本市町村座標表
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

def extract_metadata(file_path):
    """從 frontmatter 提取座標和國家"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # 提取坐標
            coords = None
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                coords = (float(match.group(1)), float(match.group(2)))

            # 提取國家
            country = None
            match = re.search(r'country:\s*([^\n]+)', content)
            if match:
                country = match.group(1).strip()

            return coords, country
    except:
        pass
    return None, None

def is_japan_coords(lng, lat):
    """判斷座標是否在日本"""
    # 日本大致在 130-145E, 30-45N
    return 130 <= lng <= 145 and 30 <= lat <= 46

print("=" * 80)
print("🔍 掃描瑞芳區 - 識別日本景點")
print("=" * 80)

japan_files = []
taiwan_files = []

for file_name in sorted(os.listdir(RUIFANG_PATH)):
    file_path = os.path.join(RUIFANG_PATH, file_name)
    if not os.path.isfile(file_path) or not file_name.endswith('.md'):
        continue

    coords, country = extract_metadata(file_path)

    print(f"\n📄 {file_name}")
    print(f"   座標: {coords}")
    print(f"   國家: {country}")

    # 判斷是否為日本景點
    is_japan = False
    if country == "日本":
        is_japan = True
    elif coords and is_japan_coords(coords[0], coords[1]):
        is_japan = True

    if is_japan:
        if coords:
            # 根據座標找到最接近的都道府縣和市町村
            # 使用廣域搜索（按照緯度找到對應的都道府縣）
            pref = None
            nearest_town = None

            # 簡單的緯度到都道府縣的映射
            lat = coords[1]
            if 36.1 <= lat <= 36.3 and 136.8 <= coords[0] <= 137.1:
                # 這是岐阜縣（白川村所在）
                pref = "岐阜県"
                nearest_town = get_nearest_town(coords, pref)
            elif 39.6 <= lat <= 40.6 and 139.4 <= coords[0] <= 141.5:
                # 這可能是青森縣附近
                pref = "青森県"
                if pref in JAPAN_TOWNS_COORDS:
                    nearest_town = get_nearest_town(coords, pref)
            else:
                # 嘗試在所有都道府縣中找
                for p in JAPAN_TOWNS_COORDS.keys():
                    t = get_nearest_town(coords, p)
                    if t:
                        pref = p
                        nearest_town = t
                        break

            if pref and nearest_town:
                japan_files.append({
                    'file': file_name,
                    'path': file_path,
                    'coords': coords,
                    'pref': pref,
                    'city': nearest_town
                })
                print(f"   ✓ 日本景點 → {pref}/{nearest_town}")
            else:
                print(f"   ✗ 日本坐標但找不到對應位置")
        else:
            print(f"   ✗ 日本景點但沒有座標")
    else:
        taiwan_files.append(file_name)
        print(f"   ✓ 台灣景點")

print(f"\n{'='*80}")
print(f"📊 掃描結果")
print(f"  日本景點: {len(japan_files)} 個")
print(f"  台灣景點: {len(taiwan_files)} 個")
print(f"{'='*80}")

if japan_files:
    print(f"\n🔧 開始移動日本景點...\n")

    moved = 0
    errors = []

    for item in japan_files:
        pref_path = os.path.join(WIKI_BASE, "日本", item['pref'])
        city_path = os.path.join(pref_path, item['city'])

        # 確保目錄存在
        os.makedirs(city_path, exist_ok=True)

        dst_path = os.path.join(city_path, item['file'])

        try:
            shutil.move(item['path'], dst_path)
            moved += 1
            print(f"✓ {item['file'][:40]:40} → {item['pref']}/{item['city']}/")
        except Exception as e:
            errors.append(f"{item['file']}: {str(e)}")
            print(f"✗ {item['file']}: {str(e)}")

    print(f"\n{'='*80}")
    print(f"✅ 完成")
    print(f"  移動: {moved} 個檔案")
    if errors:
        print(f"  錯誤: {len(errors)} 個")
    print(f"{'='*80}")
