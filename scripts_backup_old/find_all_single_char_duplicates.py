#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描 Wiki 找出一字之差的重複目錄（包括第二級城市）
例如：拉薩 和 拉薩市、廣州 和 廣州市等
"""

import os
import sys
import difflib
from collections import defaultdict
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 用於配對的後綴字
SUFFIXES = ['市', '縣', '區', '州', '府']

def find_duplicates_in_directory(directory_path, level_name=""):
    """在一個目錄中找出一字之差的重複"""
    duplicates = []

    try:
        dirs = [d for d in os.listdir(directory_path)
                if os.path.isdir(os.path.join(directory_path, d))]
    except PermissionError:
        return duplicates

    # 比較每對目錄
    for i, dir1 in enumerate(dirs):
        for dir2 in dirs[i+1:]:
            # 檢查是否是一字之差
            if abs(len(dir1) - len(dir2)) <= 1:
                # 檢查是否一個是另一個加後綴
                for suffix in SUFFIXES:
                    if dir1 == dir2 + suffix or dir2 == dir1 + suffix:
                        # 找出哪個是短的（原版本）和長的（加了後綴的版本）
                        if len(dir1) < len(dir2):
                            short, long = dir1, dir2
                        else:
                            short, long = dir2, dir1

                        # 計算檔案數
                        short_path = os.path.join(directory_path, short)
                        long_path = os.path.join(directory_path, long)

                        short_count = len([f for f in os.listdir(short_path)
                                         if f.endswith('.md') and os.path.isfile(os.path.join(short_path, f))])
                        long_count = len([f for f in os.listdir(long_path)
                                        if f.endswith('.md') and os.path.isfile(os.path.join(long_path, f))])

                        if short_count > 0 or long_count > 0:
                            duplicates.append({
                                'short': short,
                                'long': long,
                                'short_count': short_count,
                                'long_count': long_count,
                                'level': level_name,
                            })
                        break

    return duplicates

print("=" * 80, flush=True)
print("🔍 掃描一字之差的重複目錄（第一級和第二級）", flush=True)
print("=" * 80, flush=True)

all_duplicates = defaultdict(list)

# 掃描所有國家及其子目錄
for country in sorted(os.listdir(WIKI_BASE)):
    country_path = os.path.join(WIKI_BASE, country)

    if not os.path.isdir(country_path):
        continue

    # 第一級：掃描國家下的子目錄
    duplicates = find_duplicates_in_directory(country_path, level_name=f"{country} (第一級)")

    if duplicates:
        all_duplicates[country] = duplicates

    # 第二級：掃描國家下每個子目錄的下一層
    try:
        subdirs = [d for d in os.listdir(country_path)
                   if os.path.isdir(os.path.join(country_path, d))]
    except PermissionError:
        continue

    for subdir in subdirs:
        subdir_path = os.path.join(country_path, subdir)
        level_name = f"{country}/{subdir} (第二級)"

        sub_duplicates = find_duplicates_in_directory(subdir_path, level_name=level_name)

        if sub_duplicates:
            key = f"{country}/{subdir}"
            all_duplicates[key] = sub_duplicates

if not all_duplicates:
    print("\n✅ 沒有找到一字之差的重複目錄", flush=True)
else:
    print(f"\n⚠️  找到 {sum(len(v) for v in all_duplicates.values())} 對一字之差的重複\n", flush=True)

    for location in sorted(all_duplicates.keys()):
        print(f"📍 {location}", flush=True)

        for dup in all_duplicates[location]:
            print(f"\n  {dup['short']:20s} ← → {dup['long']:20s}")
            print(f"  {dup['short_count']:2d} 個檔案    ← → {dup['long_count']:2d} 個檔案")
            print(f"  ➜ 建議：刪除 {dup['short']}，保留 {dup['long']} 並合併檔案")

print(f"\n{'='*80}", flush=True)
