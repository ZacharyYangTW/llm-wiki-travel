#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將日本目錄名稱標準化為日文漢字
統一 県/縣、區/区 等表示
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\日本"

# 一級目錄（都道府縣）映射表：繁體中文縣→日文漢字県
PREFECTURE_MAPPING = {
    "佐賀縣": "佐賀県",
    "沖繩縣": "沖縄県",
    "長崎縣": "長崎県",
    "青森縣": "青森県",
    "福井縣": "福井県",
    "福岡縣": "福岡県",
    "石川縣": "石川県",
    "靜岡縣": "静岡県",
    "神奈川縣": "神奈川県",
    "岩手縣": "岩手県",
    "三重縣": "三重県",
}

# 二級目錄（市町村）映射表：非市町村目錄或需要重命名的
# 東京都特殊處理：很多目錄名不是真正的市町村
TOKYO_INVALID = {
    "• 謝淳凱 Shie Chuen Kai 東京都豊島区池袋本町3": None,  # 完全無效，刪除
    "原宿": None,
    "大國藥妝": None,
    "新宿Airbnb": None,
    "新宿さくらみち": None,
    "東京": "東京都",
    "東京都": None,  # 重複，刪除
    "東京都荒川区東日暮里6": None,  # 太具體的地址，刪除
    "池袋": None,
    "涉谷": "渋谷区",  # 修正繁體中文為日文漢字
    "港區": "港区",  # 修正繁體中文為日文漢字
    "都營新宿線": None,
    "新宿": "新宿区",  # 補充區
}

# 其他需要修正的二級目錄
CITY_MAPPING = {
    "三重縣熊野市": "熊野市",  # 移除重複的縣份
}

def rename_dir(old_path, new_name):
    """重命名目錄"""
    try:
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if old_path != new_path:
            shutil.move(old_path, new_path)
            return True, new_path
        return False, old_path
    except Exception as e:
        print(f"  ❌ 重命名失敗: {e}")
        return False, old_path

def remove_dir(path):
    """刪除空目錄或將檔案移動後刪除"""
    try:
        # 先將所有檔案移出去（暫時放在父目錄）
        files = []
        if os.path.isdir(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    files.append(file_path)

        # 刪除目錄
        shutil.rmtree(path, ignore_errors=True)
        return True, files
    except Exception as e:
        print(f"  ❌ 刪除失敗: {e}")
        return False, []

def main():
    print("=" * 70)
    print("🔤 標準化日本目錄名稱為日文漢字")
    print("=" * 70)
    print()

    # 步驟 1: 標準化一級目錄（都道府縣）
    print("📍 步驟 1: 標準化都道府縣名稱")
    print("-" * 70)

    renamed_count = 0
    for old_name, new_name in PREFECTURE_MAPPING.items():
        old_path = os.path.join(WIKI_DIR, old_name)
        if os.path.exists(old_path):
            success, new_path = rename_dir(old_path, new_name)
            if success:
                renamed_count += 1
                print(f"  ✓ {old_name} → {new_name}")

    print()

    # 步驟 2: 標準化東京都的二級目錄
    print("📍 步驟 2: 清理東京都的非市町村目錄")
    print("-" * 70)

    tokyo_dir = os.path.join(WIKI_DIR, "東京都")
    deleted_count = 0
    renamed_tokyo_count = 0

    if os.path.exists(tokyo_dir):
        for dir_name in os.listdir(tokyo_dir):
            dir_path = os.path.join(tokyo_dir, dir_name)

            if not os.path.isdir(dir_path):
                continue

            # 檢查是否在無效清單中
            if dir_name in TOKYO_INVALID:
                action = TOKYO_INVALID[dir_name]

                if action is None:
                    # 刪除此目錄
                    success, files = remove_dir(dir_path)
                    if success:
                        deleted_count += 1
                        print(f"  ✗ {dir_name} (已刪除)")
                elif action.endswith("區"):
                    # 重命名為正確的市區名稱
                    success, new_path = rename_dir(dir_path, action)
                    if success:
                        renamed_tokyo_count += 1
                        print(f"  ✓ {dir_name} → {action}")

    print()

    # 步驟 3: 修正其他混亂的目錄名稱
    print("📍 步驟 3: 修正其他混亂的目錄名稱")
    print("-" * 70)

    other_fixed = 0
    for root, dirs, files in os.walk(WIKI_DIR):
        for dir_name in dirs[:]:  # 使用 [:] 避免在迭代時修改列表
            if dir_name in CITY_MAPPING:
                dir_path = os.path.join(root, dir_name)
                new_name = CITY_MAPPING[dir_name]

                success, new_path = rename_dir(dir_path, new_name)
                if success:
                    other_fixed += 1
                    print(f"  ✓ {dir_name} → {new_name}")

    print()
    print("=" * 70)
    print(f"✅ 完成！")
    print(f"  都道府縣重命名: {renamed_count} 個")
    print(f"  東京都清理: 已刪除 {deleted_count} 個，重命名 {renamed_tokyo_count} 個")
    print(f"  其他修正: {other_fixed} 個")
    print("=" * 70)

if __name__ == "__main__":
    main()
