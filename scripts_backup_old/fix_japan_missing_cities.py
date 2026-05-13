#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
補充日本缺失城市的都道府縣映射並重組
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 補充缺失的城市映射
MISSING_MAPPINGS = {
    "高山市": "岐阜県",
    "那智勝浦町": "和歌山県",
    "洞爺湖町": "北海道",
    "喜多方市": "福島県",
    "深浦町": "青森県",
    "琴平町": "香川県",
    "境港市": "鳥取県",
    "大仙市": "秋田県",
    "斜里町": "北海道",
    "大空町": "北海道",
    "四万十町": "高知県",
    "小美玉市": "茨城県",
    "大子町": "茨城県",
    "佐々町": "長崎県",
    "高森町": "熊本県",
    "高千穂町": "宮崎県",
    "屋久島町": "鹿児島県",
    "南大隅町": "鹿児島県",
    "三鷹市": "東京都",
    "富士市": "静岡県",
    "黑部市": "富山県",
    "伊勢市": "三重県",
    "三重縣熊野市": "三重県",
}

def restructure_missing():
    """重新組織缺失的城市"""
    japan_path = os.path.join(WIKI_DIR, "日本")
    moved_count = 0

    for city, prefecture in MISSING_MAPPINGS.items():
        city_path = os.path.join(japan_path, city)

        if not os.path.exists(city_path):
            print(f"  ⚠️  目錄不存在: {city}")
            continue

        # 建立都道府縣目錄
        prefecture_path = os.path.join(japan_path, prefecture)
        os.makedirs(prefecture_path, exist_ok=True)

        # 建立市區町村目錄
        target_city_path = os.path.join(prefecture_path, city)
        os.makedirs(target_city_path, exist_ok=True)

        # 移動檔案
        try:
            for file in os.listdir(city_path):
                src = os.path.join(city_path, file)
                dst = os.path.join(target_city_path, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)

            # 刪除原目錄
            shutil.rmtree(city_path)
            moved_count += 1
            print(f"  ✓ {prefecture}/{city}")
        except Exception as e:
            print(f"  ❌ 錯誤: {city} - {e}")

    return moved_count

def main():
    print("=" * 70)
    print("🔧 補充日本缺失城市的映射")
    print("=" * 70)
    print()

    moved = restructure_missing()
    print()

    print("=" * 70)
    print(f"✅ 完成！{moved} 個城市已重新組織")
    print("=" * 70)

if __name__ == "__main__":
    main()
