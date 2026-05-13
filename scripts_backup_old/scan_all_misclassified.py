#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 可疑的城市名稱（應該指向其他國家）
SUSPICIOUS_NAMES = {
    '紐約': 'USA',
    '洛杉磯': 'USA',
    '舊金山': 'USA',
    '倫敦': 'UK',
    '巴黎': 'France',
    '澳門': 'Macau',
    '台南市': 'Taiwan',
    '台北': 'Taiwan',
    '台灣': 'Taiwan',
    '東京': 'Japan',
    '京都': 'Japan',
    '大阪': 'Japan',
}

wiki_path = Path('h:/我的雲端硬碟/llm_wiki_travel/wiki')

print("=" * 80)
print("掃描所有可疑的城市資料夾")
print("=" * 80)

found_suspicious = False

for country_path in sorted(wiki_path.iterdir()):
    if not country_path.is_dir() or country_path.name.startswith('.'):
        continue

    country = country_path.name

    for city_path in country_path.iterdir():
        if not city_path.is_dir() or city_path.name.startswith('.'):
            continue

        city = city_path.name

        if city in SUSPICIOUS_NAMES:
            files = list(city_path.glob('*.md'))
            if files:
                found_suspicious = True
                print(f"\n⚠️ {country}/{city}: {len(files)} 個檔案")
                print(f"   應該在: {SUSPICIOUS_NAMES[city]}")

                for f in files[:3]:
                    print(f"     • {f.name}")

                if len(files) > 3:
                    print(f"     ... 還有 {len(files) - 3} 個檔案")

if not found_suspicious:
    print("\n✓ 沒有發現其他可疑的城市資料夾")

print("\n" + "=" * 80)
print("掃描完成")
print("=" * 80)
