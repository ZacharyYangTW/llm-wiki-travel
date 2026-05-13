#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理誤分類的檔案
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\台灣"

print("=" * 70, flush=True)
print("🔧 清理台灣目錄中的誤分類", flush=True)
print("=" * 70, flush=True)

# 找出不應該存在的目錄
invalid_dirs = []
for item in os.listdir(WIKI_BASE):
    item_path = os.path.join(WIKI_BASE, item)
    if not os.path.isdir(item_path):
        continue

    # 檢查是否包含非台灣地名的字符
    if '沖繩' in item or '日本' in item or '縣豐見城市' in item:
        invalid_dirs.append(item)

if invalid_dirs:
    print(f"\n找到 {len(invalid_dirs)} 個誤分類目錄\n")

    for invalid_dir in invalid_dirs:
        invalid_path = os.path.join(WIKI_BASE, invalid_dir)
        print(f"❌ {invalid_dir}")

        # 列出其中的檔案
        for file in os.listdir(invalid_path):
            file_path = os.path.join(invalid_path, file)
            if os.path.isfile(file_path) and file.endswith('.md'):
                print(f"   - {file}")

                # 根據檔案名判斷應該移到哪裡
                if '古坑' in file:
                    target_dir = os.path.join(WIKI_BASE, '雲林縣')
                else:
                    # 如果無法判斷，先列出來
                    print(f"     ⚠️  無法判斷歸屬，請手動處理")
                    continue

                os.makedirs(target_dir, exist_ok=True)
                target_file = os.path.join(target_dir, file)

                if os.path.exists(target_file):
                    os.remove(target_file)

                shutil.move(file_path, target_file)
                print(f"     ✓ 移動到 {os.path.basename(target_dir)}")

        # 刪除空目錄
        try:
            if not os.listdir(invalid_path):
                os.rmdir(invalid_path)
                print(f"   ✓ 刪除空目錄")
        except:
            pass
else:
    print("\n✅ 沒有找到誤分類目錄")

print("\n" + "=" * 70, flush=True)
