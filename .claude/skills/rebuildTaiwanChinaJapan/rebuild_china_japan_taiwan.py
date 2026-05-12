#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 KML 完整地理編碼並重建台灣、中國、日本目錄結構
Skill: /rebuildTaiwanChinaJapan

二級目錄結構：
- wiki/台灣/{縣市}/{鄉鎮市區}/
- wiki/中國/{省份}/{城市}/
- wiki/日本/{都道府縣}/{市區町村}/

每 10 秒報告進度
"""

import os
import sys
import io
import re
import json
import time
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
GEOJSON_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wgii\data"

# 中國省份座標中心（用於地理編碼）
CHINA_PROVINCES = {
    "北京市": (116.4074, 39.9042),
    "上海市": (121.4737, 31.2304),
    "天津市": (117.2008, 39.0842),
    "重慶市": (106.5516, 29.5630),
    "河北省": (114.5149, 38.0456),
    "山西省": (112.5489, 37.8739),
    "遼寧省": (123.4328, 41.8045),
    "吉林省": (125.3245, 44.0065),
    "黑龍江省": (126.6424, 45.7520),
    "江蘇省": (120.5954, 32.9697),
    "浙江省": (120.1551, 30.2741),
    "安徽省": (117.2272, 31.8604),
    "福建省": (119.2965, 26.0745),
    "江西省": (115.8581, 28.6834),
    "山東省": (117.1205, 36.6519),
    "河南省": (113.6254, 34.7466),
    "湖北省": (114.3055, 30.5933),
    "湖南省": (112.9388, 28.2282),
    "廣東省": (113.2644, 23.1291),
    "廣西壯族自治區": (108.3660, 22.8170),
    "海南省": (110.3312, 19.8318),
    "四川省": (104.0666, 30.5728),
    "貴州省": (106.7139, 26.5783),
    "雲南省": (102.8329, 24.8801),
    "西藏自治區": (91.1174, 29.6470),
    "陝西省": (108.9398, 34.3416),
    "甘肅省": (103.8343, 36.0611),
    "青海省": (101.7782, 36.6175),
    "寧夏回族自治區": (106.2786, 38.4680),
    "新疆維吾爾自治區": (87.6278, 43.7930),
    "內蒙古自治區": (111.7088, 47.5140),
}

# 台灣縣市座標中心
TAIWAN_COUNTIES = {
    "台北市": (121.5654, 25.0330),
    "新北市": (121.4657, 24.9871),
    "基隆市": (121.7081, 25.1283),
    "桃園市": (121.3010, 24.9936),
    "新竹市": (120.9647, 24.8138),
    "新竹縣": (121.0000, 24.7000),
    "苗栗縣": (120.8200, 24.5602),
    "台中市": (120.6736, 24.1477),
    "彰化縣": (120.5387, 23.9936),
    "南投縣": (120.6780, 23.8241),
    "雲林縣": (120.3900, 23.7200),
    "嘉義市": (120.4294, 23.4801),
    "嘉義縣": (120.4490, 23.4000),
    "台南市": (120.2270, 22.9998),
    "高雄市": (120.3133, 22.6273),
    "屏東縣": (120.4903, 22.5519),
    "宜蘭縣": (121.7195, 24.6969),
    "花蓮縣": (121.6011, 23.9871),
    "台東縣": (121.1441, 22.7972),
    "澎湖縣": (119.5793, 23.5710),
    "金門縣": (118.3170, 24.4493),
    "連江縣": (119.9400, 26.1605),
}

# 日本都道府縣座標中心
JAPAN_PREFECTURES_COORDS = {
    "北海道": (142.8635, 44.1693),
    "青森県": (140.7674, 40.8246),
    "岩手県": (141.1468, 39.6917),
    "宮城県": (140.8694, 38.2688),
    "秋田県": (140.8025, 39.7201),
    "山形県": (140.3733, 38.2408),
    "福島県": (140.4730, 37.7503),
    "茨城県": (140.4469, 36.3415),
    "栃木県": (139.8807, 36.5652),
    "群馬県": (139.0604, 36.7394),
    "埼玉県": (139.6289, 35.8617),
    "千葉県": (140.1232, 35.6047),
    "東京都": (139.6917, 35.6895),
    "神奈川県": (139.6917, 35.4437),
    "新潟県": (138.8621, 37.9185),
    "富山県": (137.2108, 36.6953),
    "石川県": (136.5761, 36.5946),
    "福井県": (136.2261, 36.0640),
    "山梨県": (138.5689, 35.6640),
    "長野県": (137.2606, 36.6513),
    "岐阜県": (137.0394, 35.3910),
    "愛知県": (137.0705, 35.1105),
    "三重県": (136.5169, 34.7306),
    "滋賀県": (136.0850, 35.0081),
    "京都府": (135.7581, 35.0116),
    "大阪府": (135.5023, 34.6937),
    "兵庫県": (135.1955, 34.6901),
    "奈良県": (135.8048, 34.6852),
    "和歌山県": (135.1657, 33.9204),
    "鳥取県": (134.2381, 35.5040),
    "島根県": (132.4614, 35.2296),
    "岡山県": (133.9339, 34.6639),
    "広島県": (132.4727, 34.3853),
    "山口県": (131.4707, 34.1856),
    "徳島県": (134.5598, 33.9042),
    "香川県": (134.0434, 34.3397),
    "愛媛県": (132.7655, 33.8412),
    "高知県": (133.5309, 33.5614),
    "福岡県": (130.4017, 33.5904),
    "佐賀県": (130.2997, 33.2490),
    "長崎県": (129.8737, 32.7503),
    "熊本県": (130.7355, 32.7898),
    "大分県": (131.1212, 33.2381),
    "宮崎県": (131.4233, 31.9111),
    "鹿児島県": (130.5494, 31.5628),
    "沖縄県": (127.6809, 26.2124),
}

def parse_kml():
    """解析 KML 檔案"""
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

        if coords_elem is not None and coords_elem.text and name:
            try:
                lng, lat = map(float, coords_elem.text.strip().split(',')[:2])
                pois.append({
                    'name': name,
                    'lng': lng,
                    'lat': lat,
                })
            except ValueError:
                pass

    return pois

def distance(p1, p2):
    """計算兩點之間的距離（簡化版）"""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def geocode_poi(poi):
    """對 POI 進行地理編碼，返回國家、區域1、區域2"""
    lng, lat = poi['lng'], poi['lat']

    # 台灣範圍: 120° ~ 122°E, 22° ~ 26°N
    if 120 <= lng <= 122 and 22 <= lat <= 26:
        # 找到最近的台灣縣市
        min_dist = float('inf')
        nearest_county = None
        for county, coord in TAIWAN_COUNTIES.items():
            d = distance((lng, lat), coord)
            if d < min_dist:
                min_dist = d
                nearest_county = county

        return {
            'country': '台灣',
            'region1': nearest_county or '未分類',
            'region2': '其他',
        }

    # 中國範圍: 73° ~ 135°E, 18° ~ 54°N（但排除台灣）
    elif 73 <= lng <= 135 and 18 <= lat <= 54 and not (120 <= lng <= 122 and 22 <= lat <= 26):
        # 找到最近的中國省份
        min_dist = float('inf')
        nearest_province = None
        for province, coord in CHINA_PROVINCES.items():
            d = distance((lng, lat), coord)
            if d < min_dist:
                min_dist = d
                nearest_province = province

        return {
            'country': '中國',
            'region1': nearest_province or '未分類',
            'region2': '其他',
        }

    # 日本範圍: 130° ~ 145°E, 30° ~ 46°N
    elif 130 <= lng <= 145 and 30 <= lat <= 46:
        # 找到最近的日本都道府縣
        min_dist = float('inf')
        nearest_pref = None
        for pref, coord in JAPAN_PREFECTURES_COORDS.items():
            d = distance((lng, lat), coord)
            if d < min_dist:
                min_dist = d
                nearest_pref = pref

        return {
            'country': '日本',
            'region1': nearest_pref or '未分類',
            'region2': '其他',
        }

    return None

def create_md_file(country, region1, region2, poi_name, lng, lat):
    """創建 POI 的 Markdown 檔案"""
    # 創建目錄
    dir_path = Path(WIKI_DIR) / country / region1 / region2
    dir_path.mkdir(parents=True, exist_ok=True)

    # 淨化檔案名（移除換行符和特殊字符）
    safe_name = re.sub(r'[\n\r\t\\/:*?"<>|]', '', poi_name).strip()
    if not safe_name:
        safe_name = "未命名"

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
**區域:** {region1} / {region2}

## 基本資訊

## 備註

"""

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(file_path)
    except Exception as e:
        return None

