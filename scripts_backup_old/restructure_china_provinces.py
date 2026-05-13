#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新組織中國檔案為二級目錄結構：wiki/中國/{省份}/{市縣}/
"""

import os
import sys
import shutil
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 中國城市 → 省份映射（基於當前66個目錄）
CITY_TO_PROVINCE = {
    # 直轄市
    "北京": "北京市",
    "上海": "上海市",
    "天津": "天津市",
    "重慶": "重慶市",

    # 河北省
    "唐山市": "河北省",
    "承德市": "河北省",
    "秦皇島市": "河北省",

    # 山西省
    "大同": "山西省",
    "大同市": "山西省",
    "晉中市": "山西省",

    # 內蒙古自治區
    "呼和浩特市": "內蒙古自治區",

    # 遼寧省
    "瀋陽": "遼寧省",

    # 黑龍江省
    "哈爾濱": "黑龍江省",

    # 江蘇省
    "南京市": "江蘇省",
    "蘇州": "江蘇省",
    "蘇州市": "江蘇省",

    # 浙江省
    "杭州": "浙江省",
    "杭州市": "浙江省",
    "嘉興市": "浙江省",

    # 安徽省
    "合肥市": "安徽省",
    "蕪湖市": "安徽省",

    # 福建省
    "福州市": "福建省",
    "廈門": "福建省",
    "廈門市": "福建省",

    # 江西省
    "南昌市": "江西省",

    # 山東省
    "泰安": "山東省",
    "泰安市": "山東省",
    "黃山市": "山東省",

    # 河南省
    "鄭州": "河南省",
    "鄭州市": "河南省",
    "洛陽": "河南省",
    "開封": "河南省",
    "安陽市": "河南省",

    # 湖北省
    "武汉市": "湖北省",
    "武漢市": "湖北省",

    # 湖南省
    "長沙": "湖南省",
    "長沙市": "湖南省",
    "岳陽市": "湖南省",

    # 廣東省
    "廣州市": "廣東省",
    "深圳市": "廣東省",
    "珠海市": "廣東省",
    "中山市": "廣東省",
    "韶關市": "廣東省",

    # 廣西壯族自治區
    "南寧市": "廣西壯族自治區",

    # 海南省
    "海口市": "海南省",

    # 四川省
    "成都": "四川省",
    "樂山": "四川省",
    "樂山市": "四川省",
    "酒泉市": "四川省",

    # 貴州省
    "貴陽市": "貴州省",

    # 雲南省
    "昆明市": "雲南省",
    "麗江市": "雲南省",

    # 西藏自治區
    "拉薩": "西藏自治區",
    "拉薩市": "西藏自治區",
    "日喀則": "西藏自治區",
    "日喀則市": "西藏自治區",
    "那曲": "西藏自治區",

    # 陝西省
    "西安": "陝西省",
    "咸陽市": "陝西省",

    # 甘肅省
    "蘭州市": "甘肅省",
    "兰州市": "甘肅省",

    # 青海省
    "西寧": "青海省",
    "青海": "青海省",

    # 寧夏回族自治區
    "銀川市": "寧夏回族自治區",

    # 新疆維吾爾自治區
    "烏魯木齊市": "新疆維吾爾自治區",

    # 香港特別行政區
    "香港": "香港特別行政區",

    # 澳門特別行政區
    "澳門": "澳門特別行政區",

    # 景點或特殊情況
    "九寨溝": "四川省",      # 九寨溝在四川
    "曲阜": "山東省",         # 曲阜在山東
    "黃山市": "安徽省",       # 黃山在安徽
    "張家界": "湖南省",       # 張家界在湖南
    "張家界市": "湖南省",     # 張家界在湖南

    # 未知或需要手動處理
    "未知": None,              # 保留在根目錄或需要進一步分類
}

def restructure_china():
    """重新組織中國檔案為省份/市縣結構"""
    china_path = os.path.join(WIKI_DIR, "中國")
    moved_count = 0
    unmapped_count = 0
    merged_count = 0

    # 取得所有現有城市目錄
    existing_cities = [d for d in os.listdir(china_path)
                      if os.path.isdir(os.path.join(china_path, d))]

    for city in existing_cities:
        city_path = os.path.join(china_path, city)
        province = CITY_TO_PROVINCE.get(city)

        if not province:
            print(f"  ⚠️  無法找到省份: {city}")
            unmapped_count += 1
            continue

        # 建立省份目錄
        province_path = os.path.join(china_path, province)
        os.makedirs(province_path, exist_ok=True)

        # 建立市縣目錄
        target_city_path = os.path.join(province_path, city)

        # 檢查目標位置是否已存在
        if os.path.exists(target_city_path):
            # 合併檔案到已存在的目錄
            try:
                for file in os.listdir(city_path):
                    src = os.path.join(city_path, file)
                    dst = os.path.join(target_city_path, file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                shutil.rmtree(city_path)
                merged_count += 1
                print(f"  ✓ {city} 合併到 {province}/{city}")
            except Exception as e:
                print(f"  ❌ 錯誤: {city} - {e}")
        else:
            # 移動整個目錄
            try:
                os.makedirs(target_city_path, exist_ok=True)
                for file in os.listdir(city_path):
                    src = os.path.join(city_path, file)
                    dst = os.path.join(target_city_path, file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                shutil.rmtree(city_path)
                moved_count += 1
                print(f"  ✓ {city} → {province}/{city}")
            except Exception as e:
                print(f"  ❌ 錯誤: {city} - {e}")

    return moved_count, merged_count, unmapped_count

def main():
    print("=" * 70)
    print("🗂️ 重新組織中國檔案為省份/市縣結構")
    print("=" * 70)
    print()

    moved, merged, unmapped = restructure_china()
    print()

    print("=" * 70)
    print(f"✅ 完成！")
    print(f"  新建立: {moved} 個市縣")
    print(f"  合併: {merged} 個重複目錄")
    if unmapped > 0:
        print(f"  ⚠️  無法分類: {unmapped} 個")
    print("=" * 70)

if __name__ == "__main__":
    main()
