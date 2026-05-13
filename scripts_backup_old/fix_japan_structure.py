#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復日本目錄結構，確保符合兩層邏輯：wiki/日本/{都道府県}/{市町村}
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
JAPAN_DIR = os.path.join(WIKI_DIR, "日本")

# 需要修復的目錄映射
# 格式: 源目錄 -> (都道府県, 市町村)
FIX_MAPPING = {
    "長崎縣壹岐島": ("長崎県", "壹岐島"),
    "沖繩縣北谷町": ("沖繩県", "北谷町"),
    "沖繩縣那霸市": ("沖繩県", "那霸市"),
    "沖繩縣本部町": ("沖繩県", "本部町"),
}

def move_file(src, dst):
    """移動檔案"""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.move(src, dst)
        return True
    return False

def main():
    print("=" * 70)
    print("🔧 修復日本目錄結構（兩層邏輯）")
    print("=" * 70)
    print()

    moved_count = 0
    fixed_dirs = []

    # 修復映射中的目錄
    for src_dir, (prefecture, city) in FIX_MAPPING.items():
        src_path = os.path.join(JAPAN_DIR, src_dir)

        if not os.path.exists(src_path):
            continue

        print(f"🔍 處理: {src_dir}")

        # 建立目標目錄
        dst_dir = os.path.join(JAPAN_DIR, prefecture, city)
        os.makedirs(dst_dir, exist_ok=True)

        # 移動所有檔案
        if os.path.isdir(src_path):
            for item in os.listdir(src_path):
                src_item_path = os.path.join(src_path, item)
                dst_item_path = os.path.join(dst_dir, item)

                if os.path.isfile(src_item_path):
                    if move_file(src_item_path, dst_item_path):
                        print(f"  ✓ {item} → {prefecture}/{city}/")
                        moved_count += 1

        # 刪除空的源目錄
        try:
            if not os.listdir(src_path):
                shutil.rmtree(src_path)
                print(f"  ✓ 已刪除空目錄: {src_dir}")
                fixed_dirs.append(src_dir)
        except:
            pass

        print()

    # 處理 static 岡県 (應該是靜岡県)
    static_path = os.path.join(JAPAN_DIR, "静岡県")
    shizuoka_path = os.path.join(JAPAN_DIR, "靜岡県")

    if os.path.exists(static_path) and not os.path.exists(shizuoka_path):
        print("🔄 修復繁簡混用: 静岡県 → 靜岡県")
        try:
            shutil.move(static_path, shizuoka_path)
            print("  ✓ 已重命名")
            fixed_dirs.append("静岡県")
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")

    print()

    # 合併繁簡混用的目錄
    duplicate_prefectures = [
        ("兵庫県", "兵庫縣"),
        ("沖繩県", "沖繩縣"),
    ]

    for simplified, traditional in duplicate_prefectures:
        simp_path = os.path.join(JAPAN_DIR, simplified)
        trad_path = os.path.join(JAPAN_DIR, traditional)

        if os.path.exists(simp_path) and os.path.exists(trad_path):
            print(f"🔄 合併繁簡混用: {traditional} ← {simplified}")

            # 將簡體目錄的內容移到繁體
            for item in os.listdir(simp_path):
                src_item = os.path.join(simp_path, item)
                dst_item = os.path.join(trad_path, item)

                if os.path.isdir(src_item):
                    if os.path.exists(dst_item):
                        # 如果目標已存在，合併子目錄
                        for subitem in os.listdir(src_item):
                            src_sub = os.path.join(src_item, subitem)
                            dst_sub = os.path.join(dst_item, subitem)
                            if os.path.isfile(src_sub) and not os.path.exists(dst_sub):
                                shutil.move(src_sub, dst_sub)
                                moved_count += 1
                                print(f"  ✓ {item}/{subitem}")
                    else:
                        shutil.move(src_item, dst_item)
                        moved_count += 1
                        print(f"  ✓ {item}")
                elif os.path.isfile(src_item):
                    dst_file = os.path.join(trad_path, item)
                    if not os.path.exists(dst_file):
                        shutil.move(src_item, dst_file)
                        moved_count += 1
                        print(f"  ✓ {item}")

            # 刪除簡體目錄
            try:
                shutil.rmtree(simp_path)
                print(f"  ✓ 已刪除: {simplified}")
                fixed_dirs.append(simplified)
            except:
                pass

    print()
    print("=" * 70)
    print(f"✅ 修復完成")
    print(f"  已修復目錄: {len(fixed_dirs)} 個")
    print(f"  已移動檔案: {moved_count} 個")
    print("=" * 70)

if __name__ == "__main__":
    main()
