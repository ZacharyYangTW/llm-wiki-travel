#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki 重新整理工具 - 通用範本
【規則定義在 COMMON/RULES_TEMPLATE.md - 不准改動】

用於：台灣、中國、日本等各國
用法：
  python reorganize_{country}.py case=1  # 驗證正確位置的檔案
  python reorganize_{country}.py case=2  # 清空"其他"目錄
  python reorganize_{country}.py case=3  # 處理缺少二級區域層級的檔案
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

# ============================================================================
# 【配置部分 - 針對各國修改】
# ============================================================================

COUNTRY_NAME = "台灣"  # 改為：中國、日本、韓國等
WIKI_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\wiki\台灣"  # 改為各國路徑
GEOJSON_PATH = r"h:\我的雲端硬碟\llm_wiki_travel\twgeojson\twtown2010.json"  # 改為各國 GeoJSON

# ============================================================================
# 【工具函數 - 通用，不修改】
# ============================================================================

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
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def load_geojson_regions() -> Dict[str, Dict]:
    """載入 GeoJSON 區域邊界

    注意：某些 GeoJSON 可能包含重複的區域名（如台灣的某些縣市），
    本函數會自動合併重複區域的所有 polygon，確保座標查詢完整性。
    """
    try:
        with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
            geojson = json.load(f)

        regions = {}
        for feature in geojson.get('features', []):
            props = feature.get('properties', {})
            # 根據國家調整 key 名稱
            region1_name = props.get('level1')  # 一級區域名
            region2_name = props.get('level2')  # 二級區域名
            geometry = feature.get('geometry', {})

            if region1_name and region2_name and geometry.get('type') == 'MultiPolygon':
                key = f"{region1_name}/{region2_name}"

                if key not in regions:
                    # 首次見到該區域，建立新條目
                    regions[key] = {
                        'level1': region1_name,
                        'level2': region2_name,
                        'geometry': {'type': 'MultiPolygon', 'coordinates': []}
                    }

                # 合併 polygons（處理重複的區域）
                regions[key]['geometry']['coordinates'].extend(geometry.get('coordinates', []))

        print(f"✓ 載入 {len(regions)} 個區域邊界")
        return regions

    except Exception as e:
        print(f"❌ 無法載入 GeoJSON: {e}")
        return {}

