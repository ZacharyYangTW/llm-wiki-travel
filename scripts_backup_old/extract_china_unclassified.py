#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取中國所有無法分類到城市的檔案及其坐標
這些檔案很可能被誤分類，需要移到其他國家
"""

import os
import sys
import csv
import re
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_CHINA = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\中國"
OUTPUT_CSV = r"h:\我的雲端硬碟\llm_wiki_travel\china_unclassified_files.csv"
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 中國主要省份和直轄市
CHINA_PROVINCES = {
    '上海', '北京', '天津', '重慶',
    '江蘇省', '浙江省', '安徽省', '福建省', '江西省', '山東省',
    '河南省', '湖北省', '湖南省', '廣東省', '廣西自治區',
    '海南省', '四川省', '貴州省', '雲南省', '西藏',
    '陝西省', '甘肅省', '青海省', '寧夏回族自治區', '新疆',
    '山西省', '河北省', '遼寧省', '吉林省', '黑龍江省',
    '內蒙古', '臺灣'
}

def extract_coordinates(md_file):
    """提取坐標"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(COORD_PATTERN, content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return lng, lat
    except:
        pass
    return None, None

print("=" * 70, flush=True)
print("🔍 提取中國無法分類到城市的檔案", flush=True)
print("=" * 70, flush=True)

rows = []

# 掃描所有省份
for province in sorted(os.listdir(WIKI_CHINA)):
    province_path = os.path.join(WIKI_CHINA, province)

    if not os.path.isdir(province_path):
        continue

    # 列出省份目錄下的一級子目錄（城市）
    cities = set()
    for item in os.listdir(province_path):
        item_path = os.path.join(province_path, item)
        if os.path.isdir(item_path):
            cities.add(item)

    # 找省份根目錄的 .md 檔案（未分類）
    root_files = [f for f in os.listdir(province_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(province_path, f))]

    if root_files:
        print(f"\n📍 {province} ({len(root_files)} 個根目錄檔案):", flush=True)

        for filename in root_files:
            file_path = os.path.join(province_path, filename)
            title = filename[:-3]

            lng, lat = extract_coordinates(file_path)

            rows.append({
                '檔案名': filename,
                '省份': province,
                '經度': lng if lng is not None else '',
                '緯度': lat if lat is not None else '',
                '路徑': f"中國/{province}/{filename}"
            })

            if lng and lat:
                print(f"  {title[:40]:<40} [{lng:8.4f}, {lat:8.4f}]", flush=True)
            else:
                print(f"  {title[:40]:<40} [無坐標]", flush=True)

# 寫入 CSV
print(f"\n💾 寫入 CSV...", flush=True)
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['檔案名', '省份', '經度', '緯度', '路徑'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 70, flush=True)
print(f"✅ 完成！", flush=True)
print(f"  總共提取: {len(rows)} 個檔案", flush=True)
print(f"  CSV 已保存到: {OUTPUT_CSV}", flush=True)
print("=" * 70, flush=True)
