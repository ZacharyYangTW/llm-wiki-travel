#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據檔名分類中國「未知」目錄中的檔案
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 根據檔名模式判斷城市歸屬
FILE_CLASSIFICATION = {
    # 北京檔案（關鍵詞）
    "北京": "北京市/北京",
    "唐寧港灣": "北京市/北京",
    "四通橋": "北京市/北京",
    "人民大學": "北京市/北京",
    "稻香村": "北京市/北京",
    "佛羅倫薩小鎮": "北京市/北京",
    "港味天下": "北京市/北京",
    "紫光大廈": "北京市/北京",
    "王府井": "北京市/北京",

    # 天津檔案（關鍵詞）
    "武清": "天津市/天津",
    "北務": "天津市/天津",
}

def classify_unknown():
    """分類「未知」目錄中的檔案"""
    china_path = os.path.join(WIKI_DIR, "中國")
    unknown_path = os.path.join(china_path, "未知")
    classified_count = 0
    unclassified_count = 0

    if not os.path.exists(unknown_path):
        print("  ⚠️  「未知」目錄不存在")
        return 0, 0

    for filename in os.listdir(unknown_path):
        if not filename.endswith('.md'):
            continue

        src_path = os.path.join(unknown_path, filename)

        # 根據檔名找分類
        target_location = None
        for keyword, location in FILE_CLASSIFICATION.items():
            if keyword in filename:
                target_location = location
                break

        if not target_location:
            print(f"  ⚠️  無法分類: {filename}")
            unclassified_count += 1
            continue

        # 建立目標目錄
        parts = target_location.split('/')
        target_dir = os.path.join(china_path, parts[0], parts[1])
        os.makedirs(target_dir, exist_ok=True)

        # 移動檔案
        target_path = os.path.join(target_dir, filename)
        try:
            shutil.move(src_path, target_path)
            classified_count += 1
            print(f"  ✓ {filename} → {target_location}/")
        except Exception as e:
            print(f"  ❌ 錯誤: {filename} - {e}")

    # 刪除空的「未知」目錄
    try:
        if not os.listdir(unknown_path):
            os.rmdir(unknown_path)
            print(f"\n  ✓ 已刪除空的「未知」目錄")
    except:
        pass

    return classified_count, unclassified_count

def main():
    print("=" * 70)
    print("🔧 分類中國「未知」目錄中的檔案")
    print("=" * 70)
    print()

    classified, unclassified = classify_unknown()
    print()

    print("=" * 70)
    print(f"✅ 完成！")
    print(f"  分類: {classified} 個檔案")
    if unclassified > 0:
        print(f"  未分類: {unclassified} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
