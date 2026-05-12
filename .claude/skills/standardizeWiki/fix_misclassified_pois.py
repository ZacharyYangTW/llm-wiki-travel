#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正誤分類的景點
識別並移動到正確的國家/城市
"""

import os
import sys
import re
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 誤分類規則：(源目錄, 要移除的子目錄) -> (目標國家, 目標城市)
MISCLASSIFICATION_RULES = [
    # 印尼中的馬來西亞景點
    {
        'source_country': '印尼',
        'source_city': 'Medan',
        'keywords': ['penang', 'kl', 'kuala lumpur', 'klia', 'klsentral', 'malac', 'melaka', 'merdeka', 'petronas'],
        'target_country': '馬來西亞',
        'target_mapping': {
            'penang': 'Penang',
            'kl': 'Kuala Lumpur',
            'kuala lumpur': 'Kuala Lumpur',
            'klia': 'Kuala Lumpur',
            'klsentral': 'Kuala Lumpur',
            'malac': 'Malacca',
            'melaka': 'Malacca',
            'merdeka': 'Kuala Lumpur',
            'petronas': 'Kuala Lumpur',
        }
    }
]

def get_target_city(filename, keyword_map):
    """根據檔名關鍵詞確定目標城市"""
    filename_lower = filename.lower()

    for keyword, target in keyword_map.items():
        if keyword in filename_lower:
            return target

    # 如果沒有匹配到特定城市，返回 None
    return None

def fix_misclassifications():
    """修正誤分類景點"""
    print("=" * 100)
    print("🔧 修正誤分類景點")
    print("=" * 100)

    total_moved = 0
    total_failed = 0

    for rule in MISCLASSIFICATION_RULES:
        source_country = rule['source_country']
        source_city = rule['source_city']
        target_country = rule['target_country']
        keywords = rule['keywords']
        target_mapping = rule['target_mapping']

        print(f"\n{'='*100}")
        print(f"🔍 檢查 {source_country}/{source_city} 中的誤分類景點")
        print(f"{'='*100}\n")

        source_path = os.path.join(WIKI_BASE, source_country, source_city, 'POI')

        if not os.path.isdir(source_path):
            print(f"   ❌ 源目錄不存在: {source_path}")
            continue

        files = os.listdir(source_path)
        misclassified_count = 0
        city_counts = {}

        # 掃描並識別誤分類檔案
        for filename in sorted(files):
            if not filename.endswith('.md'):
                continue

            filename_lower = filename.lower()
            is_misclassified = False

            # 檢查是否符合任何誤分類關鍵詞
            for keyword in keywords:
                if keyword in filename_lower:
                    is_misclassified = True
                    break

            if not is_misclassified:
                continue

            misclassified_count += 1

            # 確定目標城市
            target_city = get_target_city(filename, target_mapping)

            if not target_city:
                print(f"   ⚠️  無法確定目標城市: {filename}")
                continue

            # 記錄統計
            city_counts[target_city] = city_counts.get(target_city, 0) + 1

            # 建立目標目錄
            target_path = os.path.join(WIKI_BASE, target_country, target_city, 'POI')
            os.makedirs(target_path, exist_ok=True)

            source_file = os.path.join(source_path, filename)
            target_file = os.path.join(target_path, filename)

            # 檢查目標檔案是否已存在
            if os.path.exists(target_file):
                print(f"   ℹ️  已存在: {target_city}/{filename} (跳過)")
                # 刪除源檔案
                try:
                    os.remove(source_file)
                    total_moved += 1
                except:
                    pass
                continue

            # 移動檔案
            try:
                shutil.move(source_file, target_file)
                print(f"   ✅ {target_city}/{filename}")
                total_moved += 1
            except Exception as e:
                print(f"   ❌ 移動失敗: {filename} -> {target_city}/ ({str(e)})")
                total_failed += 1

        if misclassified_count > 0:
            print(f"\n   📊 統計:")
            for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"      移動到 {city}: {count} 個檔案")

    print(f"\n{'='*100}")
    print(f"✅ 修正完成！")
    print(f"   成功移動: {total_moved} 個檔案")
    print(f"   移動失敗: {total_failed} 個檔案")
    print(f"{'='*100}")

if __name__ == '__main__':
    fix_misclassifications()
