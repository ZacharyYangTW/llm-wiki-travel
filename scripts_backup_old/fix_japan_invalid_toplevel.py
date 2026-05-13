#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復日本第一級目錄中的非法城市（應該在都道府縣下）
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 錯誤的一級目錄 → 正確的都道府縣位置
INVALID_TOPLEVEL = {
    "立山町": "富山県",
    "御殿場市": "靜岡県",
    "鹿嶋市": "茨城県",
    "三鷹市": "東京都",
}

def fix_invalid_toplevel():
    """修復錯誤的第一級城市"""
    japan_path = os.path.join(WIKI_DIR, "日本")
    fixed_count = 0

    for city, prefecture in INVALID_TOPLEVEL.items():
        city_path = os.path.join(japan_path, city)

        if not os.path.exists(city_path):
            print(f"  ⚠️  目錄不存在: {city}")
            continue

        # 建立正確的目標位置
        prefecture_path = os.path.join(japan_path, prefecture)
        os.makedirs(prefecture_path, exist_ok=True)

        target_city_path = os.path.join(prefecture_path, city)

        # 如果目標位置已存在，合併檔案
        if os.path.exists(target_city_path):
            for file in os.listdir(city_path):
                src = os.path.join(city_path, file)
                dst = os.path.join(target_city_path, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
        else:
            # 移動整個目錄
            os.makedirs(target_city_path, exist_ok=True)
            for file in os.listdir(city_path):
                src = os.path.join(city_path, file)
                dst = os.path.join(target_city_path, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)

        # 刪除原一級目錄
        try:
            shutil.rmtree(city_path)
            fixed_count += 1
            print(f"  ✓ {city} 移動到 {prefecture}/{city}")
        except Exception as e:
            print(f"  ❌ 錯誤: {city} - {e}")

    return fixed_count

def main():
    print("=" * 70)
    print("🔧 修復日本第一級目錄中的非法城市")
    print("=" * 70)
    print()

    fixed = fix_invalid_toplevel()
    print()

    print("=" * 70)
    print(f"✅ 完成！{fixed} 個非法目錄已修復")
    print("=" * 70)

if __name__ == "__main__":
    main()
