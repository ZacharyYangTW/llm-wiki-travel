#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
補充中國遺漏的城市映射
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 遺漏的城市映射
MISSING_MAPPINGS = {
    "咸寧市": "湖北省",
}

def fix_missing():
    """修複遺漏的城市"""
    china_path = os.path.join(WIKI_DIR, "中國")
    fixed_count = 0

    for city, province in MISSING_MAPPINGS.items():
        city_path = os.path.join(china_path, city)

        if not os.path.exists(city_path):
            print(f"  ⚠️  目錄不存在: {city}")
            continue

        # 建立省份目錄
        province_path = os.path.join(china_path, province)
        os.makedirs(province_path, exist_ok=True)

        # 建立市縣目錄
        target_city_path = os.path.join(province_path, city)
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
            fixed_count += 1
            print(f"  ✓ {city} → {province}/{city}")
        except Exception as e:
            print(f"  ❌ 錯誤: {city} - {e}")

    return fixed_count

def main():
    print("=" * 70)
    print("🔧 補充中國遺漏的城市")
    print("=" * 70)
    print()

    fixed = fix_missing()
    print()

    # 處理"未知"目錄
    china_path = os.path.join(WIKI_DIR, "中國")
    unknown_path = os.path.join(china_path, "未知")

    if os.path.exists(unknown_path):
        print("⚠️  「未知」目錄處理:")
        print("  該目錄包含無法分類的檔案")
        print("  建議：")
        print("    1. 手動檢查檔案內容")
        print("    2. 根據coordinates欄位分類")
        print("    3. 或保留在中國根目錄作為待分類")

    print()
    print("=" * 70)
    print(f"✅ 完成！{fixed} 個遺漏城市已修復")
    print("=" * 70)

if __name__ == "__main__":
    main()
