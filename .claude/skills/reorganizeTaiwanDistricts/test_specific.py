#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, io, shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

WIKI_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\台灣"

# 找葛優森林民宿
src = None
for county_dir in Path(WIKI_PATH).iterdir():
    other_dir = county_dir / '其他'
    if other_dir.exists():
        for f in other_dir.glob('*.md'):
            if '葛優' in f.name or '葛优' in f.name:
                src = f
                break
    if src:
        break

if not src:
    # 找任何一個在"其他"裡的檔案
    for county_dir in Path(WIKI_PATH).iterdir():
        other_dir = county_dir / '其他'
        if other_dir.exists():
            for f in other_dir.glob('*.md'):
                src = f
                break
        if src:
            break

if not src:
    print("找不到測試檔案")
    sys.exit(1)

print(f"測試檔案: {src}")
print(f"存在: {src.exists()}")

dest_dir = Path(WIKI_PATH) / "新竹縣" / "尖石鄉"
print(f"\n目標目錄: {dest_dir}")

try:
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"mkdir 成功")
except Exception as e:
    print(f"mkdir 失敗: {e}")
    sys.exit(1)

dest_file = dest_dir / src.name
print(f"目標檔案: {dest_file}")
print(f"目標已存在: {dest_file.exists()}")

try:
    shutil.move(str(src), str(dest_file))
    print(f"移動成功！")
    # 移回
    shutil.move(str(dest_file), str(src))
    print(f"已移回")
except Exception as e:
    print(f"移動失敗: {type(e).__name__}: {e}")
