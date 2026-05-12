#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理已驗證國家中，第一級城市是中文的資料夾而且是空的
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 已驗證的國家
VERIFIED_COUNTRIES = [
    '日本', '台灣', '中國', '美國', '泰國', '韓國',
    '馬來西亞', '法國', '菲律賓', '德國', '巴西',
    '澳洲', '印度', '埃及'
]

def is_chinese_folder_name(name):
    """檢查資料夾名是否是中文"""
    return all('一' <= char <= '鿿' for char in name)

def cleanup_country(country_name):
    """清理單個國家的空中文資料夾"""
    country_path = os.path.join(WIKI_BASE, country_name)

    if not os.path.isdir(country_path):
        return 0

    removed_count = 0

    # 遍歷第一級目錄（通常是州、省或地區）
    for division_name in os.listdir(country_path):
        division_path = os.path.join(country_path, division_name)

        if not os.path.isdir(division_path):
            continue

        # 遍歷第二級目錄（城市）
        for city_name in list(os.listdir(division_path)):
            city_path = os.path.join(division_path, city_name)

            if not os.path.isdir(city_path):
                continue

            # 檢查是否是中文資料夾
            if not is_chinese_folder_name(city_name):
                continue

            # 檢查是否為空
            if len(os.listdir(city_path)) == 0:
                try:
                    os.rmdir(city_path)
                    print(f"  ✓ 刪除: {country_name}/{division_name}/{city_name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ✗ 刪除失敗: {country_name}/{division_name}/{city_name} - {str(e)}")

    return removed_count

print("=" * 80)
print("🗑️  清理已驗證國家的空中文資料夾")
print("=" * 80)

total_removed = 0

for country_name in VERIFIED_COUNTRIES:
    print(f"\n🌍 {country_name}")
    removed = cleanup_country(country_name)
    if removed > 0:
        print(f"   共刪除: {removed} 個空資料夾")
    else:
        print(f"   無空資料夾")
    total_removed += removed

print(f"\n{'='*80}")
print(f"✅ 清理完成！")
print(f"   總共刪除: {total_removed} 個空資料夾")
print(f"{'='*80}")
