#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終清理：處理所有剩餘的根目錄 .md 檔案
"""

import os
import sys
import re
import shutil
import math
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 各國城市中心（完整版）
CITY_CENTERS = {
    '中國': {
        '北京': (116.4074, 39.9042),
        '上海': (121.4737, 31.2304),
        '廣州': (113.2644, 23.1291),
        '西安': (108.9398, 34.3416),
        '成都': (104.0660, 30.5728),
        '敦煌': (100.7500, 40.1500),
        '麗江': (100.2324, 26.8154),
        '拉薩': (91.1173, 29.6470),
        '蘭州': (103.8343, 36.0611),
        '昆明': (102.7103, 24.8801),
        '杭州': (120.1538, 30.2741),
        '南京': (118.7969, 32.0603),
        '武漢': (114.3055, 30.5928),
        '重慶': (106.5516, 29.5630),
        '福州': (119.2965, 26.0745),
        '廈門': (118.0894, 24.4798),
        '南昌': (115.8581, 28.6832),
        '長沙': (112.9388, 28.2282),
        '石家莊': (114.5149, 38.0428),
        '沈陽': (123.4328, 41.8045),
        '哈爾濱': (126.5348, 45.8038),
        '太原': (112.5489, 37.8706),
        '合肥': (117.2272, 31.8654),
        '鄭州': (113.6254, 34.7466),
        '青島': (120.3826, 36.0671),
        '蘇州': (120.5954, 31.2989),
        '寧波': (121.5440, 29.8683),
        '紹興': (120.5954, 30.0042),
        '溫州': (120.6634, 27.9921),
        '嘉興': (120.7610, 30.7667),
        '衢州': (118.8801, 28.9715),
        '金華': (119.6519, 29.1189),
        '麗水': (119.9265, 28.4569),
        '十堰': (110.7975, 32.6254),
        '黃岡': (114.9035, 30.4408),
        '荊門': (112.2021, 31.8357),
        '荊州': (112.2388, 30.3368),
        '咸寧': (114.2997, 29.8683),
        '孝感': (113.9263, 30.8857),
        '宜昌': (111.2868, 30.7032),
        '襄陽': (112.1338, 32.0018),
        '恩施': (109.4872, 30.2755),
        '隨州': (113.3754, 31.7174),
        '黃石': (115.0298, 30.2143),
        '益陽': (112.9388, 28.5749),
        '常德': (111.6388, 29.0402),
        '岳陽': (113.0927, 29.3706),
        '懷化': (109.9787, 27.5500),
        '邵陽': (111.4626, 27.2357),
        '永州': (111.6108, 26.4149),
        '郴州': (113.0227, 25.7938),
        '婁底': (111.9964, 27.7371),
        '株洲': (113.1352, 27.8357),
        '衡陽': (112.6081, 26.8955),
        '南陽': (112.5489, 32.9992),
        '商丘': (115.6394, 34.4365),
        '周口': (114.6491, 33.6201),
        '駐馬店': (114.0211, 32.9797),
        '開封': (114.3055, 34.8038),
        '洛陽': (112.4549, 34.6271),
        '三門峽': (111.1892, 34.7747),
        '安陽': (114.3052, 36.0671),
        '鶴壁': (114.9035, 35.7549),
        '新鄉': (113.8743, 35.3082),
        '焦作': (113.2181, 35.2352),
        '濮陽': (115.0298, 35.7688),
        '漯河': (114.0211, 33.5796),
        '許昌': (113.8445, 34.0288),
        '平頂山': (113.2944, 33.7499),
        '信陽': (114.0788, 32.1198),
        '黑河': (127.4986, 50.2538),
        '綏化': (126.5858, 46.6381),
        '伊春': (130.3826, 47.7282),
        '佳木斯': (130.3598, 46.5891),
        '大慶': (125.1075, 46.5891),
        '齊齊哈爾': (123.9605, 47.3426),
        '牡丹江': (129.5959, 44.5831),
        '雞西': (130.9707, 45.2984),
        '七台河': (131.0101, 45.8038),
        '鶴崗': (130.3000, 47.3554),
        '雙鴨山': (131.1692, 46.6381),
        '阿城': (126.5858, 45.5440),
        '阿木爾': (125.0000, 49.0000),
    },
    '台灣': {
        '台北': (121.5654, 25.0330),
        '基隆': (121.7581, 25.1276),
        '台中': (120.6736, 24.1477),
        '高雄': (120.3133, 22.6273),
        '新北': (121.4657, 24.9871),
    },
    '香港': {
        '香港': (114.1095, 22.3193),
    },
    '澳門': {
        '澳門': (113.5549, 22.1987),
    },
    '菲律賓': {
        '馬尼拉': (120.9842, 14.5995),
        '長灘島': (121.9347, 11.9674),
        '宿務': (123.8854, 10.3157),
    },
    '美國': {
        '紐約': (-74.0060, 40.7128),
        '洛杉磯': (-118.2437, 34.0522),
        '舊金山': (-122.4194, 37.7749),
        '安克雷奇': (-149.9004, 61.2181),
    },
    '加拿大': {
        '多倫多': (-79.3871, 43.6629),
        '溫哥華': (-123.1207, 49.2827),
        '蒙特利爾': (-73.5673, 45.5017),
        '安克雷奇': (-149.9004, 61.2181),
    },
}

def euclidean_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)

def extract_coordinates(md_file):
    """提取坐標"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(COORD_PATTERN, content)
        if match:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return lng, lat
    except:
        pass
    return None, None

