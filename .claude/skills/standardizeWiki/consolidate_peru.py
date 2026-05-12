#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一祕魯/秘魯目錄，重新命名英文城市為繁體中文
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 英文城市 -> 繁體中文城市對應
CITY_MAPPING = {
    'Arequipa': '阿雷基帕',
    'Cajamarca': '卡哈馬卡',
    'Cusco': '庫斯科',
    'Ica': '伊卡',
    'Lima': '利馬',
    'Trujillo': '特魯希略',
}

print("=" * 100)
print("統一祕魯目錄結構，使用繁體中文城市名")
print("=" * 100)

# Step 1: 重新命名秘魯下的英文目錄為繁體中文
peru_path = os.path.join(WIKI_BASE, '秘魯')
if os.path.isdir(peru_path):
    print("\nStep 1: 重新命名秘魯下的英文目錄為繁體中文\n")

    for eng_city, cn_city in CITY_MAPPING.items():
        old_dir = os.path.join(peru_path, eng_city)
        new_dir = os.path.join(peru_path, cn_city)

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
                os.rename(old_dir, new_dir)
                print(f"✓ 已重新命名: {eng_city} → {cn_city}")

# Step 2: 將祕魯目錄合併到秘魯
trad_peru_path = os.path.join(WIKI_BASE, '祕魯')
if os.path.isdir(trad_peru_path):
    print(f"\nStep 2: 將祕魯目錄合併到秘魯\n")

    # 先確保秘魯目錄已重新命名
    for cn_city in CITY_MAPPING.values():
        src_dir = os.path.join(trad_peru_path, cn_city)
        dst_dir = os.path.join(peru_path, cn_city)

        if os.path.isdir(src_dir):
            os.makedirs(dst_dir, exist_ok=True)

            # 合併檔案
            for file in os.listdir(src_dir):
                src_file = os.path.join(src_dir, file)
                dst_file = os.path.join(dst_dir, file)
                if os.path.isfile(src_file):
                    try:
                        shutil.move(src_file, dst_file)
                        print(f"✓ 已移動: {cn_city}/{file}")
                    except Exception as e:
                        print(f"✗ 移動失敗: {cn_city}/{file}")

            # 刪除空目錄
            try:
                os.rmdir(src_dir)
            except:
                pass

    # 刪除祕魯目錄
    try:
        os.rmdir(trad_peru_path)
        print(f"\n✓ 已刪除空的祕魯目錄")
    except Exception as e:
        print(f"\n⚠️  無法刪除祕魯目錄: {e}")

print(f"\n{'='*100}")
print("✅ 秘魯目錄統一完成！")
print(f"{'='*100}\n")
