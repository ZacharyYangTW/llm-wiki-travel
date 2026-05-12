#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 Wiki 目錄命名規則，將非中日台國家的目錄改為英文
規則：除了中國、日本、台灣外，其他所有國家都使用英文目錄名
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 需要改回英文的目錄映射 (中文 -> English)
RENAME_MAPPING = {
    # 秘魯
    '秘魯': {
        '阿雷基帕': 'Arequipa',
        '卡哈馬卡': 'Cajamarca',
        '庫斯科': 'Cusco',
        '伊卡': 'Ica',
        '利馬': 'Lima',
        '特魯希略': 'Trujillo',
    },
    # 越南
    '越南': {
        '河內': 'Hanoi',
        '胡志明市': 'Ho Chi Minh City',
        '峴港': 'Da Nang',
        '海防': 'Hai Phong',
        '同奈省': 'Dong Nai',
        '河江省': 'Ha Giang',
        '隆安省': 'Long An',
        '南定省': 'Nam Dinh',
        '廣南省': 'Quang Nam',
        '廣寧省': 'Quang Ninh',
        '西寧省': 'Tay Ninh',
        '清化省': 'Thanh Hoa',
        '前江省': 'Tien Giang',
    }
}

print("=" * 100)
print("Wiki 目錄命名規則修正：改為英文目錄名")
print("=" * 100)
print("\n規則：除了中國、日本、台灣外，其他所有國家都使用英文目錄名\n")

total_renamed = 0
total_failed = 0

for country, city_mapping in RENAME_MAPPING.items():
    country_path = os.path.join(WIKI_BASE, country)

    if not os.path.isdir(country_path):
        print(f"⚠️  {country} 目錄不存在")
        continue

    print(f"\n{'='*100}")
    print(f"{country}")
    print(f"{'='*100}\n")

    for cn_city, en_city in city_mapping.items():
        cn_path = os.path.join(country_path, cn_city)
        en_path = os.path.join(country_path, en_city)

        if not os.path.isdir(cn_path):
            continue

        # 如果英文目錄已存在，需要合併
        if os.path.isdir(en_path):
            print(f"⚠️  {en_city} 目錄已存在，合併 {cn_city} 到 {en_city}")
            # 簡單起見，刪除重複的中文目錄（假設檔案已合併）
            try:
                # 首先檢查中文目錄是否為空
                if not os.listdir(cn_path):
                    os.rmdir(cn_path)
                    print(f"  ✓ 已刪除空的 {cn_city} 目錄")
                    total_renamed += 1
                else:
                    print(f"  ❌ {cn_city} 目錄非空，需要手動處理")
                    total_failed += 1
            except Exception as e:
                print(f"  ✗ 刪除失敗: {e}")
                total_failed += 1
        else:
            # 直接重新命名
            try:
                os.rename(cn_path, en_path)
                print(f"✓ {cn_city} → {en_city}")
                total_renamed += 1
            except Exception as e:
                print(f"✗ 重新命名失敗: {cn_city} → {en_city}")
                print(f"  錯誤: {e}")
                total_failed += 1

print(f"\n{'='*100}")
print("✅ 修正完成！")
print(f"  已重新命名: {total_renamed} 個目錄")
print(f"  失敗或需手動處理: {total_failed} 個")
print(f"{'='*100}\n")
