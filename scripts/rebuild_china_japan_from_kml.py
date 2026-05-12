#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 中重新提取中國和日本的 POI，重建目錄結構
"""

import os
import sys
import io
import re
import json
from pathlib import Path
from datetime import datetime

# 修復 Windows 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# 路徑設定
KML_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"
WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

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

def parse_kml():
    """解析 KML 文件"""
    if not os.path.exists(KML_PATH):
        print(f"❌ KML 檔案不存在: {KML_PATH}")
        return []

    try:
        parser = ET.XMLParser(recover=True)
        tree = ET.parse(KML_PATH, parser)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ 無法解析 KML: {e}")
        return []

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    pois = []

    for placemark in root.findall(".//kml:Placemark", ns):
        name = placemark.findtext(".//kml:name", "", ns)
        coords_elem = placemark.find(".//kml:Point/kml:coordinates", ns)
        desc = placemark.findtext(".//kml:description", "", ns)

        if coords_elem is not None and coords_elem.text:
            try:
                lng, lat = map(float, coords_elem.text.strip().split(',')[:2])
                pois.append({
                    'name': name,
                    'lng': lng,
                    'lat': lat,
                    'description': desc
                })
            except ValueError:
                pass

    return pois

def classify_country(lng, lat):
    """根據座標判斷國家"""
    # 中國大陸: 73° ~ 135°E, 18° ~ 54°N
    if 73 <= lng <= 135 and 18 <= lat <= 54:
        return "中國"
    # 日本: 130° ~ 145°E, 30° ~ 46°N
    elif 130 <= lng <= 145 and 30 <= lat <= 46:
        return "日本"
    return None

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

def create_md_file(country, province, city, poi_name, lng, lat):
    """創建 POI 的 Markdown 檔案"""
    # 創建目錄
    dir_path = Path(WIKI_DIR) / country / province / city
    dir_path.mkdir(parents=True, exist_ok=True)

    # 創建檔案名（處理特殊字符和換行符）
    safe_name = re.sub(r'[\n\r\t\\/:*?"<>|]', '', poi_name).strip()
    file_path = dir_path / f"{safe_name}.md"

    # 檢查是否已存在
    if file_path.exists():
        return None

    # 創建 Markdown 內容
    content = f"""---
name: {poi_name}
type: place
coordinates: [{lng}, {lat}]
created_at: {datetime.now().isoformat()}
---

# {poi_name}

**座標:** {lat:.4f}, {lng:.4f}
**國家:** {country}
**省份/州:** {province}
**城市:** {city}

## 基本資訊

## 備註

"""

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(file_path)
    except Exception as e:
        print(f"❌ 無法創建檔案 {file_path}: {e}")
        return None

def main():
    import time

    print("🌍 從 KML 重建中國和日本目錄")
    print("=" * 60)

    # 解析 KML
    print("📖 解析 KML...")
    pois = parse_kml()
    print(f"✓ 載入 {len(pois)} 個 POI")

    # 分類
    china_count = 0
    japan_count = 0
    other_count = 0
    created_count = 0

    print("\n📍 分類 POI...")

    start_time = time.time()
    last_report = start_time

    for i, poi in enumerate(pois, 1):
        # 每 10 秒報告進度
        current_time = time.time()
        if current_time - last_report >= 10:
            elapsed = current_time - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (len(pois) - i) / rate if rate > 0 else 0
            print(f"⏱️ [{elapsed:6.1f}s] 進度: {i:5d}/{len(pois)} ({i/len(pois)*100:5.1f}%) | " +
                  f"中{china_count:4d} 日{japan_count:4d} 其他{other_count:4d} | " +
                  f"已建{created_count:4d} | 預計剩餘: {remaining:.0f}s")
            sys.stdout.flush()
            last_report = current_time

        country = classify_country(poi['lng'], poi['lat'])

        if country == "中國":
            china_count += 1
            # 獲取省份
            province = get_province_from_kml_desc(poi['description'], country)
            if province is None:
                # 預設為未分類
                province = "未分類"
                city = "其他"
            else:
                city = "其他"

            result = create_md_file(country, province, city, poi['name'], poi['lng'], poi['lat'])
            if result:
                created_count += 1

        elif country == "日本":
            japan_count += 1
            # 獲取都道府県
            prefecture = get_province_from_kml_desc(poi['description'], country)
            if prefecture is None:
                prefecture = "未分類"
                city = "其他"
            else:
                city = "其他"

            result = create_md_file(country, prefecture, city, poi['name'], poi['lng'], poi['lat'])
            if result:
                created_count += 1

        else:
            other_count += 1

    print(f"\n✓ 中國 POI: {china_count}")
    print(f"✓ 日本 POI: {japan_count}")
    print(f"✓ 其他國家: {other_count}")
    print(f"\n✓ 已創建 {created_count} 個檔案")
    print("=" * 60)

if __name__ == "__main__":
    main()
