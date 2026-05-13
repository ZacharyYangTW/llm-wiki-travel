#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理中國檔案：將省份根目錄下的直接檔案根據坐標移到城市子目錄
"""

import os
import sys
import re
import shutil
import math
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_CHINA = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\中國"
COORD_PATTERN = r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]'

# 中國主要省份的主要城市中心坐標
CITY_CENTERS = {
    '江蘇省': {
        '南京': (118.7969, 32.0603),
        '蘇州': (120.5954, 31.2989),
        '無錫': (120.3121, 31.4945),
        '常州': (119.9667, 31.7667),
        '徐州': (117.1205, 34.2658),
        '南通': (120.8633, 32.0000),
        '揚州': (119.4290, 32.3934),
        '鎮江': (119.4312, 32.1908),
        '泰州': (119.9265, 32.4509),
        '宿遷': (118.2965, 33.9625),
    },
    '浙江省': {
        '杭州': (120.1551, 30.2875),
        '寧波': (121.5440, 29.8683),
        '嘉興': (120.7500, 30.7667),
        '湖州': (120.0830, 30.8667),
        '紹興': (120.5954, 30.0039),
        '金華': (119.6500, 29.1167),
        '衢州': (118.8667, 28.9333),
        '舟山': (122.1070, 29.9667),
        '臺州': (121.4292, 28.6567),
        '麗水': (119.5333, 28.4500),
    },
    '山東省': {
        '濟南': (117.1205, 36.6519),
        '青島': (120.3826, 36.0671),
        '淄博': (118.0894, 36.8146),
        '棗莊': (117.3272, 34.8926),
        '東營': (118.4653, 37.4386),
        '煙臺': (121.3915, 37.5270),
        '濰坊': (119.1063, 36.7099),
        '濟寧': (116.5885, 35.3375),
        '泰安': (117.0894, 36.1856),
        '威海': (122.1192, 37.5128),
        '日照': (119.4612, 35.4273),
        '聊城': (115.9839, 36.4627),
        '德州': (116.3170, 37.4500),
        '聊城': (115.9839, 36.4627),
        '臨沂': (118.3268, 35.0527),
        '菏澤': (115.4667, 35.2333),
    },
    '福建省': {
        '福州': (119.2965, 26.0745),
        '廈門': (118.0894, 24.4798),
        '漳州': (117.6602, 24.5154),
        '泉州': (118.5894, 24.8801),
        '三明': (117.6300, 26.2667),
        '莆田': (119.0084, 25.4352),
        '南平': (118.1813, 26.6592),
        '龍巖': (117.0000, 25.1000),
        '寧德': (119.5270, 26.6595),
    },
    '河南省': {
        '鄭州': (113.6254, 34.7466),
        '開封': (114.3055, 34.7794),
        '洛陽': (112.4543, 34.6171),
        '平頂山': (113.3009, 33.7453),
        '焦作': (113.2398, 35.2397),
        '鶴壁': (114.2950, 35.7561),
        '新鄉': (113.8343, 35.3082),
        '安陽': (114.3055, 36.1031),
        '濮陽': (115.0264, 35.7469),
        '許昌': (113.8343, 34.0267),
        '漯河': (114.0267, 33.5631),
        '三門峽': (111.1989, 34.7769),
        '南陽': (112.5389, 32.9988),
        '商丘': (115.6394, 34.4353),
        '信陽': (114.0867, 32.1236),
        '周口': (114.6508, 33.6155),
        '駐馬店': (114.0267, 32.9756),
    },
    '湖北省': {
        '武漢': (114.3055, 30.5928),
        '黃石': (115.0264, 30.2131),
        '十堰': (110.7975, 32.6475),
        '宜昌': (111.2865, 30.5928),
        '襄陽': (112.1388, 32.0231),
        '鄂州': (114.8904, 30.3931),
        '孝感': (113.9261, 30.8755),
        '荊門': (112.2030, 31.8346),
        '黃岡': (115.3500, 30.4500),
        '咸寧': (114.2881, 29.8683),
        '荊州': (112.2388, 30.3281),
        '恩施': (109.4864, 30.2840),
        '仙桃': (113.4500, 30.3500),
        '潛江': (112.8931, 30.2896),
        '神農架': (110.6733, 31.7545),
    },
    '湖南省': {
        '長沙': (112.9388, 28.2282),
        '株洲': (113.1309, 27.8358),
        '湘潭': (112.9388, 27.8358),
        '衡陽': (112.6089, 26.8898),
        '邵陽': (111.4656, 27.2371),
        '岳陽': (113.0927, 29.3644),
        '常德': (111.6909, 29.0502),
        '益陽': (112.3677, 28.5890),
        '婁底': (111.9956, 27.7236),
        '懷化': (109.9760, 27.5531),
        '永州': (111.6009, 26.4343),
        '張家界': (110.4793, 29.1186),
        '吉首': (109.7410, 28.3123),
    },
    '廣東省': {
        '廣州': (113.2644, 23.1291),
        '深圳': (114.0579, 22.5431),
        '珠海': (113.5644, 22.2747),
        '汕頭': (116.6684, 23.3645),
        '佛山': (113.1213, 23.0291),
        '江門': (113.0644, 22.5747),
        '湛江': (110.3893, 21.2747),
        '茂名': (110.9293, 21.6647),
        '肇慶': (112.4727, 23.0527),
        '惠州': (114.4045, 23.0988),
        '梅州': (116.1293, 24.2847),
        '汕尾': (115.3745, 22.7747),
        '河源': (114.6881, 23.7645),
        '陽江': (111.9793, 21.8547),
        '清遠': (113.0393, 23.6847),
        '東莞': (113.7565, 23.0489),
        '中山': (113.3844, 22.5211),
        '潮州': (116.6293, 23.6647),
        '揭陽': (115.8545, 23.5447),
        '云浮': (112.0393, 22.2947),
    },
    '四川省': {
        '成都': (104.0660, 30.5728),
        '自貢': (104.7761, 29.3328),
        '攀枝花': (101.7181, 26.5800),
        '瀘州': (105.3919, 28.8717),
        '德陽': (104.3782, 31.1297),
        '綿陽': (104.7395, 32.7295),
        '廣元': (105.8289, 32.4328),
        '遂寧': (105.5883, 30.5328),
        '內江': (105.0662, 29.5828),
        '樂山': (103.7661, 29.5600),
        '南充': (106.0889, 30.8328),
        '眉山': (103.8623, 30.2797),
        '宜賓': (104.6308, 28.7517),
        '廣安': (106.6343, 30.4567),
        '達州': (107.4686, 31.2097),
        '雅安': (103.0006, 29.9828),
        '巴中': (106.7517, 31.8497),
        '資陽': (104.6308, 30.1797),
        '阿壩': (103.9200, 32.8667),
        '甘孜': (101.9700, 30.0800),
        '涼山': (102.2680, 27.8967),
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

def find_nearest_city(lng, lat, province):
    """根據坐標找最近的城市"""
    if province not in CITY_CENTERS:
        return None

    cities = CITY_CENTERS[province]
    min_dist = float('inf')
    nearest_city = None

    for city_name, (c_lng, c_lat) in cities.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_dist:
            min_dist = dist
            nearest_city = city_name

    # 距離小於 3 度認為可靠
    if min_dist < 3:
        return nearest_city

    return None

def organize_province(province_name):
    """整理一個省份的檔案"""
    province_path = os.path.join(WIKI_CHINA, province_name)

    if not os.path.exists(province_path):
        return 0, 0

    # 列出根目錄的 .md 檔案
    root_files = [f for f in os.listdir(province_path)
                  if f.endswith('.md') and os.path.isfile(os.path.join(province_path, f))]

    if not root_files:
        return 0, 0

    print(f"\n🔧 {province_name} ({len(root_files)} 個檔案)", flush=True)

    moved_count = 0
    failed_list = []

    for filename in root_files:
        file_path = os.path.join(province_path, filename)
        title = filename[:-3]

        # 提取坐標
        lng, lat = extract_coordinates(file_path)

        if lng is None or lat is None:
            failed_list.append((filename, "無坐標"))
            continue

        # 找最近的城市
        city = find_nearest_city(lng, lat, province_name)

        if not city:
            failed_list.append((filename, f"距離遠"))
            continue

        # 移動檔案
        try:
            city_dir = os.path.join(province_path, city)
            os.makedirs(city_dir, exist_ok=True)
            target_file = os.path.join(city_dir, filename)

            shutil.move(file_path, target_file)
            moved_count += 1
            print(f"  ✓ {title[:30]:<30} → {city}", flush=True)

        except Exception as e:
            failed_list.append((filename, f"移動失敗"))

    if failed_list:
        print(f"  ⚠️  無法判斷: {len(failed_list)} 個", flush=True)
        for filename, reason in failed_list[:3]:
            print(f"    - {filename[:40]} ({reason})", flush=True)
        if len(failed_list) > 3:
            print(f"    ... 及其他 {len(failed_list)-3} 個", flush=True)

    return moved_count, len(failed_list)

# 主程序
print("=" * 70, flush=True)
print("🔧 整理中國省份的城市分類", flush=True)
print("=" * 70, flush=True)

# 掃描所有省份
provinces = [d for d in os.listdir(WIKI_CHINA)
             if os.path.isdir(os.path.join(WIKI_CHINA, d)) and d not in ['香港', '澳門']]

total_moved = 0
total_failed = 0

for province in sorted(provinces):
    moved, failed = organize_province(province)
    total_moved += moved
    total_failed += failed

print(f"\n{'='*70}", flush=True)
print(f"✅ 完成！", flush=True)
print(f"  總共移動: {total_moved} 個", flush=True)
print(f"  待人工檢查: {total_failed} 個", flush=True)
print(f"{'='*70}", flush=True)
