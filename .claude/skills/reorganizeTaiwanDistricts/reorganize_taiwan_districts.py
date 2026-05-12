#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣 POI 重新整理工具
Skill: /reorganizeTaiwanDistricts

【規則定義在 RULES.md - 不准改動】

用法：
  python reorganize_taiwan_districts.py case=1  # 驗證正確位置的檔案
  python reorganize_taiwan_districts.py case=2  # 清空"其他"目錄
  python reorganize_taiwan_districts.py case=3  # 處理缺少鄉鎮市區層級的檔案
"""

import os
import sys
import io
import json
import re
import time
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 修復 Windows 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 路徑設定（動態計算，不依賴絕對路徑）
_SCRIPT_DIR = Path(__file__).parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent  # .claude/skills/reorganizeTaiwanDistricts → project root
WIKI_PATH = str(_PROJECT_ROOT / "wiki" / "台灣")
TWGEOJSON_PATH = str(_PROJECT_ROOT / "twgeojson" / "twtown2010.json")
COUNTY_MAPPING_PATH = str(_SCRIPT_DIR / "county_mapping.json")

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """射線投射演算法判斷點是否在多邊形內

    改進：加入邊界容差處理，解決浮點精度問題
    （某些座標正好在邊界上或非常接近時無法判定的問題）
    """
    x, y = point
    n = len(polygon)
    inside = False
    tolerance = 1e-3  # 容差值，約 100m 級別（適合地理座標的邊界模糊度）

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]

        # 檢查點是否在邊上（點到直線的距離）
        edge_len = ((p2y - p1y)**2 + (p2x - p1x)**2)**0.5
        if edge_len > 0:
            dist = abs((p2y - p1y) * x - (p2x - p1x) * y + p2x * p1y - p2y * p1x) / edge_len
            if dist < tolerance:
                return True

        # 標準射線投射
        if ((p1y > y) != (p2y > y)) and (x < (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x):
            inside = not inside

        p1x, p1y = p2x, p2y

    return inside

def load_county_mapping() -> Dict[str, str]:
    """載入縣市名稱映射（舊 → 新）"""
    try:
        with open(COUNTY_MAPPING_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('mapping', {})
    except:
        print("⚠️  未載入縣市映射，使用原始名稱")
        return {}

def load_geojson_towns() -> Dict[str, Dict]:
    """載入鄉鎮市區 GeoJSON"""
    try:
        with open(TWGEOJSON_PATH, 'r', encoding='utf-8') as f:
            geojson = json.load(f)

        towns = {}
        for feature in geojson.get('features', []):
            props = feature.get('properties', {})
            town_name = props.get('town')
            county_name = props.get('county')
            geometry = feature.get('geometry', {})

            if town_name and county_name and geometry.get('type') == 'MultiPolygon':
                key = f"{county_name}/{town_name}"
                if key not in towns:
                    towns[key] = {
                        'county': county_name,
                        'town': town_name,
                        'geometry': {'type': 'MultiPolygon', 'coordinates': []}
                    }
                # 合併 polygons（處理重複的鄉鎮市區）
                towns[key]['geometry']['coordinates'].extend(geometry.get('coordinates', []))

        print(f"✓ 載入 {len(towns)} 個鄉鎮市區邊界")
        return towns

    except Exception as e:
        print(f"❌ 無法載入 GeoJSON: {e}")
        return {}

def extract_coordinates(file_path: Path) -> Optional[Tuple[float, float]]:
    """從檔案的 frontmatter 提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def find_correct_district(coords: Tuple[float, float], towns: Dict[str, Dict], debug: bool = False) -> Optional[str]:
    """根據座標找正確的鄉鎮市區，返回 'county/town' 格式"""
    point = coords
    for key, town_data in towns.items():
        geometry = town_data['geometry']
        for polygon_ring in geometry.get('coordinates', []):
            if not polygon_ring:
                continue
            # 取外環
            try:
                ring = [(float(c[0]), float(c[1])) for c in polygon_ring[0]]
            except (IndexError, TypeError):
                continue
            if len(ring) > 2 and point_in_polygon(point, ring):
                return key
    return None

