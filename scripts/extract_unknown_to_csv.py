#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 wiki/未知 中掃描所有檔案，提取坐標資訊，生成 CSV
"""

import os
import sys
import csv
import re
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
OUTPUT_CSV = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"

def extract_coordinates(file_path):
    """從檔案中提取坐標 [lng, lat]"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
        if match:
            lng = match.group(1).strip()
            lat = match.group(2).strip()
            return lng, lat
    except Exception:
        pass

    return None, None

def main():
    print("=" * 70)
    print("🔍 掃描 wiki/未知 中的所有檔案並提取坐標")
    print("=" * 70)
    print()

    unknown_path = os.path.join(WIKI_DIR, "未知")
    if not os.path.exists(unknown_path):
        print(f"❌ 路徑不存在: {unknown_path}")
        return

    # 收集所有檔案資訊
    files_data = []
    total_count = 0
    with_coords_count = 0
    without_coords_count = 0

    print(f"🔍 掃描中...")
    print()

    for root, dirs, files in os.walk(unknown_path):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            file_path = os.path.join(root, filename)

            # 提取文件名（不包含 .md）
            title = filename[:-3]  # 移除 .md 副檔名

            # 提取坐標
            lng, lat = extract_coordinates(file_path)

            if lng and lat:
                with_coords_count += 1
            else:
                without_coords_count += 1

            total_count += 1

            # 添加到列表（City 和 Country 暫時為空）
            files_data.append({
                '標題': title,
                '經度': lng if lng else '',
                '緯度': lat if lat else '',
                '城市': '',
                '國家': ''
            })

    # 寫入 CSV
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
            writer.writeheader()
            writer.writerows(files_data)

        print(f"✅ 已生成 CSV: {OUTPUT_CSV}")
        print()
    except Exception as e:
        print(f"❌ 寫入 CSV 失敗: {e}")
        return

    print("=" * 70)
    print(f"📊 統計資訊:")
    print(f"  總檔案數: {total_count}")
    print(f"  有坐標: {with_coords_count}")
    print(f"  無坐標: {without_coords_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
