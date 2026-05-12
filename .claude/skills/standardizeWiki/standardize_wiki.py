#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki 標準化腳本：修正簡繁體、一字之差重複、日本繁體字、相似目錄等
"""

import os
import sys
import shutil
import difflib
from collections import defaultdict
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 簡體字→繁體字映射（完整詞組級別，避免誤判）
SIMPLIFIED_CITIES = {
    "兰州": "蘭州",
    "兰州市": "蘭州市",
    "苏州": "蘇州",
    "苏州市": "蘇州市",
    "贵阳": "貴陽",
    "贵阳市": "貴陽市",
    "云浮": "雲浮",
    "云浮市": "雲浮市",
    "宁夏": "寧夏",
    "宁波": "寧波",
    "肃州": "肅州",
    "陕西": "陝西",
    "陕西省": "陝西省",
    "辽宁": "遼寧",
    "辽宁省": "遼寧省",
}

# 一字之差後綴
SUFFIXES = ['市', '縣', '區', '州', '府']

# 日本繁體字→日文漢字映射（部分例子）
JAPANESE_TRADITIONAL_MAP = {
    "东京都": "東京都",
    "大阪府": "大阪府",
    "京都府": "京都府",
    "奈良県": "奈良県",
    "兵库県": "兵庫県",
    "滋贺県": "滋賀県",
    "三重県": "三重県",
    "爱知県": "愛知県",
    "岐阜県": "岐阜県",
    "长野県": "長野県",
    "新泻県": "新潟県",
    "山梨県": "山梨県",
    "富山県": "富山県",
    "石川県": "石川県",
    "福井県": "福井県",
    "福冈県": "福岡縣",
}

def check_simplified_and_convert(name):
    """檢查是否包含簡體字並返回繁體版本，如無簡體字返回 None"""
    for simplified, traditional in SIMPLIFIED_CITIES.items():
        if simplified in name:
            return name.replace(simplified, traditional)
    return None

def is_similar(s1, s2, threshold=0.8):
    """檢查兩個字符串是否相似"""
    if abs(len(s1) - len(s2)) > 5:
        return False
    ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
    return ratio >= threshold

def find_issues():
    """掃描並找出所有命名問題"""
    issues = {
        'simplified': [],      # 簡體字
        'single_char': [],     # 一字之差
        'similar': [],         # 相似目錄
        'japan_traditional': [] # 日本繁體字
    }

    # 掃描每個國家
    for country in os.listdir(WIKI_BASE):
        country_path = os.path.join(WIKI_BASE, country)
        if not os.path.isdir(country_path):
            continue

        # 掃描一級目錄
        level1_dirs = [d for d in os.listdir(country_path)
                      if os.path.isdir(os.path.join(country_path, d))]

        # 檢查簡體字
        for dir_name in level1_dirs:
            traditional = check_simplified_and_convert(dir_name)
            if traditional:
                issues['simplified'].append({
                    'country': country,
                    'current': dir_name,
                    'target': traditional,
                    'level': 1
                })

        # 檢查一字之差重複（一級）
        for i, dir1 in enumerate(level1_dirs):
            for dir2 in level1_dirs[i+1:]:
                if abs(len(dir1) - len(dir2)) <= 1:
                    for suffix in SUFFIXES:
                        if dir1 == dir2 + suffix or dir2 == dir1 + suffix:
                            short = dir1 if len(dir1) < len(dir2) else dir2
                            long = dir2 if len(dir1) < len(dir2) else dir1

                            short_files = len([f for f in os.listdir(os.path.join(country_path, short))
                                             if f.endswith('.md')])
                            long_files = len([f for f in os.listdir(os.path.join(country_path, long))
                                            if f.endswith('.md')])

                            if short_files > 0 or long_files > 0:
                                issues['single_char'].append({
                                    'country': country,
                                    'short': short,
                                    'long': long,
                                    'short_files': short_files,
                                    'long_files': long_files,
                                    'level': 1
                                })

        # 掃描二級目錄
        for level1 in level1_dirs:
            level1_path = os.path.join(country_path, level1)
            level2_dirs = [d for d in os.listdir(level1_path)
                          if os.path.isdir(os.path.join(level1_path, d))]

            # 檢查簡體字
            for dir_name in level2_dirs:
                traditional = check_simplified_and_convert(dir_name)
                if traditional:
                    issues['simplified'].append({
                        'country': country,
                        'parent': level1,
                        'current': dir_name,
                        'target': traditional,
                        'level': 2
                    })

            # 檢查一字之差重複（二級）
            for i, dir1 in enumerate(level2_dirs):
                for dir2 in level2_dirs[i+1:]:
                    if abs(len(dir1) - len(dir2)) <= 1:
                        for suffix in SUFFIXES:
                            if dir1 == dir2 + suffix or dir2 == dir1 + suffix:
                                short = dir1 if len(dir1) < len(dir2) else dir2
                                long = dir2 if len(dir1) < len(dir2) else dir1

                                short_path = os.path.join(level1_path, short)
                                long_path = os.path.join(level1_path, long)

                                short_files = len([f for f in os.listdir(short_path)
                                                 if f.endswith('.md')])
                                long_files = len([f for f in os.listdir(long_path)
                                                if f.endswith('.md')])

                                if short_files > 0 or long_files > 0:
                                    issues['single_char'].append({
                                        'country': country,
                                        'parent': level1,
                                        'short': short,
                                        'long': long,
                                        'short_files': short_files,
                                        'long_files': long_files,
                                        'level': 2
                                    })

    return issues

print("=" * 80, flush=True)
print("🔍 掃描 Wiki 命名標準化問題", flush=True)
print("=" * 80, flush=True)

issues = find_issues()

# 輸出簡體字問題
if issues['simplified']:
    print(f"\n⚠️  發現 {len(issues['simplified'])} 個簡體字目錄", flush=True)
    for issue in issues['simplified']:
        if 'parent' in issue:
            print(f"  {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)
        else:
            print(f"  {issue['country']}/{issue['current']} → {issue['target']}", flush=True)

# 輸出一字之差重複
if issues['single_char']:
    print(f"\n⚠️  發現 {len(issues['single_char'])} 個一字之差重複", flush=True)
    for issue in issues['single_char']:
        if 'parent' in issue:
            print(f"  {issue['country']}/{issue['parent']}/{issue['short']} ({issue['short_files']}) + {issue['long']} ({issue['long_files']}) → {issue['long']}", flush=True)
        else:
            print(f"  {issue['country']}/{issue['short']} ({issue['short_files']}) + {issue['long']} ({issue['long_files']}) → {issue['long']}", flush=True)

print(f"\n{'='*80}", flush=True)
print(f"✅ 掃描完成", flush=True)
print(f"{'='*80}", flush=True)