def scan_taiwan_poi(case: int = 2) -> List[Dict]:
    """
    掃描台灣 POI
    case=1: 驗證已在正確位置的檔案 wiki/台灣/{縣市}/{鄉鎮市區}/*.md
    case=2: 掃描"其他"目錄中的檔案 wiki/台灣/{縣市}/其他/*.md
    case=3: 掃描直接在縣市目錄下的檔案 wiki/台灣/{縣市}/*.md
    """
    pois = []
    wiki_path = Path(WIKI_PATH)

    if case == 2:
        # 只掃描"其他"目錄中的檔案
        for county_dir in wiki_path.iterdir():
            if not county_dir.is_dir() or county_dir.name.startswith('.'):
                continue

            other_dir = county_dir / '其他'
            if other_dir.exists() and other_dir.is_dir():
                for md_file in other_dir.glob('*.md'):
                    coords = extract_coordinates(md_file)
                    if coords:
                        pois.append({
                            'file': md_file,
                            'county': county_dir.name,
                            'district': '其他',
                            'name': md_file.stem,
                            'coords': coords
                        })

    elif case == 1:
        # 掃描已在正確位置的檔案（三層結構）
        for county_dir in wiki_path.iterdir():
            if not county_dir.is_dir() or county_dir.name.startswith('.'):
                continue

            for district_dir in county_dir.iterdir():
                if not district_dir.is_dir() or district_dir.name.startswith('.') or district_dir.name == '其他':
                    continue

                for md_file in district_dir.glob('*.md'):
                    coords = extract_coordinates(md_file)
                    if coords:
                        pois.append({
                            'file': md_file,
                            'county': county_dir.name,
                            'district': district_dir.name,
                            'name': md_file.stem,
                            'coords': coords
                        })

    elif case == 3:
        # 掃描直接在縣市目錄下的檔案（缺少二級區域層級）
        for county_dir in wiki_path.iterdir():
            if not county_dir.is_dir() or county_dir.name.startswith('.'):
                continue

            for md_file in county_dir.glob('*.md'):
                coords = extract_coordinates(md_file)
                if coords:
                    pois.append({
                        'file': md_file,
                        'county': county_dir.name,
                        'district': None,  # 尚未分類
                        'name': md_file.stem,
                        'coords': coords
                    })

    return pois

def move_file(src: Path, dest_county: str, dest_district: str) -> bool:
    """
    移動檔案到正確的三層位置
    規則：如果目標檔案已存在，刪除源檔案（只保留一份，不增加序號）
    """
    try:
        dest_dir = Path(WIKI_PATH) / dest_county / dest_district

        # 驗證源檔案存在
        if not src.exists():
            return False

        # 建立目標目錄
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"  ❌ mkdir 失敗: {dest_dir} - {e}")
            return False

        dest_file = dest_dir / src.name

        # 如果目標檔案已存在，刪除源檔案（只保留一份）
        if dest_file.exists():
            try:
                os.remove(str(src))
                return True
            except Exception as e:
                print(f"  ❌ 刪除失敗: {src} - {e}")
                return False

        # 否則正常移動
        try:
            shutil.move(str(src), str(dest_file))
            return True
        except Exception as e:
            print(f"  ❌ 移動失敗: {src} → {dest_file} - {e}")
            return False
    except Exception as e:
        print(f"  ❌ move_file 異常: {e}")
        return False

