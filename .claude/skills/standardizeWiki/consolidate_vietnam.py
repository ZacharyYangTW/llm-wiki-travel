#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整併越南 Hanoi 和河內，統一越南城市名為繁體中文
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 英文城市名 -> 繁體中文城市名對應
CITY_MAPPING = {
    'Hanoi': '河內',
    'Ho Chi Minh City': '胡志明市',
    'Da Nang': '峴港',
    'Hai Phong': '海防',
    'Can Tho': '芹苴',
    'Da Lat': '大叻',
    'Hue': '順化',
    'Hoi An': '會安',
    'Nha Trang': '芽莊',
    'Phan Rang': '潘蘭',
    'Dong Nai': '同奈省',
    'Ha Giang': '河江省',
    'Long An': '隆安省',
    'Nam Dinh': '南定省',
    'Quang Nam': '廣南省',
    'Quang Ninh': '廣寧省',
    'Tay Ninh': '西寧省',
    'Thanh Hoa': '清化省',
    'Tien Giang': '前江省',
}

print("=" * 100)
print("整併越南 Hanoi 和河內，統一城市名為繁體中文")
print("=" * 100)

vietnam_path = os.path.join(WIKI_BASE, '越南')

if not os.path.isdir(vietnam_path):
    print("越南目錄不存在")
    sys.exit(1)

print("\nStep 1: 整併 Hanoi 和河內\n")

hanoi_path = os.path.join(vietnam_path, 'Hanoi')
henanei_path = os.path.join(vietnam_path, '河內')

if os.path.isdir(hanoi_path):
    os.makedirs(henanei_path, exist_ok=True)

    # 合併 Hanoi 的檔案到河內
    for file in os.listdir(hanoi_path):
        src = os.path.join(hanoi_path, file)
        dst = os.path.join(henanei_path, file)

        if os.path.isfile(src):
            try:
                shutil.move(src, dst)
                print(f"✓ 已合併: {file}")
            except Exception as e:
                print(f"✗ 合併失敗: {file} - {e}")

    # 刪除 Hanoi 目錄
    try:
        os.rmdir(hanoi_path)
        print(f"\n✓ 已刪除空的 Hanoi 目錄")
    except:
        pass

# Step 2: 重新命名其他英文目錄為繁體中文
print(f"\nStep 2: 重新命名英文城市目錄為繁體中文\n")

for eng_city, cn_city in CITY_MAPPING.items():
    if eng_city == 'Hanoi':
        continue  # 已處理

    old_dir = os.path.join(vietnam_path, eng_city)
    new_dir = os.path.join(vietnam_path, cn_city)

    if os.path.isdir(old_dir):
        if os.path.isdir(new_dir):
            print(f"⚠️  {cn_city} 目錄已存在，合併 {eng_city} 到 {cn_city}")
            # 合併檔案
            for file in os.listdir(old_dir):
                src = os.path.join(old_dir, file)
                dst = os.path.join(new_dir, file)
                if os.path.isfile(src):
                    try:
                        shutil.move(src, dst)
                    except:
                        pass
            # 刪除空目錄
            try:
                os.rmdir(old_dir)
            except:
                pass
        else:
            try:
                os.rename(old_dir, new_dir)
                print(f"✓ 已重新命名: {eng_city} → {cn_city}")
            except Exception as e:
                print(f"✗ 重新命名失敗: {eng_city} → {cn_city}")

print(f"\n{'='*100}")
print("✅ 越南城市名統一完成！")
print(f"{'='*100}\n")