def find_nearest_city(lat, lng, country):
    """找該國最近的城市"""
    if country not in CITY_CENTERS:
        return None

    cities = CITY_CENTERS[country]
    min_dist = float('inf')
    best_city = None

    for city_name, (c_lng, c_lat) in cities.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            best_city = city_name

    return best_city

print("=" * 70, flush=True)
print("🔧 最終清理：處理所有剩餘根目錄檔案", flush=True)
print("=" * 70, flush=True)

moved = 0
unclassified = []
failed = []

# 掃描所有國家根目錄
for country in sorted(os.listdir(WIKI_BASE)):
    country_path = os.path.join(WIKI_BASE, country)

    if not os.path.isdir(country_path):
        continue

    # 找出根目錄的 .md 檔案
    root_files = [f for f in os.listdir(country_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(country_path, f))]

    if not root_files:
        continue

    print(f"\n📍 {country} ({len(root_files)} 個根目錄檔案)", flush=True)

    for filename in root_files:
        file_path = os.path.join(country_path, filename)
        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            unclassified.append((country, title))
            print(f"  ⚠️  {title[:40]:<40} [無坐標]", flush=True)
            continue

        # 找最近的城市
        city = find_nearest_city(lat, lng, country)

        if not city:
            unclassified.append((country, title))
            print(f"  ⚠️  {title[:40]:<40} [無城市匹配]", flush=True)
            continue

        # 移動到城市目錄
        try:
            city_dir = os.path.join(country_path, city)
            os.makedirs(city_dir, exist_ok=True)
            target_file = os.path.join(city_dir, filename)

            if os.path.exists(target_file):
                os.remove(target_file)

            shutil.move(file_path, target_file)
            moved += 1
            print(f"  ✓ {title[:40]:<40} → {city}", flush=True)

        except Exception as e:
            failed.append((country, title, str(e)[:30]))
            print(f"  ❌ {title[:40]:<40} {str(e)[:30]}", flush=True)

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  已移動: {moved} 個", flush=True)
print(f"  無法分類: {len(unclassified)} 個", flush=True)
if failed:
    print(f"  失敗: {len(failed)} 個", flush=True)

if unclassified:
    print(f"\n⚠️  無法分類的檔案：", flush=True)
    for country, title in unclassified:
        print(f"  - {country}/{title}", flush=True)

print(f"{'='*70}", flush=True)
