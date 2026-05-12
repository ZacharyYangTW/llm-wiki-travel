#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki 目錄結構標準化腳本
- Phase 1: 國家層標準化（重命名/合併）
- Phase 2: 台灣城市重新歸類（坐標計算）
- Phase 3: 日本城市英文→日語漢字
- Phase 4: 中國城市英文拼音→中文（合併）
- Phase 5: 韓國城市英文→中文
- Phase 6: 其他英文國家城市改中文
"""

import os
import sys
import re
import shutil
import math
import io
from pathlib import Path
from collections import defaultdict

# UTF-8 編碼支援
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# ============================================================================
# 映射表定義
# ============================================================================

# Phase 1: 國家層重命名（無重複）
COUNTRY_RENAMES = {
    "Australia": "澳洲",
    "Austria": "奧地利",
    "Czechia": "捷克",
    "Indonesia": "印尼",
    "Spain": "西班牙",
}

# Phase 1: 國家層合併（有重複）
COUNTRY_MERGES = {
    "Belgium": "比利時",
    "Chile": "智利",
    "CN": "中國",
    "Hungary": "匈牙利",
    "Peru": "秘魯",
}

# Phase 2: 台灣 22 縣市中心坐標
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

# Phase 3: 日本城市映射（英文 → 日語漢字）
JAPAN_CITY_MAP = {
    "Abashiri": "網走市",
    "Aizuwakamatsu": "会津若松市",
    "Akita": "秋田市",
    "Arakawa City": "東京都",  # 東京區級歸入東京
    "Asahikawa": "旭川市",
    "Beppu": "別府市",
    "Chiba": "千葉市",
    "Chikushino": "筑紫野市",
    "Chitose": "千歳市",
    "Chiyoda City": "東京都",
    "Daigo": "大子町",
    "Daisen": "大仙市",
    "Dazaifu": "太宰府市",
    "Fujisawa": "藤沢市",
    "Fukaura": "深浦町",
    "Fukuoka": "福岡市",
    "Fukutsu": "福津市",
    "Funabashi": "船橋市",
    "Gotemba": "御殿場市",
    "Hakodate": "函館市",
    "Hatsukaichi": "廿日市市",
    "Himeji": "姫路市",
    "Hirado": "平戸市",
    "Hiroshima": "広島市",
    "Hitachinaka": "常陸那珂市",
    "Hitoyoshi": "人吉市",
    "Hofu": "防府市",
    "Ibusuki": "指宿市",
    "Ichikawa": "市川市",
    "Imabari": "今治市",
    "Ishigaki": "石垣市",
    "Ishioka": "石岡市",
    "Iwakuni": "岩国市",
    "Izumisano": "泉佐野市",
    "Izumo": "出雲市",
    "JR大阪站": "大阪市",  # 合併到大阪
    "JR新大阪駅": "大阪市",
    "Kagoshima": "鹿児島市",
    "Kamakura": "鎌倉市",
    "Kameoka": "亀岡市",
    "Karatsu": "唐津市",
    "Kasama": "笠間市",
    "Kashima": "鹿嶋市",
    "Kawasaki": "川崎市",
    "Kirishima": "霧島市",
    "Kitakata": "喜多方市",
    "Kitakyushu": "北九州市",
    "Kobe": "神戸市",
    "Kochi": "高知市",
    "Kotohira": "琴平町",
    "Kumamoto": "熊本市",
    "Kurashiki": "倉敷市",
    "Kure": "呉市",
    "Kurume": "久留米市",
    "Kōhoku": "東京都",
    "Matsue": "松江市",
    "Matsuyama": "松山市",
    "Minamiosumi": "南大隅町",
    "Minato City": "東京都",
    "Mito": "水戸市",
    "Miyoshi": "三次市",
    "Motobu": "本部町",
    "Munakata": "宗像市",
    "Nachikatsuura": "那智勝浦町",
    "Nagasaki": "長崎市",
    "Nagoya": "名古屋市",
    "Naha": "那覇市",
    "Nanjo": "南城市",
    "Nankoku": "南国市",
    "Narita": "成田市",
    "Naruto": "鳴門市",
    "Natori": "名取市",
    "Nemuro": "根室市",
    "Nikko": "日光市",
    "Noshiro": "能代市",
    "Oda": "大田市",
    "Okayama": "岡山市",
    "Omitama": "小美玉市",
    "Osaka": "大阪市",
    "Ota City": "東京都",
    "Otaru": "小樽市",
    "Ozora": "大空町",
    "Ozu": "大洲市",
    "Sakaiminato": "境港市",
    "Sakura": "佐倉市",
    "Sapporo": "札幌市",
    "Sasebo": "佐世保市",
    "Saza": "佐々町",
    "Sendai": "仙台市",
    "Shari": "斜里町",
    "Shimabara": "島原市",
    "Shimanto": "四万十町",
    "Shimonoseki": "下関市",
    "Shingu": "新宮市",
    "Shinjuku City": "東京都",
    "Shirakawa": "白河市",
    "Taito City": "東京都",
    "Takachiho": "高千穂町",
    "Takamatsu": "高松市",
    "Takamori": "高森町",
    "Takeo": "武雄市",
    "Taketomi": "竹富町",
    "Tanabe": "田辺市",
    "Tateyama": "立山町",
    "Teshikaga": "弟子屈町",
    "Tomigusuku": "豊見城市",
    "Toshima City": "東京都",
    "Tosu": "鳥栖市",
    "Tottori": "鳥取市",
    "Toyako": "洞爺湖町",
    "Tsushima": "対馬市",
    "Urayasu": "浦安市",
    "Utsunomiya": "宇都宮市",
    "Wakkanai": "稚内市",
    "Yakushima": "屋久島町",
    "Yamagata": "山形市",
    "Yamaguchi": "山口市",
    "Yasugi": "安来市",
    "Yatsushiro": "八代市",
}

# Phase 4: 中國城市映射（英文拼音 → 中文）
CHINA_CITY_MAP = {
    "An Yang Shi": "安陽市",
    "Anyang": "安陽市",
    "Chang Sha Shi": "長沙市",
    "Cheng De Shi": "承德市",
    "Datong": "大同市",
    "Fu Zhou Shi": "福州市",
    "Fuzhou": "福州市",
    "Guang Zhou Shi": "廣州市",
    "Hang Zhou Shi": "杭州市",
    "He Fei Shi": "合肥市",
    "Hohhot": "呼和浩特市",
    "Hu He Hao Te Shi": "呼和浩特市",
    "Huang Shan Shi": "黃山市",
    "Huangshan City": "黃山市",
    "Jia Xing Shi": "嘉興市",
    "Jin Zhong Shi": "晉中市",
    "Jinzhong": "晉中市",
    "Jiu Quan Shi": "酒泉市",
    "Jiuquan": "酒泉市",
    "Kun Ming Shi": "昆明市",
    "La Sa Shi": "拉薩市",
    "Lan Zhou Shi": "蘭州市",
    "Lanzhou": "蘭州市",
    "Le Shan Shi": "樂山市",
    "Leshan": "樂山市",
    "Li Jiang Shi": "麗江市",
    "Lijiang": "麗江市",
    "Nan Jing Shi": "南京市",
    "Qin Huang Dao Shi": "秦皇島市",
    "Qinhuangdao": "秦皇島市",
    "Shaoguan": "韶關市",
    "Shen Zhen Shi": "深圳市",
    "Shigatse": "日喀則市",
    "Su Zhou Shi": "蘇州市",
    "Suzhou": "蘇州市",
    "Tai An Shi": "泰安市",
    "Tangshan": "唐山市",
    "Wu Han Shi": "武漢市",
    "Xia Men Shi": "廈門市",
    "Xiamen": "廈門市",
    "Xian Yang Shi": "咸陽市",
    "Xianning": "咸寧市",
    "Yue Yang Shi": "岳陽市",
    "Zhang Jia Jie Shi": "張家界市",
    "Zhangjiajie": "張家界市",
    "Zheng Zhou Shi": "鄭州市",
    "Zhong Shan Shi": "中山市",
    "Zhu Hai Shi": "珠海市",
}

# Phase 5: 韓國城市映射（英文 → 中文）
KOREA_CITY_MAP = {
    "Andong": "安東市",
    "Changwon-si": "昌原市",
    "Cheju": "濟州市",
    "Chuncheon": "春川市",
    "Gapyeong-gun": "加平郡",
    "Jangseong-gun": "長城郡",
    "Seogwipo": "西歸浦市",
    "Suncheon": "順天市",
}

# Phase 6: 其他國家城市映射（英文 → 中文）
OTHER_CITY_MAP = {
    "澳洲": {
        "Brisbane Airport": "布里斯本",
        "Melbourne Airport": "墨爾本",
        "Sydney": "雪梨",
    },
    "奧地利": {
        "Wien": "維也納",
        "Salzburg": "薩爾斯堡",
        "Hallstatt": "哈爾施塔特",
        "Bad Ischl": "巴德伊舍爾",
        "Hallein": "哈萊因",
        "Gosauzwang": "格紹茨旺",
        "Schwechat": "施瓦夏特",
    },
    "捷克": {
        "Hlavní město Praha": "布拉格",
        "Karlovy Vary": "卡羅維瓦利",
        "Český Krumlov": "庫倫洛夫",
    },
    "印尼": {
        "Batam Kota": "巴淡島",
    },
    "西班牙": {
        "Segovia": "塞哥維亞",
    },
}

# ============================================================================
# 工具函數
# ============================================================================

def euclidean_distance(lat1, lon1, lat2, lon2):
    """計算兩個座標之間的歐氏距離"""
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def find_nearest_taiwan_county(lng, lat):
    """根據座標找到最近的台灣縣市"""
    min_distance = float('inf')
    nearest_county = None

    for county, (c_lng, c_lat) in TAIWAN_COUNTIES.items():
        dist = euclidean_distance(lat, lng, c_lat, c_lng)
        if dist < min_distance:
            min_distance = dist
            nearest_county = county

    return nearest_county

def extract_coordinates(content):
    """從 MD 檔案中提取座標"""
    match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
    if match:
        try:
            lng = float(match.group(1).strip())
            lat = float(match.group(2).strip())
            return lng, lat
        except:
            return None
    return None

def preview_changes():
    """預覽所有要進行的改動"""
    print("=" * 80)
    print("WIKI 目錄標準化 - 變更預覽")
    print("=" * 80)
    print()

    changes = {
        "國家重命名": [],
        "國家合併": [],
        "台灣重新歸類": 0,
        "日本城市重命名": [],
        "中國城市合併": [],
        "韓國城市重命名": [],
        "其他國家城市": [],
    }

    # Phase 1A: 國家重命名
    for old_name, new_name in COUNTRY_RENAMES.items():
        old_path = os.path.join(WIKI_DIR, old_name)
        if os.path.exists(old_path):
            changes["國家重命名"].append(f"  {old_name} → {new_name}")

    # Phase 1B: 國家合併
    for old_name, new_name in COUNTRY_MERGES.items():
        old_path = os.path.join(WIKI_DIR, old_name)
        if os.path.exists(old_path):
            file_count = sum([len(files) for _, _, files in os.walk(old_path)])
            changes["國家合併"].append(f"  {old_name} ✗ → {new_name} ({file_count} 個檔案)")

    # Phase 2: 台灣重新歸類
    taiwan_path = os.path.join(WIKI_DIR, "台灣")
    if os.path.exists(taiwan_path):
        for city_dir in os.listdir(taiwan_path):
            city_path = os.path.join(taiwan_path, city_dir)
            if os.path.isdir(city_path):
                # 檢查是否有非縣市目錄（英文名）
                if city_dir not in TAIWAN_COUNTIES and len(city_dir) > 0 and city_dir[0].isascii():
                    file_count = sum([len(files) for _, _, files in os.walk(city_path)])
                    changes["台灣重新歸類"] += file_count

    # Phase 3: 日本城市
    japan_path = os.path.join(WIKI_DIR, "日本")
    if os.path.exists(japan_path):
        for city_dir in os.listdir(japan_path):
            if city_dir in JAPAN_CITY_MAP:
                changes["日本城市重命名"].append(f"  {city_dir} → {JAPAN_CITY_MAP[city_dir]}")

    # Phase 4: 中國城市
    china_path = os.path.join(WIKI_DIR, "中國")
    if os.path.exists(china_path):
        for city_dir in os.listdir(china_path):
            if city_dir in CHINA_CITY_MAP:
                changes["中國城市合併"].append(f"  {city_dir} → {CHINA_CITY_MAP[city_dir]}")

    # Phase 5: 韓國城市
    korea_path = os.path.join(WIKI_DIR, "韓國")
    if os.path.exists(korea_path):
        for city_dir in os.listdir(korea_path):
            if city_dir in KOREA_CITY_MAP:
                changes["韓國城市重命名"].append(f"  {city_dir} → {KOREA_CITY_MAP[city_dir]}")

    # 輸出預覽
    print("📊 國家層重命名")
    for item in changes["國家重命名"]:
        print(item)
    print()

    print("📊 國家層合併")
    for item in changes["國家合併"]:
        print(item)
    print()

    if changes["台灣重新歸類"] > 0:
        print(f"📊 台灣城市重新歸類: {changes['台灣重新歸類']} 個檔案")
        print()

    if changes["日本城市重命名"]:
        print("📊 日本城市英文→日語")
        for item in changes["日本城市重命名"][:5]:
            print(item)
        if len(changes["日本城市重命名"]) > 5:
            print(f"  ... 及其他 {len(changes['日本城市重命名']) - 5} 個")
        print()

    if changes["中國城市合併"]:
        print("📊 中國城市英文→中文")
        for item in changes["中國城市合併"][:5]:
            print(item)
        if len(changes["中國城市合併"]) > 5:
            print(f"  ... 及其他 {len(changes['中國城市合併']) - 5} 個")
        print()

    if changes["韓國城市重命名"]:
        print("📊 韓國城市英文→中文")
        for item in changes["韓國城市重命名"]:
            print(item)
        print()

    print("=" * 80)
    response = input("確認要執行上述改動嗎？(y/n): ").strip().lower()
    return response == 'y'

def execute():
    """執行所有改動"""
    print("\n🔄 開始執行改動...\n")

    stats = {
        "renamed": 0,
        "merged": 0,
        "files_moved": 0,
        "errors": 0,
    }

    # Phase 1A: 國家重命名
    print("Phase 1A: 國家目錄重命名...")
    for old_name, new_name in COUNTRY_RENAMES.items():
        old_path = os.path.join(WIKI_DIR, old_name)
        new_path = os.path.join(WIKI_DIR, new_name)

        if os.path.exists(old_path):
            try:
                os.rename(old_path, new_path)
                print(f"  ✅ {old_name} → {new_name}")
                stats["renamed"] += 1
            except Exception as e:
                print(f"  ❌ {old_name} 重命名失敗: {e}")
                stats["errors"] += 1

    print()

    # Phase 1B: 國家合併
    print("Phase 1B: 國家目錄合併...")
    for old_name, new_name in COUNTRY_MERGES.items():
        old_path = os.path.join(WIKI_DIR, old_name)
        new_path = os.path.join(WIKI_DIR, new_name)

        if os.path.exists(old_path):
            if not os.path.exists(new_path):
                os.makedirs(new_path, exist_ok=True)

            try:
                # 合併子目錄
                for item in os.listdir(old_path):
                    src = os.path.join(old_path, item)
                    dst = os.path.join(new_path, item)

                    if os.path.exists(dst):
                        # 如果目標存在，進行檔案級別合併
                        if os.path.isdir(src):
                            for file in os.listdir(src):
                                shutil.move(os.path.join(src, file), os.path.join(dst, file))
                        else:
                            os.remove(src)  # 跳過重複檔案
                    else:
                        shutil.move(src, dst)

                # 刪除舊目錄
                os.rmdir(old_path)
                print(f"  ✅ {old_name} 合併到 {new_name}")
                stats["merged"] += 1
            except Exception as e:
                print(f"  ❌ {old_name} 合併失敗: {e}")
                stats["errors"] += 1

    print()

    # Phase 2: 台灣重新歸類
    print("Phase 2: 台灣城市重新歸類（坐標計算）...")
    taiwan_path = os.path.join(WIKI_DIR, "台灣")
    if os.path.exists(taiwan_path):
        reclassified = 0
        for city_dir in list(os.listdir(taiwan_path)):
            city_path = os.path.join(taiwan_path, city_dir)

            # 跳過已有的縣市目錄
            if city_dir in TAIWAN_COUNTIES:
                continue

            # 只處理英文或非標準名稱的目錄
            if not os.path.isdir(city_path):
                continue

            for file in os.listdir(city_path):
                file_path = os.path.join(city_path, file)

                if not file.endswith('.md'):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    coords = extract_coordinates(content)
                    if coords:
                        lng, lat = coords
                        nearest_county = find_nearest_taiwan_county(lng, lat)

                        if nearest_county and nearest_county != city_dir:
                            # 建立目標目錄
                            target_dir = os.path.join(taiwan_path, nearest_county)
                            os.makedirs(target_dir, exist_ok=True)

                            # 移動檔案
                            target_path = os.path.join(target_dir, file)
                            shutil.move(file_path, target_path)
                            reclassified += 1

                except Exception as e:
                    print(f"  ⚠️ {file} 處理失敗: {e}")
                    stats["errors"] += 1

        if reclassified > 0:
            print(f"  ✅ 已重新歸類 {reclassified} 個台灣檔案")
            stats["files_moved"] += reclassified

        # 清理空目錄
        for city_dir in list(os.listdir(taiwan_path)):
            city_path = os.path.join(taiwan_path, city_dir)
            if os.path.isdir(city_path) and len(os.listdir(city_path)) == 0:
                try:
                    os.rmdir(city_path)
                except:
                    pass

    print()

    # Phase 3: 日本城市
    print("Phase 3: 日本城市英文→日語漢字...")
    japan_path = os.path.join(WIKI_DIR, "日本")
    if os.path.exists(japan_path):
        for old_city in list(os.listdir(japan_path)):
            if old_city in JAPAN_CITY_MAP:
                new_city = JAPAN_CITY_MAP[old_city]
                old_path = os.path.join(japan_path, old_city)
                new_path = os.path.join(japan_path, new_city)

                if old_path != new_path:
                    try:
                        if os.path.exists(new_path):
                            # 合併
                            for file in os.listdir(old_path):
                                shutil.move(os.path.join(old_path, file), os.path.join(new_path, file))
                            os.rmdir(old_path)
                        else:
                            os.rename(old_path, new_path)

                        print(f"  ✅ {old_city} → {new_city}")
                        stats["renamed"] += 1
                    except Exception as e:
                        print(f"  ❌ {old_city} 重命名失敗: {e}")
                        stats["errors"] += 1

    print()

    # Phase 4: 中國城市
    print("Phase 4: 中國城市英文拼音→中文...")
    china_path = os.path.join(WIKI_DIR, "中國")
    if os.path.exists(china_path):
        for old_city in list(os.listdir(china_path)):
            if old_city in CHINA_CITY_MAP:
                new_city = CHINA_CITY_MAP[old_city]
                old_path = os.path.join(china_path, old_city)
                new_path = os.path.join(china_path, new_city)

                if old_path != new_path and os.path.isdir(old_path):
                    try:
                        if os.path.exists(new_path):
                            # 合併
                            for file in os.listdir(old_path):
                                src = os.path.join(old_path, file)
                                dst = os.path.join(new_path, file)
                                if not os.path.exists(dst):
                                    shutil.move(src, dst)
                            os.rmdir(old_path)
                        else:
                            os.rename(old_path, new_path)

                        print(f"  ✅ {old_city} → {new_city}")
                        stats["merged"] += 1
                    except Exception as e:
                        print(f"  ❌ {old_city} 合併失敗: {e}")
                        stats["errors"] += 1

    print()

    # Phase 5: 韓國城市
    print("Phase 5: 韓國城市英文→中文...")
    korea_path = os.path.join(WIKI_DIR, "韓國")
    if os.path.exists(korea_path):
        for old_city in list(os.listdir(korea_path)):
            if old_city in KOREA_CITY_MAP:
                new_city = KOREA_CITY_MAP[old_city]
                old_path = os.path.join(korea_path, old_city)
                new_path = os.path.join(korea_path, new_city)

                if old_path != new_path and os.path.isdir(old_path):
                    try:
                        if os.path.exists(new_path):
                            for file in os.listdir(old_path):
                                shutil.move(os.path.join(old_path, file), os.path.join(new_path, file))
                            os.rmdir(old_path)
                        else:
                            os.rename(old_path, new_path)

                        print(f"  ✅ {old_city} → {new_city}")
                        stats["renamed"] += 1
                    except Exception as e:
                        print(f"  ❌ {old_city} 重命名失敗: {e}")
                        stats["errors"] += 1

    print()
    print("=" * 80)
    print("✅ 整理完成！")
    print("=" * 80)
    print(f"重命名目錄: {stats['renamed']}")
    print(f"合併目錄: {stats['merged']}")
    print(f"移動檔案: {stats['files_moved']}")
    print(f"錯誤: {stats['errors']}")

def main():
    # 檢查是否有 --skip-confirm 參數
    skip_confirm = '--skip-confirm' in sys.argv or '--auto' in sys.argv

    if skip_confirm:
        print("直接執行（跳過確認）\n")
        execute()
    elif preview_changes():
        execute()
    else:
        print("取消操作")

if __name__ == "__main__":
    main()