def main():
    # 解析命令行參數
    case = 2  # 預設 case 2
    for arg in sys.argv[1:]:
        if arg.startswith('case='):
            try:
                case = int(arg.split('=')[1])
            except:
                case = 2

    print("🌍 台灣 POI 歸類驗證和整理")
    print("=" * 60)

    if case == 1:
        print("📋 執行：CASE 1 - 驗證已在正確位置的檔案")
        print("⚠️  目標：驗證 wiki/台灣/{縣市}/{鄉鎮市區}/*.md 中的座標")
    elif case == 2:
        print("📋 執行：CASE 2 - 處理 wiki/台灣/{縣市}/其他/*.md")
        print("⚠️  目標：清空所有 '其他' 目錄，移動檔案到正確的鄉鎮市區")
    elif case == 3:
        print("📋 執行：CASE 3 - 處理缺少二級區域層級的檔案")
        print("⚠️  目標：移動直接在縣市下的檔案到正確的鄉鎮市區")
    else:
        print(f"❌ 不支持的 case: {case}")
        return

    print("=" * 60)

    # 載入縣市映射
    print("📖 載入縣市名稱映射...")
    county_mapping = load_county_mapping()
    if county_mapping:
        print(f"✓ 載入 {len(county_mapping)} 個縣市映射")
    else:
        print("⚠️  未載入縣市映射")

    # 載入邊界資料
    print("📖 載入鄉鎮市區邊界...")
    towns = load_geojson_towns()
    if not towns:
        print("❌ 無法載入邊界資料")
        return

    # 掃描 POI
    print(f"📍 掃描 CASE {case} POI...")
    pois = scan_taiwan_poi(case=case)

    if case == 1:
        print(f"✓ 找到 {len(pois)} 個 POI 在正確位置\n")
    elif case == 2:
        print(f"✓ 找到 {len(pois)} 個 POI 在'其他'目錄\n")
    elif case == 3:
        print(f"✓ 找到 {len(pois)} 個 POI 直接在縣市目錄下\n")

    if case == 1:
        # CASE 1: 驗證已在正確位置的檔案
        print("🔍 驗證檔案座標是否在指定的鄉鎮市區內...\n")

        correct = 0
        incorrect = 0
        cannot_locate = 0

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
                      f"正確{correct:4d} 錯誤{incorrect:4d} 無位{cannot_locate:4d} | 預計剩餘: {remaining:.0f}s")
                sys.stdout.flush()
                last_report = current_time

            # 找座標應該在的鄉鎮市區
            correct_key = find_correct_district(poi['coords'], towns)

            if not correct_key:
                # 座標無法映射到任何鄉鎮市區邊界
                cannot_locate += 1
                continue

            correct_county, correct_district = correct_key.split('/')

            # 應用縣市名稱映射（GeoJSON 舊名 → wiki 新名）
            if county_mapping and correct_county in county_mapping:
                correct_county = county_mapping[correct_county]

            # 檢查是否在正確位置
            if poi['county'] == correct_county and poi['district'] == correct_district:
                correct += 1
            else:
                incorrect += 1
                print(f"  ⚠️  {poi['name']}: 現在 {poi['county']}/{poi['district']} → 應該 {correct_county}/{correct_district}")

        # 最終報告
        elapsed_total = time.time() - start_time
        print(f"\n{'=' * 60}")
        print(f"✓ CASE 1 執行完成")
        print(f"✓ 掃描正確位置: {len(pois)} 個檔案")
        print(f"✓ 位置正確: {correct}")
        print(f"✓ 位置錯誤: {incorrect}")
        print(f"✓ 無法定位: {cannot_locate}")
        print(f"✓ 執行時間: {elapsed_total:.1f}s")
        print(f"{'=' * 60}")

    elif case == 2:
        # CASE 2: 移動"其他"目錄中的檔案到正確位置
        print("🔍 驗證歸類並移動到正確鄉鎮市區...\n")

        moved = 0
        unmoved = 0
        cannot_locate = 0
        error_log = []  # 記錄前 3 個錯誤

        start_time = time.time()
        last_report = start_time

        for i, poi in enumerate(pois, 1):
            # 每 10 秒報告進度
            current_time = time.time()
            if current_time - last_report >= 10:
                elapsed = current_time - start_time
                rate = i / elapsed if elapsed > 0 else 0
                remaining = (len(pois) - i) / rate if rate > 0 else 0
                msg = f"⏱️ [{elapsed:6.1f}s] 進度: {i:5d}/{len(pois)} ({i/len(pois)*100:5.1f}%) | " + \
                      f"已移{moved:4d} 失敗{unmoved:4d} 無位{cannot_locate:4d} | 預計剩餘: {remaining:.0f}s"
                if error_log:
                    msg += f"\n  錯誤: {error_log[0]}"
                print(msg)
                sys.stdout.flush()
                last_report = current_time

            # 找正確的鄉鎮市區
            correct_key = find_correct_district(poi['coords'], towns)

            if not correct_key:
                # 座標無法映射到任何鄉鎮市區邊界
                cannot_locate += 1
                error_log.append(f"無法定位 {poi['file'].name} @ {poi['coords']}")
                if len(error_log) > 3:
                    error_log.pop(0)
                continue

            correct_county, correct_district = correct_key.split('/')

            # 應用縣市名稱映射（GeoJSON 舊名 → wiki 新名）
            if county_mapping and correct_county in county_mapping:
                correct_county = county_mapping[correct_county]

            # 移動檔案到正確位置
            ok = move_file(poi['file'], correct_county, correct_district)
            if ok:
                moved += 1
            else:
                unmoved += 1
                if len(error_log) < 1:
                    # 診斷：列印完整路徑和存在狀態
                    exists = poi['file'].exists() if hasattr(poi['file'], 'exists') else 'N/A'
                    error_log.append(f"{poi['name']} → {correct_county}/{correct_district} | src存在:{exists} | src={poi['file']}")

        # 最終報告
        elapsed_total = time.time() - start_time
        print(f"\n{'=' * 60}")
        print(f"✓ CASE 2 執行完成")
        print(f"✓ 掃描'其他'目錄: {len(pois)} 個檔案")
        print(f"✓ 已移動: {moved}")
        print(f"✓ 移動失敗: {unmoved}")
        print(f"✓ 無法定位: {cannot_locate}")
        print(f"✓ 執行時間: {elapsed_total:.1f}s")
        print(f"{'=' * 60}")

        # 清理：刪除所有空的"其他"資料夾
        print("\n🧹 清理空的'其他'資料夾...")
        deleted_count = 0
        wiki_path = Path(WIKI_PATH)
        for county_dir in wiki_path.iterdir():
            if not county_dir.is_dir() or county_dir.name.startswith('.'):
                continue
            other_dir = county_dir / '其他'
            if other_dir.exists() and other_dir.is_dir():
                # 檢查是否為空
                files = list(other_dir.glob('*'))
                if len(files) == 0:
                    try:
                        other_dir.rmdir()
                        deleted_count += 1
                    except:
                        pass
                else:
                    print(f"⚠️  {county_dir.name}/其他 還有 {len(files)} 個檔案")

        print(f"✓ 已刪除 {deleted_count} 個空'其他'資料夾")
        print(f"\n✅ CASE 2 完成！不再有'其他'資料夾！")

    elif case == 3:
        # CASE 3: 移動直接在縣市目錄下的檔案到正確的二級區域
        print("🔍 驗證歸類並移動到正確鄉鎮市區...\n")

        moved = 0
        unmoved = 0
        cannot_locate = 0
        error_log = []

        start_time = time.time()
        last_report = start_time

        for i, poi in enumerate(pois, 1):
            # 每 10 秒報告進度
            current_time = time.time()
            if current_time - last_report >= 10:
                elapsed = current_time - start_time
                rate = i / elapsed if elapsed > 0 else 0
                remaining = (len(pois) - i) / rate if rate > 0 else 0
                msg = f"⏱️ [{elapsed:6.1f}s] 進度: {i:5d}/{len(pois)} ({i/len(pois)*100:5.1f}%) | " + \
                      f"已移{moved:4d} 失敗{unmoved:4d} 無位{cannot_locate:4d} | 預計剩餘: {remaining:.0f}s"
                if error_log:
                    msg += f"\n  錯誤: {error_log[0]}"
                print(msg)
                sys.stdout.flush()
                last_report = current_time

            # 找正確的鄉鎮市區
            correct_key = find_correct_district(poi['coords'], towns)

            if not correct_key:
                # 座標無法映射到任何鄉鎮市區邊界
                cannot_locate += 1
                error_log.append(f"無法定位 {poi['file'].name} @ {poi['coords']}")
                if len(error_log) > 3:
                    error_log.pop(0)
                continue

            correct_county, correct_district = correct_key.split('/')

            # 應用縣市名稱映射（GeoJSON 舊名 → wiki 新名）
            if county_mapping and correct_county in county_mapping:
                correct_county = county_mapping[correct_county]

            # 移動檔案到正確位置
            ok = move_file(poi['file'], correct_county, correct_district)
            if ok:
                moved += 1
            else:
                unmoved += 1
                if len(error_log) < 1:
                    exists = poi['file'].exists() if hasattr(poi['file'], 'exists') else 'N/A'
                    error_log.append(f"{poi['name']} → {correct_county}/{correct_district} | src存在:{exists}")

        # 最終報告
        elapsed_total = time.time() - start_time
        print(f"\n{'=' * 60}")
        print(f"✓ CASE 3 執行完成")
        print(f"✓ 掃描縣市目錄: {len(pois)} 個檔案")
        print(f"✓ 已移動: {moved}")
        print(f"✓ 移動失敗: {unmoved}")
        print(f"✓ 無法定位: {cannot_locate}")
        print(f"✓ 執行時間: {elapsed_total:.1f}s")
        print(f"{'=' * 60}")
        print(f"\n✅ CASE 3 完成！所有檔案都有二級區域！")

if __name__ == "__main__":
    main()
