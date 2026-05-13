#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Phase 5: 韓國城市 English → 中文
KOREA_MAP = {
    'Busan': '釜山廣域市',
    'Daegu': '大邱廣域市',
    'Gangwon': '江原特別自治道',
    'Gwangju': '光州廣域市',
    'Gyeonggi': '京畿道',
    'Incheon': '仁川廣域市',
    'Jeju': '濟州特別自治道',
    'North Gyeongsang': '北慶尚道',
    'Seoul': '首爾特別市',
    'South Chungcheong': '南忠清道',
    'South Gyeongsang': '南慶尚道',
    'Ulsan': '蔚山廣域市',
}

# Phase 6: 其他國家城市 English → 中文
OTHER_COUNTRIES_MAP = {
    '澳洲': {
        'New South Wales': '新南威爾斯州',
        'Tasmania': '塔斯馬尼亞州',
        'Victoria': '維多利亞州',
        'Western Australia': '西澳大利亞州',
        'Queensland': '昆士蘭州',
        'South Australia': '南澳大利亞州',
        'Australian Capital Territory': '澳大利亞首都地區',
        'Northern Territory': '北領地',
    },
    '奧地利': {
        'Salzburg': '薩爾斯堡',
        'Vienna': '維也納',
        'Hallstatt': '哈爾施塔特',
    },
    '捷克': {
        'Prague': '布拉格',
        'South Moravia': '南摩拉維亞州',
    },
    '印尼': {
        'Batam': '巴淡',
    },
    '西班牙': {
        'Catalonia': '加泰隆尼亞',
        'Madrid': '馬德里',
    },
}

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

print("=" * 80)
print("Phase 5 & 6: 城市名稱標準化 (English → 中文)")
print("=" * 80)

def move_and_merge(src_path, dst_path, src_name, dst_name):
    """移動源目錄到目標，如果目標已存在則合併"""
    if not src_path.exists():
        return False

    if dst_path.exists():
        # 合併：將源目錄中的文件移到目標
        for md_file in src_path.glob('*.md'):
            target_file = dst_path / md_file.name
            if not target_file.exists():
                shutil.move(str(md_file), str(target_file))
            else:
                print(f"  ⚠️ 重複: {dst_name}/{md_file.name}")
        # 刪除空的源目錄
        if not any(src_path.glob('*.md')):
            src_path.rmdir()
    else:
        # 直接重命名
        shutil.move(str(src_path), str(dst_path))

    return True

# Phase 5: 韓國
print("\n[Phase 5] 韓國城市 English → 中文:")
print("-" * 80)

korea_path = wiki_path / '韓國'
if korea_path.exists():
    for eng_name, chi_name in KOREA_MAP.items():
        src = korea_path / eng_name
        dst = korea_path / chi_name

        if src.exists():
            count = len(list(src.glob('*.md')))
            if move_and_merge(src, dst, eng_name, chi_name):
                print(f"✅ {eng_name} → {chi_name} ({count} 個檔案)")
            else:
                print(f"❌ {eng_name}: 移動失敗")
        else:
            print(f"⚠️ {eng_name}: 目錄不存在")

# Phase 6: 其他國家
print("\n[Phase 6] 其他國家城市 English → 中文:")
print("-" * 80)

for country, city_map in OTHER_COUNTRIES_MAP.items():
    country_path = wiki_path / country
    print(f"\n{country}:")

    if country_path.exists():
        for eng_name, chi_name in city_map.items():
            src = country_path / eng_name
            dst = country_path / chi_name

            if src.exists():
                count = len(list(src.glob('*.md')))
                if move_and_merge(src, dst, eng_name, chi_name):
                    print(f"  ✅ {eng_name} → {chi_name} ({count} 個檔案)")
                else:
                    print(f"  ❌ {eng_name}: 移動失敗")
            else:
                print(f"  ⚠️ {eng_name}: 目錄不存在")
    else:
        print(f"  ❌ {country}: 國家目錄不存在")

print("\n" + "=" * 80)
print("標準化完成")
print("=" * 80)
