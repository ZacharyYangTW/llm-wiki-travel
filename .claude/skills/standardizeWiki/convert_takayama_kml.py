#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 轉換高山市 POI 到 Wiki Markdown
"""

import os
import sys
import re
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

# 高山市的 POI 信息（從 KML 提取）
TAKAYAMA_POIS = [
    {
        'name': 'Country Hotel Takayama',
        'jp_name': '高山カントリーホテル',
        'description': '高山鄉村飯店',
        'category': '飯店',
        'coords': [137.251, 36.139],
    },
    {
        'name': 'Takayama Nohi Bus Center',
        'jp_name': '高山濃飛バスセンター',
        'description': '高山濃飛巴士站',
        'category': '交通',
        'coords': [137.251, 36.142],
    },
    {
        'name': '高山駅',
        'jp_name': '高山駅',
        'description': '高山站',
        'category': '交通',
        'coords': [137.251, 36.141],
    },
    {
        'name': 'Takayama Hachiman Post Office',
        'jp_name': '高山八幡郵便局',
        'description': '郵局',
        'category': '公共設施',
        'coords': [137.259, 36.146],
    },
    {
        'name': '飛驒國分寺',
        'jp_name': '飛驒国分寺',
        'description': '國分寺',
        'category': '寺廟',
        'coords': [137.254, 36.143],
    },
    {
        'name': '匠館',
        'jp_name': '匠館',
        'description': '匠館烤肉串',
        'category': '餐飲',
        'coords': [137.258, 36.144],
    },
    {
        'name': '右衛門横町',
        'jp_name': '右衛門横町',
        'description': '右衛門横町旁邊有甜酒，裡面有賣海鹽',
        'category': '商店',
        'coords': [137.258, 36.144],
    },
    {
        'name': 'Wabisuke',
        'jp_name': 'わびすけ',
        'description': '古里古里串燒，很熱情會講日文的阿婆賣飛驒牛580/串',
        'category': '餐飲',
        'coords': [137.258, 36.144],
    },
    {
        'name': 'Takumiya Yasukawa',
        'jp_name': '匠家やすかわ',
        'description': '肉之匠家，飛驒牛，包子都有賣',
        'category': '餐飲',
        'coords': [137.259, 36.144],
    },
    {
        'name': '飛驒牛まん本舖',
        'jp_name': '飛驒牛まん本舖',
        'description': '網友推薦飛驒牛肉包',
        'category': '餐飲',
        'coords': [137.260, 36.144],
    },
    {
        'name': 'Hida Kotte',
        'jp_name': 'ひだこって',
        'description': '飛驒牛壽司，有ABCX四種套餐',
        'category': '餐飲',
        'coords': [137.259, 36.142],
    },
    {
        'name': '茶乃芽',
        'jp_name': '茶乃芽',
        'description': '喝咖啡',
        'category': '餐飲',
        'coords': [137.259, 36.142],
    },
    {
        'name': 'Valor Takayama Minami',
        'jp_name': 'ヴァロー高山南',
        'description': 'Valor超市',
        'category': '購物',
        'coords': [137.252, 36.135],
    },
    {
        'name': 'Hidagyu Maruaki',
        'jp_name': '丸明',
        'description': '丸明高級飛驒牛',
        'category': '餐飲',
        'coords': [137.254, 36.143],
    },
    {
        'name': 'Nakabashi Bridge',
        'jp_name': '中橋',
        'description': '中橋（賞夜櫻的好去處）',
        'category': '景點',
        'coords': [137.259, 36.140],
    },
    {
        'name': '全家便利商店',
        'jp_name': 'ファミリーマート',
        'description': '全家便利商店',
        'category': '便利店',
        'coords': [137.252, 36.142],
    },
]

def create_markdown(poi):
    """為 POI 創建 Markdown 內容"""
    timestamp = datetime.now().isoformat() + 'Z'

    # 生成簡化的 slug
    slug = poi['name'].lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    frontmatter = f"""---
title: {poi['name']}
slug: {slug}
location: 高山市
country: 日本
city: 高山市
category: {poi['category']}
tags: ["高山", "景點"]
coordinates: [{poi['coords'][0]}, {poi['coords'][1]}]
md5:
created_at: {timestamp}
processed: false
graph-excluded: false
source_url: raw/travel/Zachary's World Trip.kml
source_type: kml-placemark
---

# {poi['name']}"""

    content = f"""
## 基本資訊

**日文名稱：** {poi['jp_name']}
**位置：** 高山市
**國家：** 日本
**座標：** {poi['coords'][0]}, {poi['coords'][1]}
**分類：** {poi['category']}

## 描述

{poi['description']}

## 相關連結

- 座標: {poi['coords'][0]}, {poi['coords'][1]}
"""

    return frontmatter + content

print("=" * 80)
print("📝 轉換高山市 POI 到 Wiki")
print("=" * 80)

takayama_path = os.path.join(WIKI_BASE, "日本", "岐阜県", "高山市")
os.makedirs(takayama_path, exist_ok=True)

created = 0
errors = []

for poi in TAKAYAMA_POIS:
    try:
        # 生成檔名
        filename = f"{poi['name']}.md"
        filepath = os.path.join(takayama_path, filename)

        # 檢查檔案是否已存在
        if os.path.exists(filepath):
            print(f"⊘ {filename} - 已存在，跳過")
            continue

        # 創建 Markdown 檔案
        content = create_markdown(poi)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        created += 1
        print(f"✓ {filename}")
    except Exception as e:
        errors.append(f"{poi['name']}: {str(e)}")
        print(f"✗ {poi['name']}: {str(e)}")

print(f"\n{'='*80}")
print(f"✅ 完成")
print(f"  建立: {created} 個檔案")
if errors:
    print(f"  錯誤: {len(errors)} 個")
print(f"{'='*80}")
