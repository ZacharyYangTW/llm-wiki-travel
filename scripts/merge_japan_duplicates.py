#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併日本重複的城市目錄
保留日文漢字版本（県），把繁體中文版本（縣）合併進去
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\日本"

# 映射表：繁體中文 -> 日文漢字
MERGE_MAP = {
    '佐賀縣': '佐賀県',
    '千葉縣': '千葉県',
    '和歌山縣': '和歌山県',
    '大分縣': '大分県',
    '兵庫縣': '兵庫県',
    '宮城縣': '宮城県',
    '山口縣': '山口県',
    '山形縣': '山形県',
    '岡山縣': '岡山県',
    '岩手縣': '岩手県',
    '島根縣': '島根県',
    '廣島縣': '広島県',
    '德島縣': '徳島県',
    '愛媛縣': '愛媛県',
    '新潟縣': '新潟県',
    '栃木縣': '栃木県',
    '熊本縣': '熊本県',
    '石川縣': '石川県',
    '神奈川縣': '神奈川県',
    '福井縣': '福井県',
    '福岡縣': '福岡県',
    '福島縣': '福島県',
    '秋田縣': '秋田県',
    '茨城縣': '茨城県',
    '長崎縣': '長崎県',
    '青森縣': '青森県',
    '靜岡縣': '静岡県',
    '香川縣': '香川県',
    '鳥取縣': '鳥取県',
    '鹿兒島縣': '鹿児島県',
    # 特殊情況
    '大阪': '大阪府',
    '東京': '東京都',
    '福岡': '福岡県',
    '長崎': '長崎県',
    '沖繩': '沖縄県',
}

print("=" * 70, flush=True)
print("🔧 合併日本重複目錄", flush=True)
print("=" * 70, flush=True)

merged_count = 0
files_moved = 0
failed_list = []

for chinese_name, japanese_name in sorted(MERGE_MAP.items()):
    chinese_path = os.path.join(WIKI_BASE, chinese_name)
    japanese_path = os.path.join(WIKI_BASE, japanese_name)

    # 檢查繁體中文版本是否存在
    if not os.path.isdir(chinese_path):
        continue

    # 如果日文版本不存在，創建它
    if not os.path.isdir(japanese_path):
        os.makedirs(japanese_path, exist_ok=True)
        print(f"\n📁 創建目錄: {japanese_name}", flush=True)

    # 列出繁體中文版本中的檔案
    items = os.listdir(chinese_path)

    if not items:
        print(f"\n✓ {chinese_name} 是空目錄，直接刪除", flush=True)
        try:
            os.rmdir(chinese_path)
            merged_count += 1
        except Exception as e:
            failed_list.append((chinese_name, str(e)[:50]))
        continue

    print(f"\n🔀 合併 {chinese_name} → {japanese_name} ({len(items)} 項)", flush=True)

    # 移動所有檔案和子目錄
    for item in items:
        chinese_item = os.path.join(chinese_path, item)
        japanese_item = os.path.join(japanese_path, item)

        try:
            # 如果目標已存在，刪除後再移動
            if os.path.exists(japanese_item):
                if os.path.isdir(japanese_item):
                    shutil.rmtree(japanese_item)
                else:
                    os.remove(japanese_item)

            shutil.move(chinese_item, japanese_item)
            files_moved += 1
            print(f"  ✓ {item}", flush=True)

        except Exception as e:
            failed_list.append((f"{chinese_name}/{item}", str(e)[:50]))
            print(f"  ❌ {item}: {str(e)[:50]}", flush=True)

    # 刪除空的繁體中文版本目錄
    try:
        if os.path.isdir(chinese_path) and not os.listdir(chinese_path):
            os.rmdir(chinese_path)
            merged_count += 1
    except Exception as e:
        failed_list.append((chinese_name, f"刪除失敗: {str(e)[:30]}"))

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已合併: {merged_count} 對目錄", flush=True)
print(f"  已移動: {files_moved} 個項目", flush=True)
if failed_list:
    print(f"  失敗: {len(failed_list)} 個", flush=True)
    for item, error in failed_list[:5]:
        print(f"    - {item}: {error}", flush=True)

print(f"{'='*70}", flush=True)
