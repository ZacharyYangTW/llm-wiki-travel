#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查日本目錄結構是否符合兩層邏輯
應該是：wiki/日本/{都道府県}/{市町村}
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
JAPAN_DIR = os.path.join(WIKI_DIR, "日本")

# 日本的47個都道府県（包含所有變體：日文原名、繁體中文等）
PREFECTURES = {
    "北海道", "青森県", "岩手県", "宮城県", "秋田県",
    "山形県", "福島県", "茨城県", "栃木県", "群馬県",
    "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県",
    "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "愛知県", "三重県", "滋賀県", "京都府",
    "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県",
    "島根県", "岡山県", "広島県", "山口県", "徳島県",
    "香川県", "愛媛県", "高知県", "福岡県", "佐賀県",
    "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県",
    "沖縄県", "静岡県", "靜岡県",  # 靜岡的日文和繁體混用
    # 繁體中文版本
    "北海道", "青森縣", "岩手縣", "宮城縣", "秋田縣",
    "山形縣", "福島縣", "茨城縣", "栃木縣", "群馬縣",
    "埼玉縣", "千葉縣", "東京都", "神奈川縣", "新潟縣",
    "富山縣", "石川縣", "福井縣", "山梨縣", "長野縣",
    "岐阜縣", "愛知縣", "三重縣", "滋賀縣", "京都府",
    "大阪府", "兵庫縣", "奈良縣", "和歌山縣", "鳥取縣",
    "島根縣", "岡山縣", "廣島縣", "山口縣", "德島縣",
    "香川縣", "愛媛縣", "高知縣", "福岡縣", "佐賀縣",
    "長崎縣", "熊本縣", "大分縣", "宮崎縣", "鹿児島縣",
    "沖繩縣",
}

def main():
    print("=" * 70)
    print("🔍 檢查日本目錄結構是否符合兩層邏輯")
    print("=" * 70)
    print()

    if not os.path.exists(JAPAN_DIR):
        print(f"❌ 日本目錄不存在: {JAPAN_DIR}")
        return

    # 掃描第一層（應該是都道府県）
    level1_dirs = {}
    invalid_dirs = []
    files_in_root = []

    for item in os.listdir(JAPAN_DIR):
        item_path = os.path.join(JAPAN_DIR, item)

        if os.path.isfile(item_path):
            files_in_root.append(item)
        elif os.path.isdir(item_path):
            if item in PREFECTURES:
                # 統計該都道府県下的市町村
                level1_dirs[item] = {
                    'cities': [],
                    'files': [],
                    'invalid': []
                }

                # 掃描第二層
                for city_item in os.listdir(item_path):
                    city_path = os.path.join(item_path, city_item)
                    if os.path.isfile(city_path):
                        level1_dirs[item]['files'].append(city_item)
                    elif os.path.isdir(city_path):
                        level1_dirs[item]['cities'].append(city_item)
            else:
                invalid_dirs.append(item)

    # 顯示結果
    print(f"📊 日本目錄結構分析:")
    print()

    # 顯示正確結構
    print(f"✅ 符合兩層結構的都道府県: {len(level1_dirs)} 個")
    for prefecture, data in sorted(level1_dirs.items()):
        city_count = len(data['cities'])
        file_count = len(data['files'])
        print(f"  - {prefecture}")
        if file_count > 0:
            print(f"    ⚠️  有 {file_count} 個檔案在都道府県根目錄: {', '.join(data['files'][:3])}")
        if city_count > 0:
            print(f"    └─ {city_count} 個市町村")

    print()

    # 顯示不符合結構的目錄
    if invalid_dirs:
        print(f"❌ 不符合兩層結構的目錄: {len(invalid_dirs)} 個")
        for invalid_dir in invalid_dirs:
            dir_path = os.path.join(JAPAN_DIR, invalid_dir)
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            sub_dir_count = len([d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))])
            print(f"  - {invalid_dir} ({sub_dir_count} 個子目錄, {file_count} 個檔案)")

    print()

    # 顯示根目錄中的檔案
    if files_in_root:
        print(f"⚠️  日本根目錄中有 {len(files_in_root)} 個檔案:")
        for file in files_in_root:
            print(f"  - {file}")

    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
