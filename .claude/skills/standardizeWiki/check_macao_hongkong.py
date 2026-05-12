#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import io
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\中國"

def extract_coordinates(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                return (float(match.group(1)), float(match.group(2)))
    except:
        pass
    return None

print("澳門和香港的檔案分佈:\n")

macao_files = defaultdict(list)
hongkong_files = defaultdict(list)

for prov_name in sorted(os.listdir(WIKI_BASE)):
    prov_path = os.path.join(WIKI_BASE, prov_name)
    if not os.path.isdir(prov_path):
        continue

    for city_name in sorted(os.listdir(prov_path)):
        city_path = os.path.join(prov_path, city_name)

        if city_name.endswith('.md'):
            continue

        if os.path.isdir(city_path):
            for file_name in os.listdir(city_path):
                if file_name.endswith('.md'):
                    file_path = os.path.join(city_path, file_name)
                    coords = extract_coordinates(file_path)

                    if coords:
                        lng, lat = coords
                        # 澳門座標 (113.5, 22.1-22.2)
                        if 113.5 <= lng <= 113.6 and 22.0 <= lat <= 22.2:
                            macao_files[f"{prov_name}/{city_name}"].append(file_name)
                        # 香港座標 (114.1-114.2, 22.2-22.4)
                        elif 114.0 <= lng <= 114.2 and 22.2 <= lat <= 22.4:
                            hongkong_files[f"{prov_name}/{city_name}"].append(file_name)

print("澳門檔案:")
if macao_files:
    total = sum(len(v) for v in macao_files.values())
    print(f"   總計: {total} 個")
    for location, files in sorted(macao_files.items()):
        print(f"   {location}: {len(files)} 個")
else:
    print("   無")

print("\n香港檔案:")
if hongkong_files:
    total = sum(len(v) for v in hongkong_files.values())
    print(f"   總計: {total} 個")
    for location, files in sorted(hongkong_files.items()):
        print(f"   {location}: {len(files)} 個")
else:
    print("   無")

# 顯示原澳門和香港目錄狀態
print("\n原澳門和香港目錄狀態:")
for name in ["澳門", "香港"]:
    path = os.path.join(WIKI_BASE, name)
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.md')]
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        print(f"   {name}: {len(files)} 個檔案, {len(dirs)} 個子目錄")
    else:
        print(f"   {name}: 目錄不存在")
