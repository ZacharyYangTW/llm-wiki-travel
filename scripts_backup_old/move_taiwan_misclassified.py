#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

# 1. 移動金門縣澳門檔案
print("=" * 70)
print("1. 移動金門縣 → 澳門:")
kinmen = wiki_path / '台灣' / '金門縣'
macau = wiki_path / '澳門'

moved = 0
for md_file in kinmen.glob('*.md'):
    content = md_file.read_text(encoding='utf-8')
    match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', content)
    
    if match:
        lng = float(match.group(1))
        lat = float(match.group(2))
        
        # 澳門座標
        if 113.5 <= lng <= 114.5 and 22.0 <= lat <= 22.6:
            target = macau / md_file.name
            shutil.move(str(md_file), str(target))
            print(f"  ✓ {md_file.name}")
            moved += 1

print(f"  共移動 {moved} 個檔案")

# 2. 移動連江縣福州檔案（长乐）
print("\n2. 移動連江縣 → 中國/福建省:")
lianchiang = wiki_path / '台灣' / '連江縣'
fujian_changLe = wiki_path / '中國' / '福建省' / '長樂'

if not fujian_changLe.exists():
    fujian_changLe.mkdir(parents=True, exist_ok=True)

moved = 0
for town_dir in lianchiang.iterdir():
    if not town_dir.is_dir():
        continue
    
    for md_file in town_dir.glob('*.md'):
        if '长乐' in md_file.name:
            target = fujian_changLe / md_file.name
            shutil.move(str(md_file), str(target))
            print(f"  ✓ {md_file.name}")
            moved += 1

print(f"  共移動 {moved} 個檔案")

print("\n" + "=" * 70)
print("驗證:")
macau_count = len(list(macau.glob('*.md')))
fujian_count = len(list(fujian_changLe.glob('*.md')))
print(f"  澳門: {macau_count} 個檔案")
print(f"  中國/福建省/長樂: {fujian_count} 個檔案")
