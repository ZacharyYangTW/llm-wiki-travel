#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據座標和正確的行政區劃重新組織台灣和日本檔案
台灣: wiki/台灣/{縣市}/{鄉鎮市區}/
日本: wiki/日本/{都道府縣}/{市區町村}/
"""

import os
import sys
import re
import shutil
import math
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# ============================================================================
# 台灣行政區劃（縣市及鄉鎮市區中心座標）
# ============================================================================
TAIWAN_DISTRICTS = {
    "台北市": {
        "中正區": (121.5098, 25.0273),
        "大安區": (121.5362, 25.0233),
        "信義區": (121.5662, 25.0380),
        "松山區": (121.5450, 25.0532),
        "南港區": (121.5779, 25.0530),
        "東興區": (121.5650, 25.0650),
        "中山區": (121.5253, 25.0652),
        "松江區": (121.5132, 25.0780),
        "大同區": (121.5087, 25.0715),
        "士林區": (121.5104, 25.1091),
        "北投區": (121.5035, 25.1374),
        "內湖區": (121.5800, 25.0878),
    },
    "新北市": {
        "板橋": (121.4596, 25.0110),
        "新莊": (121.4317, 25.0558),
        "泰山": (121.4168, 25.0770),
        "林口": (121.3710, 25.0825),
        "蘆洲": (121.4867, 25.0862),
        "五股": (121.4348, 25.0665),
        "新店": (121.5403, 24.9753),
        "安坡": (121.4943, 25.0254),
        "中和": (121.4978, 24.9932),
        "永和": (121.5138, 25.0170),
        "汐止": (121.6493, 25.0678),
        "貢寮": (121.8246, 25.0127),
        "瑞芳": (121.8085, 25.1088),
        "平溪": (121.7289, 25.0148),
        "金山": (121.6286, 25.2237),
        "萬里": (121.6859, 25.1956),
        "石碇": (121.6648, 24.9490),
        "深坑": (121.6128, 24.9667),
        "坪林": (121.7267, 24.9392),
        "烏來": (121.7191, 24.8488),
    },
    "台中市": {
        "中區": (120.6660, 24.1395),
        "東區": (120.6899, 24.1530),
        "南區": (120.6531, 24.1201),
        "西區": (120.6451, 24.1370),
        "北區": (120.6620, 24.1620),
        "西屯區": (120.6212, 24.1763),
        "南屯區": (120.6374, 24.1079),
        "北屯區": (120.6969, 24.1857),
        "豐原": (120.7457, 24.2585),
        "東勢": (120.8295, 24.2624),
        "太平": (120.7583, 24.1079),
        "烏日": (120.6898, 24.0631),
        "大里": (120.7220, 24.0919),
        "霧峰": (120.8046, 24.0614),
        "石岡": (120.8687, 24.2244),
        "新社": (120.7876, 24.2195),
        "和平": (120.8621, 24.3687),
        "潭子": (120.6869, 24.1924),
        "龍井": (120.5989, 24.1919),
        "大安": (120.6014, 24.2840),
        "外埔": (120.5816, 24.2416),
        "后里": (120.6997, 24.2996),
    },
    "台南市": {
        "中西區": (120.2026, 22.9939),
        "東區": (120.2264, 22.9989),
        "南區": (120.1989, 22.9516),
        "北區": (120.2227, 23.0394),
        "安平": (120.1631, 22.9845),
        "永康": (120.2315, 22.9417),
        "歸仁": (120.2742, 22.9197),
        "仁德": (120.2783, 22.8882),
        "關子嶺": (120.3456, 22.8012),
        "新化": (120.3076, 22.9065),
        "善化": (120.2919, 22.8543),
        "大內": (120.4064, 22.8845),
        "山上": (120.3911, 22.9312),
        "玉井": (120.3865, 22.8110),
        "南化": (120.4485, 22.8454),
        "左鎮": (120.3908, 22.7957),
        "六甲": (120.4234, 23.0087),
        "官田": (120.3654, 23.1543),
        "麻豆": (120.2399, 23.1769),
        "下營": (120.3157, 23.2265),
        "柳營": (120.3650, 23.2730),
        "後壁": (120.4286, 23.3284),
        "白河": (120.4292, 23.3555),
        "東山": (120.4989, 23.1826),
        "五十間": (120.3125, 23.0825),
        "西港": (120.1804, 23.0425),
        "七股": (120.0986, 22.9936),
        "將軍": (120.1398, 23.0718),
        "北門": (120.0739, 23.1765),
    },
    "高雄市": {
        "新興": (120.3117, 22.6191),
        "前金": (120.3019, 22.6049),
        "苓雅": (120.3069, 22.5925),
        "鹽埕": (120.2915, 22.6214),
        "鼓山": (120.2860, 22.6482),
        "旗津": (120.2740, 22.6058),
        "前鎮": (120.3200, 22.5577),
        "小港": (120.3461, 22.5634),
        "三民": (120.3287, 22.5935),
        "楠梓": (120.3367, 22.7017),
        "左營": (120.3030, 22.6952),
        "仁武": (120.3573, 22.7196),
        "大社": (120.4167, 22.6802),
        "岡山": (120.3505, 22.6918),
        "路竹": (120.3637, 22.6525),
        "阿蓮": (120.3975, 22.6299),
        "田寮": (120.4450, 22.6599),
        "燕巢": (120.4689, 22.6984),
        "茄萣": (120.2893, 22.5127),
        "永安": (120.2598, 22.5343),
        "梓官": (120.3026, 22.5443),
        "彌陀": (120.3436, 22.5286),
        "旗山": (120.4814, 22.7945),
        "美濃": (120.5549, 22.8860),
        "六龜": (120.6494, 22.8283),
        "甲仙": (120.6927, 22.8926),
        "杉林": (120.6203, 22.9402),
        "內門": (120.5767, 22.8233),
        "桃源": (120.7329, 23.0169),
        "那瑪夏": (120.7619, 23.0619),
        "茂林": (120.6818, 22.9047),
        "寶邊": (120.6389, 22.7869),
    },
    "連江縣": {
        "南竿鄉": (119.9563, 26.1573),
        "北竿鄉": (119.9994, 26.2236),
        "莒光鄉": (119.9282, 26.3694),
        "東引鄉": (120.0637, 26.3847),
    },
    "金門縣": {
        "金城鎮": (118.3273, 24.4354),
        "金湖鎮": (118.3897, 24.4433),
        "金沙鎮": (118.4135, 24.4734),
        "金寧鄉": (118.3789, 24.4734),
        "烈嶼鄉": (118.2896, 24.3814),
        "烏坵鄉": (118.1667, 24.2667),
    },
}

def extract_coordinates(file_path):
    """從檔案中提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return (lng, lat)
    except:
        pass
    return None

