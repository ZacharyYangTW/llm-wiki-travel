#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理已驗證國家中，所有空的中文資料夾（第一級和第二級）
"""

import os
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 已驗證的國家（第一梯隊 + 第二梯隊）
VERIFIED_COUNTRIES = [
    '日本', '台灣', '中國', '美國', '泰國', '韓國',
    '馬來西亞', '法國', '菲律賓', '德國', '巴西',
    '澳洲', '印度', '埃及',
    '越南', '荷蘭', '西班牙', '奧地利', '紐西蘭', '新加坡', '加拿大',
    '匈牙利', '秘魯', '捷克', '柬埔寨', '智利', '比利時', '盧森堡', '印尼'
]

def is_chinese(text):
    """檢查字串是否包含中文"""
    for char in text:
        if '一' <= char <= '鿿':
            return True
    return False

def is_purely_chinese(text):
    """檢查字串是否純中文（除了空格和符號）"""
    chinese_chars = [char for char in text if '一' <= char <= '鿿']
    if not chinese_chars:
        return False
    return len(chinese_chars) == len([char for char in text if not char.isspace()])

def cleanup_empty_folders(country_path, country_name):
    """清理指定國家路徑下的所有空中文資料夾"""
    removed_count = 0

    if not os.path.isdir(country_path):
        return 0

    # 先清理第二級（城市）資料夾
    for division_name in list(os.listdir(country_path)):
        division_path = os.path.join(country_path, division_name)

        if not os.path.isdir(division_path):
            continue

        # 遍歷第二級目錄（城市）
        for city_name in list(os.listdir(division_path)):
            city_path = os.path.join(division_path, city_name)

            if not os.path.isdir(city_path):
                continue

            # 檢查是否是中文資料夾
            if not is_purely_chinese(city_name):
                continue

            # 檢查是否為空
            if len(os.listdir(city_path)) == 0:
                try:
                    os.rmdir(city_path)
                    print(f"  ✓ 刪除空資料夾: {division_name}/{city_name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ✗ 刪除失敗: {division_name}/{city_name}")

    # 再清理第一級（州/省/地區）資料夾（如果為空）
    for division_name in list(os.listdir(country_path)):
        division_path = os.path.join(country_path, division_name)

        if not os.path.isdir(division_path):
            continue

        # 只清理中文名且為空的資料夾
        if is_purely_chinese(division_name) and len(os.listdir(division_path)) == 0:
            try:
                os.rmdir(division_path)
                print(f"  ✓ 刪除空資料夾: {division_name}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ 刪除失敗: {division_name}")

    return removed_count

print("=" * 80)
print("🗑️  清理已驗證國家的所有空中文資料夾")
print("=" * 80)

total_removed = 0
details_by_country = {}

for country_name in VERIFIED_COUNTRIES:
    country_path = os.path.join(WIKI_BASE, country_name)

    print(f"\n🌍 {country_name}")
    removed = cleanup_empty_folders(country_path, country_name)

    if removed > 0:
        print(f"   共刪除: {removed} 個空資料夾")
        details_by_country[country_name] = removed
    else:
        print(f"   無空資料夾")

    total_removed += removed

print(f"\n{'='*80}")
print(f"✅ 清理完成！")
print(f"   總共刪除: {total_removed} 個空資料夾")

if details_by_country:
    print(f"\n📊 清理詳情：")
    for country, count in sorted(details_by_country.items(), key=lambda x: x[1], reverse=True):
        print(f"   {country}: {count} 個")

print(f"{'='*80}")
