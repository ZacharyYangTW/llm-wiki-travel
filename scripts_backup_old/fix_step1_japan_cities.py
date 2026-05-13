#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

print("=" * 80)
print("Step 1: 建立日本缺失的城市目錄")
print("=" * 80)

# 1. 徳島市
tokushima_city = wiki_path / '日本' / '徳島県' / '徳島市'
if tokushima_city.exists():
    print("✓ 日本/徳島県/徳島市 已存在")
else:
    tokushima_city.mkdir(parents=True, exist_ok=True)
    print("✓ 建立 日本/徳島県/徳島市")

# 2. 群馬県
gunma = wiki_path / '日本' / '群馬県'
if gunma.exists():
    print("✓ 日本/群馬県 已存在")
else:
    gunma.mkdir(parents=True, exist_ok=True)
    print("✓ 建立 日本/群馬県")

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