def find_nearest_district(coords):
    """找到最近的行政區"""
    if not coords:
        return None, None

    min_distance = float('inf')
    nearest_county = None
    nearest_district = None

    for county, districts in TAIWAN_DISTRICTS.items():
        for district, (d_lng, d_lat) in districts.items():
            distance = math.sqrt((coords[0] - d_lng)**2 + (coords[1] - d_lat)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_county = county
                nearest_district = district

    return nearest_county, nearest_district

def restructure_taiwan():
    """重新組織台灣檔案"""
    moved_count = 0
    file_count = 0
    coords_found = 0
    no_match = 0

    taiwan_path = os.path.join(WIKI_DIR, "台灣")

    # 遞迴掃描所有目錄中的 .md 檔案
    for root, dirs, files in os.walk(taiwan_path):
        for filename in files:
            if filename.endswith('.md'):
                file_path = os.path.join(root, filename)
                coords = extract_coordinates(file_path)
                file_count += 1

                if coords:
                    coords_found += 1
                    correct_county, correct_district = find_nearest_district(coords)

                    if correct_county and correct_district:
                        # 建立正確的目錄
                        target_dir = os.path.join(taiwan_path, correct_county, correct_district)
                        os.makedirs(target_dir, exist_ok=True)

                        # 移動檔案
                        target_path = os.path.join(target_dir, filename)
                        if target_path != file_path:  # 確保不會複製到自己
                            try:
                                shutil.move(file_path, target_path)
                                moved_count += 1

                                if moved_count % 100 == 0:
                                    print(f"  進度: {moved_count} 個檔案已移動...")
                            except Exception as e:
                                print(f"  ❌ 錯誤移動: {filename} - {e}")
                    else:
                        no_match += 1

    print(f"  📊 掃描統計: {file_count} 檔案, {coords_found} 有座標, {no_match} 無法匹配")
    return moved_count

def main():
    print("=" * 70)
    print("🗺️ 根據正確的行政區劃重新組織")
    print("=" * 70)
    print()

    print("🇹🇼 台灣 - 重組為: wiki/台灣/{縣市}/{鄉鎮市區}/")
    taiwan_moved = restructure_taiwan()
    print(f"  ✅ 台灣: {taiwan_moved} 個檔案")
    print()

    # 清理空目錄
    taiwan_path = os.path.join(WIKI_DIR, "台灣")
    for county in os.listdir(taiwan_path):
        county_path = os.path.join(taiwan_path, county)
        if not os.path.isdir(county_path):
            continue

        for district in list(os.listdir(county_path)):
            district_path = os.path.join(county_path, district)
            if os.path.isdir(district_path) and not os.listdir(district_path):
                try:
                    os.rmdir(district_path)
                except:
                    pass

    print("=" * 70)
    print(f"✅ 完成！台灣: {taiwan_moved} 個檔案正確分類")
    print("=" * 70)

if __name__ == "__main__":
    main()
