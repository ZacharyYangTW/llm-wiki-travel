#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正匈牙利檔案的城市結構
將 wiki/匈牙利/ 下的檔案移到相應城市子目錄
"""

import os
import shutil

HUNGARY_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\匈牙利"
BUDAPEST_DIR = os.path.join(HUNGARY_DIR, "布達佩斯")
SZENTENDRE_DIR = os.path.join(HUNGARY_DIR, "聖恩德雷")

# 聖恩德雷的檔案（其他都是布達佩斯）
SZENTENDRE_FILES = {
    "Szentendre main square.md",
}

print("=" * 70)
print("🔧 修正匈牙利城市結構")
print("=" * 70)

# 建立目錄
os.makedirs(BUDAPEST_DIR, exist_ok=True)
os.makedirs(SZENTENDRE_DIR, exist_ok=True)

# 列出根目錄的 .md 檔案
files = [f for f in os.listdir(HUNGARY_DIR) if f.endswith('.md')]

print(f"📊 找到 {len(files)} 個檔案\n")

moved_count = 0
for filename in files:
    src = os.path.join(HUNGARY_DIR, filename)

    # 判斷目標城市
    if filename in SZENTENDRE_FILES:
        dst = os.path.join(SZENTENDRE_DIR, filename)
        city = "聖恩德雷"
    else:
        dst = os.path.join(BUDAPEST_DIR, filename)
        city = "布達佩斯"

    try:
        shutil.move(src, dst)
        moved_count += 1
        print(f"✓ {filename[:40]:<40} → {city}")
    except Exception as e:
        print(f"✗ {filename[:40]:<40} | 錯誤: {str(e)[:30]}")

print("\n" + "=" * 70)
print(f"✅ 完成！移動了 {moved_count} 個檔案")
print("=" * 70)
