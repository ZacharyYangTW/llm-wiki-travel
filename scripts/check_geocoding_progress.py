#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查地理編碼進度
統計已分類/未分類的檔案數量
"""

import os
import sys
import io
from collections import defaultdict
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

def count_files_by_extension(directory, ext='.md'):
    """統計目錄中指定副檔名的檔案數量"""
    count = 0
    if os.path.isdir(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(ext):
                    count += 1
    return count

def scan_directory_structure(base_path):
    """掃描目錄結構並統計檔案"""
    structure = {}

    if not os.path.isdir(base_path):
        return structure

    for country in os.listdir(base_path):
        country_path = os.path.join(base_path, country)
        if os.path.isdir(country_path):
            file_count = count_files_by_extension(country_path)
            if file_count > 0 or country in ['未知', '其他']:
                structure[country] = {
                    'path': country_path,
                    'files': file_count,
                    'subdirs': 0
                }

                # 統計子目錄
                for item in os.listdir(country_path):
                    item_path = os.path.join(country_path, item)
                    if os.path.isdir(item_path):
                        structure[country]['subdirs'] += 1

    return structure

print("=" * 80)
print("📊 地理編碼進度檢查")
print("=" * 80)
print(f"\n執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Wiki 基礎路徑: {WIKI_BASE}\n")

# 掃描已分類目錄
print("="*80)
print("✅ 已分類的國家/地區")
print("="*80)

classified = scan_directory_structure(WIKI_BASE)
classified_files = 0
classified_countries = 0

# 排除未知和其他
exclude = {'未知', '其他'}
classified_display = {k: v for k, v in sorted(classified.items()) if k not in exclude}

for idx, (country, info) in enumerate(classified_display.items(), 1):
    print(f"[{idx:2d}] {country:<15} {info['files']:5d} 個檔案  {info['subdirs']:3d} 個子目錄")
    classified_files += info['files']
    classified_countries += 1

print(f"\n小計: {classified_countries:2d} 個國家/地區, {classified_files:5d} 個檔案")

# 掃描未分類目錄
print("\n" + "="*80)
print("⚠️  未分類的檔案")
print("="*80)

unknown_path = os.path.join(WIKI_BASE, "未知")
other_path = os.path.join(WIKI_BASE, "其他")

unknown_files = 0
other_files = 0

# 未知目錄
if os.path.isdir(unknown_path):
    unknown_files = count_files_by_extension(unknown_path)
    unknown_subdirs = len([d for d in os.listdir(unknown_path) if os.path.isdir(os.path.join(unknown_path, d))])
    print(f"未知: {unknown_files:5d} 個檔案  {unknown_subdirs:3d} 個子目錄")

# 其他目錄
if os.path.isdir(other_path):
    other_files = count_files_by_extension(other_path)
    other_subdirs = len([d for d in os.listdir(other_path) if os.path.isdir(os.path.join(other_path, d))])
    print(f"其他: {other_files:5d} 個檔案  {other_subdirs:3d} 個子目錄")

unclassified_files = unknown_files + other_files
print(f"\n小計: {unclassified_files:5d} 個檔案")

# 進度統計
print("\n" + "="*80)
print("📈 進度統計")
print("="*80)

total_files = classified_files + unclassified_files
if total_files > 0:
    classified_pct = (classified_files / total_files) * 100
    unclassified_pct = (unclassified_files / total_files) * 100
else:
    classified_pct = 0
    unclassified_pct = 0

print(f"\n總檔案數:      {total_files:6d} 個")
print(f"已分類:        {classified_files:6d} 個 ({classified_pct:5.1f}%)")
print(f"未分類:        {unclassified_files:6d} 個 ({unclassified_pct:5.1f}%)")

# 進度條
bar_length = 50
filled = int(bar_length * classified_pct / 100)
bar = '█' * filled + '░' * (bar_length - filled)
print(f"\n進度: [{bar}] {classified_pct:.1f}%")

# 最多檔案的國家/地區
print("\n" + "="*80)
print("🏆 檔案最多的前 10 個國家/地區")
print("="*80)

top_countries = sorted(classified_display.items(), key=lambda x: x[1]['files'], reverse=True)[:10]
for idx, (country, info) in enumerate(top_countries, 1):
    print(f"[{idx:2d}] {country:<20} {info['files']:5d} 個")

print("\n" + "="*80)
print("✅ 檢查完成")
print("="*80 + "\n")
