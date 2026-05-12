#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試 move_file 函數"""

import os
import sys
import io
import shutil
from pathlib import Path

# 修復 Windows 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

WIKI_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\台灣"

def move_file(src: Path, dest_county: str, dest_district: str) -> bool:
    """移動檔案到正確位置"""
    try:
        dest_dir = Path(WIKI_PATH) / dest_county / dest_district

        # 驗證源檔案存在
        if not src.exists():
            print(f"❌ 源檔案不存在: {src}")
            return False

        print(f"✓ 源檔案存在: {src}")

        # 建立目標目錄
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ 目標目錄: {dest_dir}")
        except Exception as e:
            print(f"❌ mkdir 失敗: {dest_dir} - {e}")
            return False

        dest_file = dest_dir / src.name
        print(f"✓ 目標檔案: {dest_file}")

        # 如果目標檔案已存在，刪除源檔案
        if dest_file.exists():
            print(f"⚠️  目標檔案已存在，刪除源檔案")
            try:
                os.remove(str(src))
                print(f"✓ 源檔案已刪除")
                return True
            except Exception as e:
                print(f"❌ 刪除失敗: {src} - {e}")
                return False

        # 否則正常移動
        try:
            print(f"🔄 正在移動...")
            shutil.move(str(src), str(dest_file))
            print(f"✓ 檔案已移動")
            return True
        except Exception as e:
            print(f"❌ 移動失敗: {src} → {dest_file} - {e}")
            return False
    except Exception as e:
        print(f"❌ move_file 異常: {e}")
        return False

# 測試
print("🧪 測試 move_file 函數")
print("=" * 60)

# 找一個測試檔案
wiki_path = Path(WIKI_PATH)
test_file = None
for county_dir in wiki_path.iterdir():
    if not county_dir.is_dir():
        continue
    other_dir = county_dir / '其他'
    if other_dir.exists():
        for md_file in other_dir.glob('*.md'):
            test_file = md_file
            break
    if test_file:
        break

if not test_file:
    print("❌ 找不到測試檔案")
    sys.exit(1)

print(f"\n測試檔案: {test_file.name}")
print(f"原位置: {test_file.parent.parent.name}/{test_file.parent.name}\n")

# 嘗試移動到台中市/北屯區
result = move_file(test_file, "台中市", "北屯區")

print(f"\n{'=' * 60}")
print(f"結果: {'✅ 成功' if result else '❌ 失敗'}")

# 檢查檔案是否真的移動了
if result and not test_file.exists():
    print("✓ 確認：源檔案已不存在")
    dest_file = Path(WIKI_PATH) / "台中市" / "北屯區" / test_file.name
    if dest_file.exists():
        print(f"✓ 確認：目標檔案已存在")
        # 移回去
        shutil.move(str(dest_file), str(test_file))
        print("✓ 已移回原位置")
else:
    print("⚠️  檔案仍在原位置")
