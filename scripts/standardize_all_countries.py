#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化所有國家的城市名稱為中文（台灣常見翻譯）
"""

import os
import sys
import re
import shutil
import io
from pathlib import Path

# UTF-8 編碼支援
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# ============================================================================
# 各國城市英文 → 中文映射表
# ============================================================================

COUNTRY_CITY_MAPS = {
    "澳洲": {
        "Sydney": "雪梨",
        "Sydney Harbour Area": "雪梨港灣",
        "Melbourne Airport": "墨爾本",
        "Brisbane Airport": "布里斯本",
        "Perth Airport": "珀斯",
        "Hobart": "荷巴特",
        "Launceston": "朗塞斯頓",
        "Fremantle": "弗里曼圖爾",
        "Cambridge": "劍橋",
        "Mascot": "馬斯科特",
        "Mooloolaba": "姆盧拉巴",
        "Port Arthur": "亞瑟港",
        "Rottnest Island": "羅特尼斯特島",
        "Western Junction": "西部交匯點",
    },

    "奧地利": {
        "Wien": "維也納",
        "Salzburg": "薩爾茨堡",
        "Bad Ischl": "伊施爾",
        "Hallstatt": "哈爾施塔特",
        "Hallein": "哈萊因",
        "Gosauzwang": "戈紹茨瓦格",
        "Schwechat": "施韋夏特",
    },

    "捷克": {
        "Hlavní město Praha": "布拉格",
        "Karlovy Vary": "卡羅維瓦利",
        "Český Krumlov": "庫倫洛夫",
    },

    "印尼": {
        "Batam Kota": "巴淡",
    },

    "印度": {
        "Chennai": "金奈",
    },

    "西班牙": {
        "Segovia": "塞哥維亞",
    },

    "比利時": {
        "Bruxelles": "布魯塞爾",
        "Antwerpen": "安特衛普",
        "Gent": "根特",
        "Liège": "列日",
    },

    "加拿大": {
        "Richmond": "里士滿",
        "Surrey": "素里",
        "Nisku": "尼斯庫",
    },

    "智利": {
        "Easter Island": "復活節島",
        "Hanga Roa": "漢加羅亞",
        "Pudahuel": "普達烏埃爾",
        "SCL": "聖地亞哥",
    },

    "埃及": {
        "Al Bairat": "貝拉特",
        "Al Gayarah": "蓋亞拉",
    },

    "荷蘭": {
        "Den Haag": "海牙",
        "Rotterdam": "鹿特丹",
        "Schiphol": "史基浦",
    },

    "紐西蘭": {
        "Auckland": "奧克蘭",
        "Queenstown": "皇后鎮",
        "Arrowtown": "箭鎮",
        "Milford Sound": "米佛峽灣",
        "Fiordland National Park": "峽灣地國家公園",
        "Gammack": "甘馬克",
    },

    "秘魯": {
        "Lima": "利馬",
        "Cusco": "庫斯科",
        "Machu Pikchu": "馬丘比丘",
        "Aguas Calientes": "亞瓜斯卡連特斯",
        "Callao": "卡亞俄",
        "Nasca": "納斯卡",
        "Paracas": "帕拉卡斯",
    },

    "匈牙利": {
        "budapest": "布達佩斯",
        "Budapest": "布達佩斯",
        "Szentendre": "聖恩德雷",
    },

    "新加坡": {
        "Singapore": "新加坡",  # 合併重複
    },

    "馬來西亞": {
        "Malacca": "馬六甲",
        "Melaka": "馬六甲",
        "Bayan Lepas": "巴央勒帕斯",
        "Sepang": "雪邦",
        "Seri Kembangan": "芙蓉",
    },
}

# 需要特殊處理的國家
SPECIAL_HANDLING = {
    "紐西蘭": {
        "未知": "奧克蘭",  # 預設未知位置到最大城市
    },
    "馬來西亞": {
        "未知": "吉隆坡",  # 預設未知位置到首都
    },
    "新加坡": {
        "未知": "新加坡",  # 新加坡整個國家就是一個城市
    },
}

def merge_directories(src_dir, dest_dir):
    """將 src_dir 的所有檔案移動到 dest_dir，然後刪除 src_dir"""
    if not os.path.exists(src_dir):
        return 0

    os.makedirs(dest_dir, exist_ok=True)
    moved_count = 0

    try:
        for filename in os.listdir(src_dir):
            src_file = os.path.join(src_dir, filename)
            dest_file = os.path.join(dest_dir, filename)

            if os.path.isfile(src_file):
                shutil.move(src_file, dest_file)
                moved_count += 1

        # 刪除空目錄
        try:
            os.rmdir(src_dir)
        except:
            pass
    except Exception as e:
        print(f"❌ 錯誤移動 {os.path.basename(src_dir)}: {e}")

    return moved_count

def main():
    print("=" * 70)
    print("🌍 標準化所有國家的城市名稱為中文")
    print("=" * 70)
    print()

    total_moved = 0

    for country, city_map in COUNTRY_CITY_MAPS.items():
        country_dir = os.path.join(WIKI_DIR, country)

        if not os.path.exists(country_dir):
            continue

        print(f"📍 {country}")
        country_moved = 0

        for old_name, new_name in city_map.items():
            old_dir = os.path.join(country_dir, old_name)

            if os.path.exists(old_dir) and old_name != new_name:
                new_dir = os.path.join(country_dir, new_name)
                moved = merge_directories(old_dir, new_dir)
                if moved > 0:
                    print(f"   ✅ {old_name} → {new_name}: {moved} 個檔案")
                    country_moved += moved

        # 處理特殊情況（合併未知目錄）
        if country in SPECIAL_HANDLING:
            for old_name, new_name in SPECIAL_HANDLING[country].items():
                old_dir = os.path.join(country_dir, old_name)

                if os.path.exists(old_dir):
                    new_dir = os.path.join(country_dir, new_name)
                    moved = merge_directories(old_dir, new_dir)
                    if moved > 0:
                        print(f"   ✅ {old_name} → {new_name}: {moved} 個檔案")
                        country_moved += moved

        if country_moved > 0:
            print(f"   📊 {country} 小計: {country_moved} 個檔案")
            total_moved += country_moved

        print()

    print("=" * 70)
    print(f"✅ 完成！總共移動 {total_moved} 個檔案")
    print("=" * 70)

if __name__ == "__main__":
    main()