def extract_coordinates(file_path: Path) -> Optional[Tuple[float, float]]:
    """從檔案的 frontmatter 提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def find_correct_region(coords: Tuple[float, float], regions: Dict[str, Dict]) -> Optional[str]:
    """根據座標找正確的區域，返回 'level1/level2' 格式"""
    point = coords
    for key, region_data in regions.items():
        geometry = region_data['geometry']
        for polygon_ring in geometry.get('coordinates', []):
            if not polygon_ring:
                continue
            ring = [(float(c[0]), float(c[1])) for c in polygon_ring[0]]
            if len(ring) > 2 and point_in_polygon(point, ring):
                return key
    return None

def scan_poi(case: int = 2) -> List[Dict]:
    """掃描 POI（根據 case 類型）"""
    pois = []
    wiki_path = Path(WIKI_PATH)

    if case == 2:
        # 掃描"其他"目錄中的檔案
        for region1_dir in wiki_path.iterdir():
            if not region1_dir.is_dir() or region1_dir.name.startswith('.'):
                continue

            other_dir = region1_dir / '其他'
            if other_dir.exists() and other_dir.is_dir():
                for md_file in other_dir.glob('*.md'):
                    coords = extract_coordinates(md_file)
                    if coords:
                        pois.append({
                            'file': md_file,
                            'level1': region1_dir.name,
                            'level2': '其他',
                            'name': md_file.stem,
                            'coords': coords
                        })

    elif case == 1:
        # 掃描三層結構中的檔案
        for region1_dir in wiki_path.iterdir():
            if not region1_dir.is_dir() or region1_dir.name.startswith('.'):
                continue

            for region2_dir in region1_dir.iterdir():
                if not region2_dir.is_dir() or region2_dir.name.startswith('.') or region2_dir.name == '其他':
                    continue

                for md_file in region2_dir.glob('*.md'):
                    coords = extract_coordinates(md_file)
                    if coords:
                        pois.append({
                            'file': md_file,
                            'level1': region1_dir.name,
                            'level2': region2_dir.name,
                            'name': md_file.stem,
                            'coords': coords
                        })

    elif case == 3:
        # 掃描直接在一級區域下的檔案
        for region1_dir in wiki_path.iterdir():
            if not region1_dir.is_dir() or region1_dir.name.startswith('.'):
                continue

            for md_file in region1_dir.glob('*.md'):
                coords = extract_coordinates(md_file)
                if coords:
                    pois.append({
                        'file': md_file,
                        'level1': region1_dir.name,
                        'level2': None,  # 缺少二級
                        'name': md_file.stem,
                        'coords': coords
                    })

    return pois

def move_file(src: Path, dest_region1: str, dest_region2: str) -> bool:
    """移動檔案到正確位置"""
    try:
        dest_dir = Path(WIKI_PATH) / dest_region1 / dest_region2

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

        # 如果目標檔案已存在，刪除源檔案
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

# ============================================================================
# 【主函數 - 邏輯通用，適應各 case】
# ============================================================================

def main():
    # 解析命令行參數
    case = 2  # 預設 case 2
    for arg in sys.argv[1:]:
        if arg.startswith('case='):
            try:
                case = int(arg.split('=')[1])
            except:
                case = 2

    print(f"🌍 {COUNTRY_NAME} POI 重新整理工具")
    print("=" * 60)

    if case == 1:
        print("📋 執行：CASE 1 - 驗證已在正確位置的檔案")
    elif case == 2:
        print("📋 執行：CASE 2 - 清空'其他'目錄，移動檔案")
    elif case == 3:
        print("📋 執行：CASE 3 - 處理缺少二級區域層級的檔案")
    else:
        print(f"❌ 不支持的 case: {case}")
        return

    print("=" * 60)

    # 載入邊界資料
    print("📖 載入區域邊界...")
    regions = load_geojson_regions()
    if not regions:
        print("❌ 無法載入邊界資料")
        return

    # 掃描 POI
    print(f"📍 掃描 POI (CASE {case})...")
    pois = scan_poi(case=case)
    print(f"✓ 找到 {len(pois)} 個 POI\n")

    if len(pois) == 0:
        print("沒有檔案需要處理")
        return

    # 根據 case 處理
    print("🔍 開始處理...\n")

    start_time = time.time()
    last_report = start_time
    stats = {'moved': 0, 'failed': 0, 'no_location': 0, 'correct': 0, 'incorrect': 0}

    for i, poi in enumerate(pois, 1):
        # 每 10 秒報告進度
        current_time = time.time()
        if current_time - last_report >= 10:
            elapsed = current_time - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (len(pois) - i) / rate if rate > 0 else 0

            if case == 1:
                print(f"⏱️ [{elapsed:6.1f}s] 進度: {i:5d}/{len(pois)} ({i/len(pois)*100:5.1f}%) | " +
                      f"正確{stats['correct']:4d} 錯誤{stats['incorrect']:4d} 無位{stats['no_location']:4d} | 預計剩餘: {remaining:.0f}s")
            else:
                print(f"⏱️ [{elapsed:6.1f}s] 進度: {i:5d}/{len(pois)} ({i/len(pois)*100:5.1f}%) | " +
                      f"已移{stats['moved']:4d} 失敗{stats['failed']:4d} 無位{stats['no_location']:4d} | 預計剩餘: {remaining:.0f}s")
            sys.stdout.flush()
            last_report = current_time

        # 找正確的區域
        correct_key = find_correct_region(poi['coords'], regions)

        if not correct_key:
            stats['no_location'] += 1
            continue

        correct_level1, correct_level2 = correct_key.split('/')

        if case == 1:
            # 驗證位置
            if poi['level1'] == correct_level1 and poi['level2'] == correct_level2:
                stats['correct'] += 1
            else:
                stats['incorrect'] += 1
                print(f"  ⚠️  {poi['name']}: {poi['level1']}/{poi['level2']} → 應該 {correct_level1}/{correct_level2}")
        else:
            # 移動檔案
            if move_file(poi['file'], correct_level1, correct_level2):
                stats['moved'] += 1
            else:
                stats['failed'] += 1

    # 最終報告
    elapsed_total = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"✓ CASE {case} 執行完成")
    print(f"✓ 掃描檔案: {len(pois)} 個")

    if case == 1:
        print(f"✓ 位置正確: {stats['correct']}")
        print(f"✓ 位置錯誤: {stats['incorrect']}")
    else:
        print(f"✓ 已移動: {stats['moved']}")
        print(f"✓ 移動失敗: {stats['failed']}")

    print(f"✓ 無法定位: {stats['no_location']}")
    print(f"✓ 執行時間: {elapsed_total:.1f}s")
    print(f"{'=' * 60}")

    # CASE 2 特定：清理空目錄
    if case == 2:
        print("\n🧹 清理空的'其他'資料夾...")
        deleted_count = 0
        wiki_path = Path(WIKI_PATH)
        for region1_dir in wiki_path.iterdir():
            if not region1_dir.is_dir() or region1_dir.name.startswith('.'):
                continue
            other_dir = region1_dir / '其他'
            if other_dir.exists() and other_dir.is_dir():
                files = list(other_dir.glob('*'))
                if len(files) == 0:
                    try:
                        other_dir.rmdir()
                        deleted_count += 1
                    except:
                        pass
                else:
                    print(f"⚠️  {region1_dir.name}/其他 還有 {len(files)} 個檔案")

        print(f"✓ 已刪除 {deleted_count} 個空'其他'資料夾")
        print(f"\n✅ CASE 2 完成！")

if __name__ == "__main__":
    main()
