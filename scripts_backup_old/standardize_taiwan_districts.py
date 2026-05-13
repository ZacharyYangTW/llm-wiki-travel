#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化台灣行政區名稱，確保所有鄉鎮市區都有正確的後綴
"""

import os
import sys
import shutil
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 標準化映射表：舊名稱 → 新名稱（帶上正確的後綴）
DISTRICT_RENAME_MAP = {
    "台中市": {
        "大安": "大安區",
        "中區": "中區",  # 已有區
        "北區": "北區",  # 已有區
        "石岡": "石岡區",
        "西屯區": "西屯區",  # 已有區
        "和平": "和平區",
        "東區": "東區",  # 已有區
        "南屯區": "南屯區",  # 已有區
        "烏日": "烏日區",
        "新社": "新社區",
        "龍井": "龍井區",
        "霧峰": "霧峰區",
        "潭子": "潭子區",
        "后里": "后里區",
        "東勢": "東勢區",
        "太平": "太平區",
        "豐原": "豐原區",
        "外埔": "外埔區",
    },
    "高雄市": {
        "三民": "三民區",
        "左營": "左營區",
        "田寮": "田寮區",
        "甲仙": "甲仙區",
        "那瑪夏": "那瑪夏區",
        "路竹": "路竹區",
        "鼓山": "鼓山區",
        "旗津": "旗津區",
        "彌陀": "彌陀區",
        "寶邊": "寶邊區",
        "鹽埕": "鹽埕區",
        "前鎮": "前鎮區",
        "小港": "小港區",
        "前金": "前金區",
        "苓雅": "苓雅區",
        "新興": "新興區",
        "楠梓": "楠梓區",
        "仁武": "仁武區",
        "大社": "大社區",
        "岡山": "岡山區",
        "阿蓮": "阿蓮區",
        "燕巢": "燕巢區",
        "茄萣": "茄萣區",
        "永安": "永安區",
        "梓官": "梓官區",
        "旗山": "旗山區",
        "美濃": "美濃區",
        "六龜": "六龜區",
        "杉林": "杉林區",
        "內門": "內門區",
        "桃源": "桃源區",
        "茂林": "茂林區",
    },
    "台南市": {
        "中西區": "中西區",  # 已有區
        "五十間": "五十間",  # 保持原樣
        "六甲": "六甲區",
        "北門": "北門區",
        "北區": "北區",  # 已有區
        "永康": "永康區",
        "白河": "白河區",
        "安平": "安平區",
        "西港": "西港區",
        "東山": "東山區",
        "東區": "東區",  # 已有區
        "後壁": "後壁區",
        "麻豆": "麻豆區",
        "歸仁": "歸仁區",
        "南區": "南區",
        "新化": "新化區",
        "善化": "善化區",
        "大內": "大內區",
        "山上": "山上區",
        "玉井": "玉井區",
        "南化": "南化區",
        "左鎮": "左鎮區",
        "官田": "官田區",
        "下營": "下營區",
        "柳營": "柳營區",
        "將軍": "將軍區",
        "關子嶺": "關子嶺區",
        "仁德": "仁德區",
    },
    "新北市": {
        "板橋": "板橋區",
        "新莊": "新莊區",
        "泰山": "泰山區",
        "林口": "林口區",
        "蘆洲": "蘆洲區",
        "五股": "五股區",
        "新店": "新店區",
        "安坡": "安坡區",
        "中和": "中和區",
        "永和": "永和區",
        "汐止": "汐止區",
        "貢寮": "貢寮區",
        "瑞芳": "瑞芳區",
        "平溪": "平溪區",
        "金山": "金山區",
        "萬里": "萬里區",
        "石碇": "石碇區",
        "深坑": "深坑區",
        "坪林": "坪林區",
        "烏來": "烏來區",
    },
}

def rename_district_directories():
    """重命名行政區目錄以標準化名稱"""
    renamed_count = 0

    taiwan_path = os.path.join(WIKI_DIR, "台灣")

    for county, rename_map in DISTRICT_RENAME_MAP.items():
        county_path = os.path.join(taiwan_path, county)
        if not os.path.exists(county_path):
            print(f"  ⚠️  {county} 不存在")
            continue

        for old_name, new_name in rename_map.items():
            if old_name == new_name:
                continue  # 名稱相同，不需要改

            old_path = os.path.join(county_path, old_name)
            new_path = os.path.join(county_path, new_name)

            if os.path.exists(old_path) and not os.path.exists(new_path):
                try:
                    shutil.move(old_path, new_path)
                    renamed_count += 1
                    print(f"  ✓ {county}/{old_name} → {new_name}")
                except Exception as e:
                    print(f"  ❌ 錯誤: {county}/{old_name} - {e}")

    return renamed_count

def main():
    print("=" * 70)
    print("📝 標準化台灣行政區名稱")
    print("=" * 70)
    print()

    print("🇹🇼 台灣 - 確保所有行政區都有正確的後綴")
    renamed = rename_district_directories()
    print()

    print("=" * 70)
    print(f"✅ 完成！{renamed} 個目錄已重命名")
    print("=" * 70)

if __name__ == "__main__":
    main()