def main():
    print("🌍 重建中國和日本目錄（完整地理編碼）")
    print("=" * 60)

    # 解析 KML
    print("📖 解析 KML...")
    pois = parse_kml()
    print(f"✓ 載入 {len(pois)} 個 POI\n")

    # 地理編碼和重建
    print("🗺️ 進行地理編碼和重建...")

    taiwan_count = 0
    china_count = 0
    japan_count = 0
    other_count = 0
    created_count = 0

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
                  f"台{taiwan_count:4d} 中{china_count:4d} 日{japan_count:4d} 其他{other_count:4d} | " +
                  f"已建{created_count:4d} | 預計剩餘: {remaining:.0f}s")
            sys.stdout.flush()
            last_report = current_time

        # 地理編碼
        geocoded = geocode_poi(poi)

        if geocoded:
            if geocoded['country'] == '台灣':
                taiwan_count += 1
            elif geocoded['country'] == '中國':
                china_count += 1
            elif geocoded['country'] == '日本':
                japan_count += 1

            # 創建檔案
            result = create_md_file(
                geocoded['country'],
                geocoded['region1'],
                geocoded['region2'],
                poi['name'],
                poi['lng'],
                poi['lat']
            )
            if result:
                created_count += 1
        else:
            other_count += 1

    # 最終報告
    elapsed_total = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"✓ 台灣 POI: {taiwan_count}")
    print(f"✓ 中國 POI: {china_count}")
    print(f"✓ 日本 POI: {japan_count}")
    print(f"✓ 其他國家: {other_count}")
    print(f"✓ 已創建檔案: {created_count}/{taiwan_count + china_count + japan_count}")
    print(f"✓ 執行時間: {elapsed_total:.1f}s")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
