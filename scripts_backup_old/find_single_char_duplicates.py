#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描 Wiki 找出一字之差的重複目錄
例如：拉薩 和 拉薩市、杭州 和 杭州市等
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

def find_duplicates_in_country(country_path):
    """在一個國家目錄中找出一字之差的重複"""
    duplicates = []

    dirs = [d for d in os.listdir(country_path)
            if os.path.isdir(os.path.join(country_path, d))]

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
                        short_path = os.path.join(country_path, short)
                        long_path = os.path.join(country_path, long)

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
                            })
                        break

    return duplicates

print("=" * 80, flush=True)
print("🔍 掃描一字之差的重複目錄", flush=True)
print("=" * 80, flush=True)

all_duplicates = defaultdict(list)

# 掃描所有國家
for country in sorted(os.listdir(WIKI_BASE)):
    country_path = os.path.join(WIKI_BASE, country)

    if not os.path.isdir(country_path):
        continue

    duplicates = find_duplicates_in_country(country_path)

    if duplicates:
        all_duplicates[country] = duplicates

if not all_duplicates:
    print("\n✅ 沒有找到一字之差的重複目錄", flush=True)
else:
    print(f"\n⚠️  找到 {sum(len(v) for v in all_duplicates.values())} 對一字之差的重複\n", flush=True)

    for country in sorted(all_duplicates.keys()):
        print(f"📍 {country}", flush=True)

        for dup in all_duplicates[country]:
            print(f"\n  {dup['short']:20s} ← → {dup['long']:20s}")
            print(f"  {dup['short_count']:2d} 個檔案    ← → {dup['long_count']:2d} 個檔案")
            print(f"  ➜ 建議：刪除 {dup['short']}，保留 {dup['long']} 並合併檔案")

print(f"\n{'='*80}", flush=True)
