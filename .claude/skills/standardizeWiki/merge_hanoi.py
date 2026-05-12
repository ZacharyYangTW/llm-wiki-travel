#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併越南 Hanoi 和河內
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

print("=" * 100)
print("合併越南 Hanoi 和河內")
print("=" * 100)

hanoi_path = os.path.join(WIKI_BASE, '越南', 'Hanoi')
henanei_path = os.path.join(WIKI_BASE, '越南', '河內')

if not os.path.isdir(hanoi_path):
    print("\n⚠️  Hanoi 目錄不存在，無需合併")
    sys.exit(0)

print(f"\n掃描 Hanoi 目錄結構...\n")

moved_count = 0

# 處理 Hanoi 下的所有子目錄和檔案
for item in os.listdir(hanoi_path):
    src_path = os.path.join(hanoi_path, item)

    if os.path.isdir(src_path):
        # 子目錄
        print(f"📁 {item}")
        dst_dir = os.path.join(henanei_path, item)
        os.makedirs(dst_dir, exist_ok=True)

        # 合併子目錄中的檔案
        for file in os.listdir(src_path):
            src_file = os.path.join(src_path, file)
            dst_file = os.path.join(dst_dir, file)

            if os.path.isfile(src_file):
                try:
                    shutil.move(src_file, dst_file)
                    print(f"  ✓ {file}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ✗ {file} - {e}")

        # 刪除空子目錄
        try:
            os.rmdir(src_path)
        except:
            pass

    elif os.path.isfile(src_path):
        # 直接檔案
        dst_file = os.path.join(henanei_path, item)

        try:
            shutil.move(src_path, dst_file)
            print(f"✓ {item}")
            moved_count += 1
        except Exception as e:
            print(f"✗ {item} - {e}")

# 刪除 Hanoi 目錄
try:
    os.rmdir(hanoi_path)
    print(f"\n✓ 已刪除空的 Hanoi 目錄")
except Exception as e:
    print(f"\n⚠️  無法刪除 Hanoi 目錄: {e}")

print(f"\n{'='*100}")
print(f"✅ 合併完成！")
print(f"  已移動: {moved_count} 個檔案")
print(f"{'='*100}\n")
