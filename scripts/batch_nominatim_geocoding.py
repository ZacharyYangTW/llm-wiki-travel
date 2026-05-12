#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量反向地理編碼 unknown_files_all.csv 中的所有坐標
"""

import os
import sys
import csv
import requests
import time
import io
from urllib.parse import urlencode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

def reverse_geocode(lat, lng, timeout=10):
    """使用 Nominatim 進行反向地理編碼"""
    try:
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lng,
            'zoom': 10,
            'addressdetails': 1,
            'language': 'zh'
        }

        headers = {
            'User-Agent': 'llm-wiki-travel-classifier'
        }

        url = f"{NOMINATIM_URL}?{urlencode(params)}"
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})

            # 嘗試找到城市
            city = (
                address.get('city') or
                address.get('town') or
                address.get('village') or
                address.get('county')
            )

            # 獲取國家
            country = address.get('country', '')

            # 標準化國家名稱
            country_map = {
                '台灣': '台灣',
                '臺灣': '台灣',
                '日本': '日本',
                '中國': '中國',
                '泰國': '泰國',
                '越南': '越南',
                '柬埔寨': '柬埔寨',
                '馬來西亞': '馬來西亞',
                '新加坡': '新加坡',
                '美國': '美國',
                '加拿大': '加拿大',
                '香港': '香港',
                '澳門': '澳門',
                '韓國': '韓國',
                '南韓': '南韓',
                '印度': '印度',
                '埃及': '埃及',
                '荷蘭': '荷蘭',
                '法國': '法國',
                '西班牙': '西班牙',
                '匈牙利': '匈牙利',
                '比利時': '比利時',
                '盧森堡': '盧森堡',
                '捷克': '捷克',
                '紐西蘭': '紐西蘭',
            }

            country = country_map.get(country, country)

            if city and country:
                return city, country, True
            else:
                return city or '', country or '', False

        else:
            return '', '', False

    except Exception as e:
        print(f"      ⚠️  異常: {str(e)[:50]}")
        return '', '', False

def main():
    print("=" * 70, flush=True)
    print("🌍 批量反向地理編碼", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    # 讀取 CSV
    rows = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}", flush=True)
        return

    total = len(rows)
    print(f"📊 總共 {total} 個檔案待編碼", flush=True)
    print(flush=True)

    success_count = 0
    failed_count = 0
    updated_rows = []

    for i, row in enumerate(rows, 1):
        title = row['標題'].strip()
        lng = row['經度'].strip()
        lat = row['緯度'].strip()

        # 顯示進度
        if i % 100 == 1 or i == 1:
            elapsed = (i - 1) * 1.5
            eta = (total - i) * 1.5
            print(f"[{i:4d}/{total}] 進度: {i/total*100:5.1f}% | 已耗時: {int(elapsed/60)}m | 預估剩餘: {int(eta/60)}m", flush=True)

        # 如果已有城市和國家，跳過
        if row['城市'].strip() and row['國家'].strip():
            updated_rows.append(row)
            continue

        # 反向地理編碼
        city, country, success = reverse_geocode(lat, lng)

        if success:
            row['城市'] = city
            row['國家'] = country
            success_count += 1
            status = "✓"
        else:
            failed_count += 1
            status = "✗"

        updated_rows.append(row)

        # 顯示詳細進度（每 500 個）
        if i % 500 == 0:
            print(f"   已成功編碼: {success_count}, 失敗: {failed_count}", flush=True)

        # 尊重速率限制
        time.sleep(1.5)

    # 寫回 CSV
    print(flush=True)
    print("💾 寫入更新的 CSV...", flush=True)
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['標題', '經度', '緯度', '城市', '國家'], delimiter='\t')
            writer.writeheader()
            writer.writerows(updated_rows)
        print("✅ CSV 已更新", flush=True)
    except Exception as e:
        print(f"❌ 寫入失敗: {e}", flush=True)
        return

    print(flush=True)
    print("=" * 70, flush=True)
    print(f"✅ 完成！", flush=True)
    print(f"  成功編碼: {success_count} 個", flush=True)
    print(f"  失敗/無結果: {failed_count} 個", flush=True)
    print(f"  耗時: 約 {int(total * 1.5 / 60)} 分鐘", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
