#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描 Wiki 並找出高度相似的目錄對
使用 Levenshtein 距離計算相似度
"""

import os
import sys
import difflib
from collections import defaultdict
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

def string_similarity(a, b):
    """計算兩個字符串的相似度 (0-1)"""
    return difflib.SequenceMatcher(None, a, b).ratio()

def find_similar_dirs(threshold=0.7):
    """找出所有高度相似的目錄對"""

    results = defaultdict(list)

    # 掃描所有國家
    for country in sorted(os.listdir(WIKI_BASE)):
        country_path = os.path.join(WIKI_BASE, country)

        if not os.path.isdir(country_path):
            continue

        # 列出該國家的所有城市目錄
        cities = [d for d in os.listdir(country_path)
                 if os.path.isdir(os.path.join(country_path, d))]

        if not cities:
            continue

        # 比較城市名稱
        similar_pairs = []
        for i, city1 in enumerate(cities):
            for city2 in cities[i+1:]:
                similarity = string_similarity(city1, city2)
                if similarity >= threshold and city1 != city2:
                    # 計算檔案數
                    path1 = os.path.join(country_path, city1)
                    path2 = os.path.join(country_path, city2)

                    count1 = len([f for f in os.listdir(path1)
                                 if f.endswith('.md') and os.path.isfile(os.path.join(path1, f))])
                    count2 = len([f for f in os.listdir(path2)
                                 if f.endswith('.md') and os.path.isfile(os.path.join(path2, f))])

                    if count1 > 0 or count2 > 0:
                        similar_pairs.append({
                            'city1': city1,
                            'city2': city2,
                            'similarity': similarity,
                            'count1': count1,
                            'count2': count2,
                        })

        if similar_pairs:
            results[country] = similar_pairs

    return results

print("=" * 80, flush=True)
print("🔍 掃描 Wiki 中的相似目錄", flush=True)
print("=" * 80, flush=True)

similar = find_similar_dirs(threshold=0.7)

if not similar:
    print("\n✅ 沒有找到高度相似的目錄對（相似度 >= 70%）", flush=True)
else:
    for country in sorted(similar.keys()):
        print(f"\n📍 {country} ({len(similar[country])} 對)", flush=True)

        for pair in sorted(similar[country], key=lambda x: x['similarity'], reverse=True):
            similarity_percent = int(pair['similarity'] * 100)
            print(f"\n  {pair['city1']:20s} ← → {pair['city2']:20s}")
            print(f"    相似度: {similarity_percent}% | 檔案數: {pair['count1']:2d} ← → {pair['count2']:2d}")

print(f"\n{'='*80}", flush=True)
