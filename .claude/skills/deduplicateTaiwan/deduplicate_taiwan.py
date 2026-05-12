#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣 Wiki 去重工具

處理兩種重複：
1. 目錄名稱異體字重複（臺/台 等）
2. 座標錯誤歸檔（同一地點放在錯誤的縣市/鄉鎮市區）

使用方式：
  python deduplicate_taiwan.py mode=report   # 分析報告（預設）
  python deduplicate_taiwan.py mode=dry_run  # 顯示將做什麼
  python deduplicate_taiwan.py mode=fix      # 實際執行修正
"""

import os
import sys
import io
import json
import re
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 動態路徑設定
_SCRIPT_DIR = Path(__file__).parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
WIKI_PATH = str(_PROJECT_ROOT / "wiki" / "台灣")
TWGEOJSON_PATH = str(_PROJECT_ROOT / "twgeojson" / "twtown2010.json")
COUNTY_MAPPING_PATH = str(_PROJECT_ROOT / ".claude" / "skills" / "reorganizeTaiwanDistricts" / "county_mapping.json")

# ============================================================================
# 從 reorganizeTaiwanDistricts 複製的核心函數
# ============================================================================

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """射線投射演算法判斷點是否在多邊形內，加入邊界容差處理"""
    x, y = point
    n = len(polygon)
    inside = False
    tolerance = 1e-3  # 容差值，約 100m 級別

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

def load_geojson_towns() -> Dict[str, Dict]:
    """載入鄉鎮市區 GeoJSON（自動合併重複區域）"""
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
                towns[key]['geometry']['coordinates'].extend(geometry.get('coordinates', []))

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

def find_correct_district(coords: Tuple[float, float], towns: Dict[str, Dict]) -> Optional[str]:
    """根據座標找正確的鄉鎮市區，返回 'county/town' 格式"""
    point = coords
    for key, town_data in towns.items():
        geometry = town_data['geometry']
        for polygon_ring in geometry.get('coordinates', []):
            if not polygon_ring:
                continue
            try:
                ring = [(float(c[0]), float(c[1])) for c in polygon_ring[0]]
            except (IndexError, TypeError):
                continue
            if len(ring) > 2 and point_in_polygon(point, ring):
                return key
    return None

def load_county_mapping() -> Dict[str, str]:
    """載入縣市名稱映射（舊名 → 新名）"""
    try:
        with open(COUNTY_MAPPING_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('mapping', {})
    except:
        return {}

# ============================================================================
# 去重邏輯
# ============================================================================

def scan_duplicates() -> Dict[str, List[Path]]:
    """掃描台灣目錄中的重複檔案（包括 _1.md _2.md 等自動備份）"""
    duplicates = defaultdict(list)
    auto_backup_to_delete = []  # _1.md _2.md 等自動備份

    for md_file in Path(WIKI_PATH).rglob('*.md'):
        stem = md_file.stem

        # 檢查是否為自動備份檔案（如 filename_1.md, filename_2.md）
        if stem[-2] == '_' and stem[-1].isdigit():
            auto_backup_to_delete.append(md_file)
            continue

        duplicates[stem].append(md_file)

    return {
        'duplicates': {k: v for k, v in duplicates.items() if len(v) > 1},
        'auto_backups': auto_backup_to_delete
    }

def normalize_path_for_typo_check(path_str: str) -> str:
    """標準化路徑用於異體字檢查（臺 → 台）"""
    return path_str.replace('臺', '台')

def is_typo_duplicate(paths: List[Path]) -> bool:
    """判斷是否為目錄異體字重複（只差在臺/台）"""
    if len(paths) < 2:
        return False
    normalized = [normalize_path_for_typo_check(str(p)) for p in paths]
    return len(set(normalized)) == 1

def get_correct_county_name(county_from_geojson: str, mapping: Dict[str, str]) -> str:
    """從 GeoJSON 的舊縣市名映射到 wiki 中的正確名稱"""
    return mapping.get(county_from_geojson, county_from_geojson)

def classify_duplicates(duplicates: Dict[str, List[Path]]) -> Dict[str, Dict]:
    """分類重複檔案為不同類型"""
    county_mapping = load_county_mapping()
    towns = load_geojson_towns()

    classified = {
        'typo_duplicates': {},  # 異體字重複
        'coords_error_duplicates': {},  # 座標錯誤歸檔
        'legal_duplicates': {},  # 合法分布（不需處理）
        'need_manual_check': {}  # 無法自動判定
    }

    for title, paths in duplicates.items():
        # 檢查是否為異體字重複（必須只差在臺/台）
        if is_typo_duplicate(paths):
            classified['typo_duplicates'][title] = paths
            continue

        # 只有一個版本 → 跳過
        if len(paths) < 2:
            continue

        # 檢查是否為座標錯誤歸檔
        coords_dict = {}  # {Path: coords}
        all_have_coords = True

        for path in paths:
            coords = extract_coordinates(path)
            if coords:
                coords_dict[path] = coords
            else:
                all_have_coords = False

        if all_have_coords and len(coords_dict) > 1:
            # 所有版本都有座標，查詢正確位置
            location_dict = {}  # {Path: (county, town)}
            all_located = True

            for path, coords in coords_dict.items():
                location = find_correct_district(coords, towns)
                if location:
                    location_dict[path] = location
                else:
                    all_located = False
                    break

            if all_located:
                # 檢查是否各版本座標差異大（合法連鎖店分布）或都指向同一位置（錯誤歸檔）
                unique_locations = set(location_dict.values())
                unique_coords = set(coords_dict.values())

                if len(unique_coords) == len(coords_dict):
                    # 每個版本座標都不同 → 合法分布（連鎖店在多個地點）
                    classified['legal_duplicates'][title] = paths
                elif len(unique_locations) == 1:
                    # 所有版本都指向同一位置 → 檢查是否真的在正確位置
                    # 如果檔案路徑與 GeoJSON 位置匹配 → 合法（可能是重複掃描）
                    # 如果檔案路徑與 GeoJSON 位置不匹配 → 座標錯誤歸檔
                    has_correct_location = False
                    for path, location in location_dict.items():
                        # 簡單檢查：GeoJSON 位置是否包含檔案所在的鄉鎮市區名
                        path_str = str(path)
                        if location.split('/')[-1] in path_str or location.split('/')[0] in path_str:
                            has_correct_location = True
                            break

                    if has_correct_location:
                        classified['legal_duplicates'][title] = paths
                    else:
                        classified['coords_error_duplicates'][title] = {
                            'paths': paths,
                            'locations': location_dict
                        }
                else:
                    # 各版本指向不同位置 → 合法連鎖分布（各版本在不同地區）
                    classified['legal_duplicates'][title] = paths
            else:
                classified['need_manual_check'][title] = {'paths': paths, 'reason': 'Cannot locate some copies via GeoJSON'}
        else:
            if all_have_coords:
                classified['legal_duplicates'][title] = paths
            else:
                classified['need_manual_check'][title] = {'paths': paths, 'reason': 'Missing coordinates'}

    return classified

def generate_report(classified: Dict[str, Dict]) -> Dict:
    """生成詳細報告（轉換 Path 物件為字串）"""
    # 轉換 Path 物件為字串
    details = {}

    for key, value in classified.items():
        if key == 'typo_duplicates':
            details[key] = {title: [str(p) for p in paths] for title, paths in value.items()}
        elif key == 'coords_error_duplicates':
            details[key] = {
                title: {
                    'paths': [str(p) for p in data['paths']],
                    'locations': {str(p): location for p, location in data['locations'].items()}
                }
                for title, data in value.items()
            }
        elif key == 'legal_duplicates':
            details[key] = {title: [str(p) for p in paths] for title, paths in value.items()}
        elif key == 'need_manual_check':
            details[key] = {
                title: {
                    'paths': [str(p) for p in data.get('paths', [])],
                    'reason': data.get('reason', '')
                }
                for title, data in value.items()
            }

    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'typo_duplicates': len(classified['typo_duplicates']),
            'coords_error_duplicates': len(classified['coords_error_duplicates']),
            'legal_duplicates': len(classified['legal_duplicates']),
            'need_manual_check': len(classified['need_manual_check']),
            'total_duplicate_groups': sum(len(v) for v in classified.values())
        },
        'details': details
    }
    return report

def find_taiwan_files_in_china() -> List[Path]:
    """找出落在中國目錄中的台灣檔案"""
    project_root = Path(__file__).parent.parent.parent
    china_wiki_path = project_root / "wiki" / "中國"
    taiwan_files = []

    if china_wiki_path.exists():
        for md_file in china_wiki_path.rglob('*.md'):
            # 簡單檢查：檔案內容是否標記為台灣
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '台灣' in content and ('座標:' in content or 'coordinates:' in content):
                        taiwan_files.append(md_file)
            except:
                pass

    return taiwan_files

def plan_fixes(classified: Dict[str, Dict], auto_backups: List[Path] = None) -> Dict:
    """規劃修復操作"""
    county_mapping = load_county_mapping()
    if auto_backups is None:
        auto_backups = []

    fixes = {
        'to_delete': [],  # {path: reason}
        'to_move': [],  # {from: path, to: path, reason}
        'to_review': []  # {paths: [paths], reason}
    }

    # 先刪除所有自動備份檔案
    for backup_path in auto_backups:
        fixes['to_delete'].append({
            'path': str(backup_path),
            'reason': f'自動備份檔案（{backup_path.name}）'
        })

    # 刪除落在中國目錄中的台灣檔案
    taiwan_in_china = find_taiwan_files_in_china()
    for taiwan_file in taiwan_in_china:
        fixes['to_delete'].append({
            'path': str(taiwan_file),
            'reason': '台灣檔案誤放在中國目錄'
        })

    # 異體字重複：保留新名稱版本，刪除舊名稱版本
    for title, paths in classified['typo_duplicates'].items():
        # 先試著判斷哪個是舊名稱版本
        old_path = None
        new_path = None

        for path in paths:
            if '臺' in str(path):
                old_path = path
            if '台' in str(path):
                new_path = path

        if old_path and new_path:
            fixes['to_delete'].append({
                'path': str(old_path),
                'reason': f'目錄異體字重複（保留 {new_path.relative_to(WIKI_PATH)}）'
            })
        else:
            # 無法判定，標記為人工檢查
            fixes['to_review'].append({
                'paths': [str(p) for p in paths],
                'reason': '異體字重複但無法自動判定新舊版本'
            })

    # 座標錯誤歸檔：保留正確位置，刪除其他版本
    for title, data in classified['coords_error_duplicates'].items():
        paths_list = data['paths']  # 這是 List[Path]
        locations = data['locations']  # 這是 {path_str: location_str}

        # 把 paths_list 轉成字串集合，方便比對
        paths_str_set = {str(p) for p in paths_list}

        # 找出位置
        location_counts = defaultdict(list)
        for path_str, location in locations.items():
            location_counts[location].append(path_str)

        # 所有版本都指向同一位置時
        if len(location_counts) == 1:
            correct_location = list(location_counts.keys())[0]
            county, town = correct_location.split('/')

            # 保留「路徑中包含該位置」的那份，刪除其他的
            correct_path = None
            for path_str in paths_str_set:
                if town in path_str or county in path_str:
                    correct_path = path_str
                    break

            # 如果找不到匹配的，就保留第一個
            if not correct_path:
                correct_path = list(paths_str_set)[0]

            # 刪除其他版本
            for path_str in paths_str_set:
                if path_str != correct_path:
                    fixes['to_delete'].append({
                        'path': path_str,
                        'reason': f'座標錯誤歸檔（應在 {correct_location}，保留 {Path(correct_path).parent.name}）'
                    })

        # 多個位置時
        elif len(location_counts) > 1:
            # 保留出現次數多的那個位置的版本
            max_location = max(location_counts.items(), key=lambda x: len(x[1]))[0]
            max_paths = set(location_counts[max_location])

            for path_str in paths_str_set:
                if path_str not in max_paths:
                    fixes['to_delete'].append({
                        'path': path_str,
                        'reason': f'座標錯誤歸檔（應在 {max_location}）'
                    })

    return fixes

def execute_fixes(fixes: Dict, dry_run: bool = False):
    """執行修復操作"""
    deleted_count = 0
    moved_count = 0
    failed_count = 0

    print("\n" + "="*80)
    print("執行修復操作".center(80))
    print("="*80)

    # 執行刪除操作
    for item in fixes['to_delete']:
        path = Path(item['path'])
        reason = item['reason']

        if dry_run:
            print(f"[DRY RUN] 刪除: {path.relative_to(WIKI_PATH)}")
            print(f"          原因: {reason}")
            deleted_count += 1
        else:
            try:
                path.unlink()
                print(f"✓ 刪除: {path.relative_to(WIKI_PATH)}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ 刪除失敗: {path.relative_to(WIKI_PATH)} - {e}")
                failed_count += 1

    print(f"\n✓ 刪除: {deleted_count} 個檔案")
    if failed_count > 0:
        print(f"✗ 失敗: {failed_count} 個")

    print("="*80)

# ============================================================================
# 主程式
# ============================================================================

def main():
    mode = 'report'
    for arg in sys.argv[1:]:
        if arg.startswith('mode='):
            mode = arg.split('=')[1]

    print("="*80)
    print("台灣 Wiki 去重工具".center(80))
    print("="*80)
    print()

    if not os.path.isdir(WIKI_PATH):
        print(f"❌ 目錄不存在: {WIKI_PATH}")
        return

    # 掃描重複
    print("📍 掃描重複檔案...")
    scan_result = scan_duplicates()
    duplicates = scan_result['duplicates']
    auto_backups = scan_result['auto_backups']

    print(f"✓ 找到 {len(duplicates)} 個重複檔名")
    if auto_backups:
        print(f"✓ 找到 {len(auto_backups)} 個自動備份檔案（_1.md _2.md 等）")
    print()

    # 分類
    print("🏷️  分類重複...")
    classified = classify_duplicates(duplicates)
    print(f"✓ 異體字重複: {classified['typo_duplicates'].__len__()} 個")
    print(f"✓ 座標錯誤: {classified['coords_error_duplicates'].__len__()} 個")
    print(f"✓ 合法分布: {classified['legal_duplicates'].__len__()} 個")
    print(f"✓ 需人工檢查: {classified['need_manual_check'].__len__()} 個")
    print()

    # 生成報告
    report = generate_report(classified)

    if mode == 'report':
        print("📋 生成報告...")
        with open('deduplicate_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("✓ 報告已保存到 deduplicate_report.json")

        # 人類可讀的摘要
        print("\n" + "="*80)
        print("異體字重複檔案".center(80))
        print("="*80)
        for title, paths in classified['typo_duplicates'].items():
            print(f"\n{title}:")
            for path in paths:
                print(f"  - {path.relative_to(WIKI_PATH)}")

        if classified['coords_error_duplicates']:
            print("\n" + "="*80)
            print("座標錯誤歸檔".center(80))
            print("="*80)
            for title, data in classified['coords_error_duplicates'].items():
                print(f"\n{title}:")
                for path, location in data['locations'].items():
                    print(f"  - {path.relative_to(WIKI_PATH)} → 應在 {location}")

        if classified['need_manual_check']:
            print("\n" + "="*80)
            print("需人工檢查".center(80))
            print("="*80)
            for title, data in classified['need_manual_check'].items():
                print(f"\n{title}: {data.get('reason', 'Unknown')}")
                for path in data['paths']:
                    print(f"  - {path.relative_to(WIKI_PATH)}")

        if auto_backups:
            print("\n" + "="*80)
            print("自動備份檔案".center(80))
            print("="*80)
            print(f"\n找到 {len(auto_backups)} 個自動備份檔案（將在 mode=fix 時刪除）:")
            for path in auto_backups:
                print(f"  - {path.relative_to(WIKI_PATH)}")

    elif mode in ['dry_run', 'fix']:
        fixes = plan_fixes(classified, auto_backups)
        execute_fixes(fixes, dry_run=(mode == 'dry_run'))

        # 報告自動備份
        if auto_backups:
            print("\n" + "="*80)
            print("將刪除的自動備份檔案".center(80))
            print("="*80)
            for path in auto_backups:
                print(f"  - {path.relative_to(WIKI_PATH)}")

    else:
        print(f"❌ 未知的 mode: {mode}")
        print("支援的 mode: report, dry_run, fix")

if __name__ == '__main__':
    main()
