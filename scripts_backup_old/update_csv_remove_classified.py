#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 CSV 中移除已經分類的項目
"""

import os
import sys
import csv
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 已分類的檔案名稱列表（這 51 個）
CLASSIFIED_TITLES = [
    "巴黎夏爾·戴高樂機場",
    "citizenM Paris Charles de Gaulle",
    "Helzear Champs Elysées",
    "Châtelet - Les Halles",
    "Gare de Versailles Château Rive Gauche",
    "阿道弗·蘇亞雷斯馬德里-巴拉哈斯機場",
    "Apartasol Zona Sol",
    "Moncloa",
    "Atocha Renfe",
    "Oficina de Correos",
    "Girona",
    "Estacion tren tarragona",
    "Baan Khun Krub",
    "Nádraží Veleslavín (Metro A)",
    "K9 Residence",
    "Arany János utca M",
    "Buda Castle Funicular (下)",
    "Q-Park P+R Meerssenerweg",
    "Maastricht, Markt 市場站",
    "Utrecht Centraal",
    "Luxembourg Flixbus",
    "Empire",
    "Arlon 中轉站",
    "Gent Korenmarkt perron 5",
    "Gent Brugsepoort",
    "Gent Burgstraat",
    "Rotterdam Centraal",
    "Rotterdam Blaak",
    "Rotterdam, Erasmusbrug",
    "Ridderkerk, De Schans轉乘站",
    "Kinderdijk, Molenkade",
    "Giethoorn, Hollands Venetië",
    "Amsterdam Sloterdijk",
    "真駒内滝野霊園[中央バス]",
    "伊達政宗陣跡[海青中學前]",
    "富基漁港觀光漁市",
    "石門洞",
    "新店-燦坤",
    "丸作食茶",
    "鐘鼓樓",
    "加州乾洗",
    "ダイコクドラッグ 北谷アメリカンビレッジ店",
    "FamilyMart Nahakuko Terminal",
    "綜合案內所",
    "cafe OCEAN BLUE",
    "熱帯ドリームセンター",
    "Sea Turtle Pool",
    "海牛館",
    "ローソン 那覇ハーバービュー通店",
    "OKINAWA OUTLET MALL ASHIBINAA",
    "古坑服務區",
]

def main():
    print("=" * 70)
    print("🗂️ 從 CSV 中移除已分類的項目")
    print("=" * 70)
    print()

    # 讀取 CSV
    rows = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return

    print(f"原始行數: {len(rows)}")

    # 過濾出未分類的項目（標題不在已分類列表中，或城市/國家為空）
    unclassified_rows = []
    classified_count = 0

    for row in rows:
        title = row['標題'].strip()

        # 如果標題在已分類列表中，跳過
        if title in CLASSIFIED_TITLES:
            classified_count += 1
            print(f"  ✓ 移除: {title}")
            continue

        unclassified_rows.append(row)

    print()
    print(f"已分類（已移除）: {classified_count} 個")
    print(f"未分類（保留）: {len(unclassified_rows)} 個")
    print()

    # 寫回 CSV
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
            writer.writeheader()
            writer.writerows(unclassified_rows)

        print(f"✅ CSV 已更新")
        print("=" * 70)
    except Exception as e:
        print(f"❌ 寫入 CSV 失敗: {e}")
        return

if __name__ == "__main__":
    main()
