#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 中重新提取 POI，使用 GeoJSON 精確定位，重建目錄結構
用法：python rebuild_china_japan_from_kml.py country=japan
"""

import os
import sys
import io
import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 修復 Windows 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# 導入共通進度回報工具
from progress_reporter import ProgressReporter

# 導入共通函數庫
_SCRIPT_DIR = Path(__file__).resolve().parent  # Allfiles/scripts
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent  # e:\llm_wiki_travel
sys.path.insert(0, str(_PROJECT_ROOT / ".claude" / "skills" / "COMMON"))
from geojson_utils import (
    point_in_polygon,
    load_geojson_municipalities,
    find_municipality_by_geojson,
    parse_kml as parse_kml_util,
    extract_kml_coords,
    create_wiki_file,
)

# 路徑設定（動態計算）
KML_PATH = str(_PROJECT_ROOT / "Allfiles" / "raw" / "travel" / "Zachary's World Trip_fixed.kml")
WIKI_DIR = str(_PROJECT_ROOT / "Allfiles" / "wiki")

GEOJSON_PATHS = {
    'japan': str(_PROJECT_ROOT / "japan-topography" / "data" / "municipality" / "geojson" / "s0001" / "N03-21_210101.json"),
}

# 中國省份和城市映射
CITY_TO_PROVINCE = {
    "北京": "北京市", "上海": "上海市", "天津": "天津市", "重慶": "重慶市",
    "唐山市": "河北省", "承德市": "河北省", "秦皇島市": "河北省",
    "大同": "山西省", "晉中市": "山西省",
    "呼和浩特市": "內蒙古自治區",
    "瀋陽": "遼寧省",
    "哈爾濱": "黑龍江省",
    "南京市": "江蘇省", "蘇州": "江蘇省", "蘇州市": "江蘇省",
    "杭州": "浙江省", "嘉興市": "浙江省",
    "合肥市": "安徽省", "蕪湖市": "安徽省",
    "福州市": "福建省", "廈門": "福建省", "廈門市": "福建省",
    "南昌市": "江西省",
    "泰安": "山東省", "泰安市": "山東省",
    "鄭州": "河南省", "鄭州市": "河南省", "洛陽": "河南省", "開封": "河南省", "安陽市": "河南省",
    "武汉市": "湖北省", "武漢市": "湖北省",
    "長沙": "湖南省", "長沙市": "湖南省", "岳陽市": "湖南省",
    "廣州市": "廣東省", "深圳市": "廣東省", "珠海市": "廣東省", "中山市": "廣東省", "韶關市": "廣東省",
    "南寧市": "廣西壯族自治區",
    "海口市": "海南省",
    "拉薩": "西藏自治區", "拉薩市": "西藏自治區",
    "成都": "四川省",
    "貴陽": "貴州省",
    "昆明": "雲南省", "昆明市": "雲南省",
    "蘭州": "甘肅省", "蘭州市": "甘肅省",
    "銀川": "寧夏回族自治區",
    "烏魯木齊": "新疆維吾爾自治區",
    "西寧": "青海省",
}

# 日本都道府県映射
JAPAN_PREFECTURES = {
    "北海道": "北海道",
    "青森県": "東北地方",
    "岩手県": "東北地方",
    "宮城県": "東北地方",
    "秋田県": "東北地方",
    "山形県": "東北地方",
    "福島県": "東北地方",
    "茨城県": "關東地方",
    "栃木県": "關東地方",
    "群馬県": "關東地方",
    "埼玉県": "關東地方",
    "千葉県": "關東地方",
    "東京都": "關東地方",
    "神奈川県": "關東地方",
    "新潟県": "中部地方",
    "富山県": "中部地方",
    "石川県": "中部地方",
    "福井県": "中部地方",
    "山梨県": "中部地方",
    "長野県": "中部地方",
    "岐阜県": "中部地方",
    "愛知県": "中部地方",
    "三重県": "近畿地方",
    "滋賀県": "近畿地方",
    "京都府": "近畿地方",
    "大阪府": "近畿地方",
    "兵庫県": "近畿地方",
    "奈良県": "近畿地方",
    "和歌山県": "近畿地方",
    "鳥取県": "中國地方",
    "島根県": "中國地方",
    "岡山県": "中國地方",
    "広島県": "中國地方",
    "山口県": "中國地方",
    "徳島県": "四國地方",
    "香川県": "四國地方",
    "愛媛県": "四國地方",
    "高知県": "四國地方",
    "福岡県": "九州地方",
    "佐賀県": "九州地方",
    "長崎県": "九州地方",
    "熊本県": "九州地方",
    "大分県": "九州地方",
    "宮崎県": "九州地方",
    "鹿児島県": "九州地方",
    "沖縄県": "沖縄",
}

# point_in_polygon() 已移到共通庫 geojson_utils.py

# load_geojson_municipalities() 已移到共通庫 geojson_utils.py

# find_municipality_by_geojson() 已移到共通庫 geojson_utils.py

# parse_kml() 已用共通庫 parse_kml() 替代

# classify_country() 已用共通庫 classify_country_by_coords() 替代

def get_province_from_kml_desc(desc, country):
    """從 KML 描述中提取省份資訊"""
    if not desc:
        return None

    if country == "中國":
        # 嘗試從描述中找到省份名稱
        for city, province in CITY_TO_PROVINCE.items():
            if city in desc:
                return province
    elif country == "日本":
        # 嘗試從描述中找到都道府縣
        for pref in JAPAN_PREFECTURES.keys():
            if pref in desc:
                return pref

    return None

# create_md_file() 已用共通庫 create_wiki_file() 替代

def main():
    # 解析參數
    country = 'japan'
    for arg in sys.argv[1:]:
        if arg.startswith('country='):
            country = arg.split('=')[1].lower()

    if country not in GEOJSON_PATHS:
        print(f"❌ 不支持的國家: {country}")
        print(f"支持的國家: {', '.join(GEOJSON_PATHS.keys())}")
        return

    # 建立 log 檔案
    log_file = Path(_PROJECT_ROOT) / "Allfiles" / "outputs" / f"rebuild_{country}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"執行時間: {datetime.now().isoformat()}\n")
        log.write(f"國家: {country}\n")
        log.write("=" * 60 + "\n\n")

    print("=" * 60)
    print(f"🌍 從 KML 重建 {country.upper()} 目錄（使用 GeoJSON）")
    print(f"📝 Log: {log_file}")
    print("=" * 60)

    # 載入 GeoJSON
    print(f"\n📖 載入 {country} GeoJSON...")
    municipalities = load_geojson_municipalities(GEOJSON_PATHS[country])
    if not municipalities:
        print("❌ 無法載入邊界")
        return
    print(f"✓ 載入 {len(municipalities)} 個市區町村邊界")

    # 解析 KML
    print("\n📖 解析 KML...")
    pois = parse_kml_util(KML_PATH)
    print(f"✓ 載入 {len(pois)} 個 POI")

    # 篩選該國家的 POI
    country_name = "日本" if country == "japan" else country
    country_pois = []
    for poi in pois:
        result = find_municipality_by_geojson((poi['lng'], poi['lat']), municipalities)
        if result:
            country_pois.append((poi, result))

    print(f"✓ 該國家 POI: {len(country_pois)} 個")

    # 建立檔案
    print(f"\n📝 建立 {country} 檔案...\n")

    reporter = ProgressReporter(total=len(country_pois), name=f"{country} wiki 檔案建立")

    for poi, (prefecture, municipality) in country_pois:
        result = create_wiki_file(country_name, prefecture, municipality, poi['name'], poi['lng'], poi['lat'], WIKI_DIR)
        if result:
            reporter.update(created=1)
        else:
            reporter.update(failed=1)

    reporter.finish()

if __name__ == "__main__":
    main()
