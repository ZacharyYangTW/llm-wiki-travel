#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML-Wiki Validator: Verify KML POIs match wiki directory structure

Validates that each POI in KML is in the correct country/city/level-2 region
Special strict validation for China, Japan, Taiwan
"""

import os
import sys
import csv
import re
import io
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# 修復 Windows 編碼問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 嘗試用 lxml（寬鬆解析），否則回到 ElementTree
try:
    from lxml import etree as ET
    USE_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    USE_LXML = False

# 第二級行政區定義
LEVEL2_REGIONS = {
    "中國": [
        "北京", "上海", "天津", "重慶", "河北", "河南", "山東", "山西", "陝西",
        "江蘇", "安徽", "浙江", "江西", "福建", "廣東", "廣西", "四川", "貴州",
        "雲南", "西藏", "青海", "寧夏", "甘肅", "新疆", "內蒙古", "黑龍江",
        "吉林", "遼寧", "湖北", "湖南", "海南"
    ],
    "日本": [
        "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
        "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
        "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
        "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県",
        "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県",
        "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県",
        "大分県", "宮崎県", "鹿児島県", "沖縄県"
    ],
    "台灣": [
        "台北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣", "台中市",
        "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "台南市", "高雄市",
        "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣", "金門縣", "連江縣"
    ]
}

@dataclass
class POI:
    """Point of Interest from KML"""
    name: str
    latitude: float
    longitude: float
    description: str = ""

@dataclass
class ValidationResult:
    """Validation result for one POI"""
    poi_name: str
    kml_coords: str
    wiki_path: str
    status: str  # ✓, ✗, ?
    error_type: str
    suggestion: str

class KMLReader:
    """Read and parse KML file"""

    def __init__(self, kml_path: str):
        self.kml_path = Path(kml_path)
        self.pois: List[POI] = []

    def read(self) -> List[POI]:
        """Parse KML and extract POIs (with lenient parsing)"""
        if not self.kml_path.exists():
            print(f"❌ KML file not found: {self.kml_path}")
            return []

        try:
            if USE_LXML:
                # lxml with recovery mode (lenient parsing)
                parser = ET.XMLParser(recover=True)
                tree = ET.parse(str(self.kml_path), parser)
            else:
                # Standard ElementTree
                tree = ET.parse(self.kml_path)

            root = tree.getroot()

            # KML namespace
            ns = {"kml": "http://www.opengis.net/kml/2.2"}

            # Find all Placemarks (must use namespace)
            placemarks = root.findall(".//kml:Placemark", ns)

            for placemark in placemarks:
                # Get elements with namespace
                name_elem = placemark.find("kml:name", ns)
                desc_elem = placemark.find("kml:description", ns)
                point = placemark.find(".//kml:Point", ns)

                # Check all required elements exist
                if name_elem is None or point is None:
                    continue

                coords_elem = point.find("kml:coordinates", ns)
                if coords_elem is None or not coords_elem.text:
                    continue

                # Extract coordinates
                coords_text = coords_elem.text.strip()
                coords = coords_text.split(",")

                if len(coords) < 2:
                    continue

                try:
                    lng = float(coords[0].strip())
                    lat = float(coords[1].strip())

                    poi = POI(
                        name=name_elem.text if name_elem.text else f"POI_{len(self.pois)}",
                        latitude=lat,
                        longitude=lng,
                        description=desc_elem.text if desc_elem is not None and desc_elem.text else ""
                    )
                    self.pois.append(poi)
                except (ValueError, IndexError):
                    continue

        except Exception as e:
            print(f"❌ Error reading KML: {e}")
            if USE_LXML:
                print("   (using lxml recovery mode)")
            import traceback
            traceback.print_exc()
            return []

        print(f"✓ Loaded {len(self.pois)} POIs from KML")
        if USE_LXML:
            print("   (parsed with lxml recovery mode)")
        return self.pois

class WikiSearcher:
    """Search and verify wiki files"""

    def __init__(self, wiki_path: str):
        self.wiki_path = Path(wiki_path)

    def find_poi_file(self, poi_name: str, country: str, city: str) -> Optional[Path]:
        """Find wiki file for POI in specific country/city"""
        search_path = self.wiki_path / country / city

        if not search_path.exists():
            return None

        # Exact match
        for f in search_path.glob("*.md"):
            if f.stem == poi_name:
                return f

        # Fuzzy match
        for f in search_path.glob("*.md"):
            if poi_name.lower() in f.stem.lower() or f.stem.lower() in poi_name.lower():
                return f

        return None

    def get_wiki_coords(self, wiki_file: Path) -> Optional[Tuple[float, float]]:
        """Extract coordinates from wiki file frontmatter"""
        try:
            with open(wiki_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract coordinates from frontmatter
                match = re.search(r'coordinates:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', content)
                if match:
                    return float(match.group(1)), float(match.group(2))
        except:
            pass

        return None

    def list_countries(self) -> List[str]:
        """List all countries in wiki"""
        countries = []
        for item in self.wiki_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                countries.append(item.name)
        return sorted(countries)

    def list_cities(self, country: str) -> List[str]:
        """List all cities in country"""
        country_path = self.wiki_path / country
        if not country_path.exists():
            return []

        cities = []
        for item in country_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                cities.append(item.name)
        return sorted(cities)

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """Ray casting algorithm for point-in-polygon test"""
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


class GeoJSONBoundaryLoader:
    """載入 WGII GeoJSON 邊界資料"""

    def __init__(self, wgii_data_path: str = None):
        if wgii_data_path is None:
            # 使用預設路徑
            current_dir = Path(__file__).parent.parent.parent.parent  # 回到專案根目錄
            wgii_data_path = current_dir / "wgii" / "data"

        self.wgii_path = Path(wgii_data_path)
        self.polygons: Dict[str, List[List[Tuple[float, float]]]] = {}
        self._load_boundaries()

    def _load_boundaries(self):
        """從 WGII 資料夾載入所有邊界"""
        if not self.wgii_path.exists():
            print(f"⚠️  WGII 資料路徑不存在: {self.wgii_path}")
            return

        # 載入中國邊界
        chn_path = self.wgii_path / "CHN" / "country.gcj02.geo.json"
        if chn_path.exists():
            self.polygons["中國"] = self._extract_polygons_from_geojson(chn_path, "GCJ02")

        # 載入台灣邊界
        twn_path = self.wgii_path / "Asia" / "TWN" / "country.wgs84.geo.json"
        if twn_path.exists():
            self.polygons["台灣"] = self._extract_polygons_from_geojson(twn_path, "WGS84")

        # 載入其他關鍵國家
        asia_path = self.wgii_path / "Asia"
        if asia_path.exists():
            for country_code in ["JPN", "HKG", "MAC"]:  # 日本、香港、澳門
                country_file = asia_path / country_code / "country.wgs84.geo.json"
                if country_file.exists():
                    country_name = self._code_to_name(country_code)
                    self.polygons[country_name] = self._extract_polygons_from_geojson(
                        country_file, "WGS84"
                    )

    def _code_to_name(self, code: str) -> str:
        """ISO 代碼轉國家名"""
        mapping = {
            "JPN": "日本",
            "HKG": "香港",
            "MAC": "澳門",
            "KOR": "韓國",
            "THA": "泰國",
            "VNM": "越南",
        }
        return mapping.get(code, code)

    def _extract_polygons_from_geojson(self, geojson_path: Path, coord_system: str) -> List[List[Tuple[float, float]]]:
        """從 GeoJSON 檔案提取多邊形"""
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson = json.load(f)

            polygons = []

            if geojson.get('type') == 'FeatureCollection':
                for feature in geojson.get('features', []):
                    geometry = feature.get('geometry', {})

                    if geometry.get('type') == 'Polygon':
                        ring = geometry['coordinates'][0]
                        polygons.append([(float(c[0]), float(c[1])) for c in ring])

                    elif geometry.get('type') == 'MultiPolygon':
                        for polygon in geometry['coordinates']:
                            ring = polygon[0]
                            polygons.append([(float(c[0]), float(c[1])) for c in ring])

            return polygons

        except Exception as e:
            print(f"⚠️  無法載入 {geojson_path.name}: {e}")
            return []


class KMLWikiValidator:
    """Main validator - 整合 WGII GeoJSON 邊界"""

    def __init__(self, kml_path: str, wiki_path: str, strict: bool = True, wgii_path: str = None):
        self.reader = KMLReader(kml_path)
        self.searcher = WikiSearcher(wiki_path)
        self.strict = strict
        self.results: List[ValidationResult] = []

        # 從 WGII 載入邊界資料
        geo_loader = GeoJSONBoundaryLoader(wgii_path)
        self.country_polygons = geo_loader.polygons

        # 備用邊界（簡化版，當 GeoJSON 載入失敗時使用）
        self.fallback_polygons = {
            "中國": [
                (73, 18), (135, 18), (135, 54), (73, 54)
            ],
            "日本": [
                (130, 30), (145, 30), (145, 45), (130, 45)
            ],
            "台灣": [
                (120, 22), (122, 22), (122, 25), (120, 25)
            ],
            "香港": [
                (113.8, 22.2), (114.4, 22.2), (114.4, 22.6), (113.8, 22.6)
            ],
            "澳門": [
                (113.5, 22.1), (113.6, 22.1), (113.6, 22.2), (113.5, 22.2)
            ],
        }

        # 如果 GeoJSON 載入失敗，使用備用邊界
        if not self.country_polygons:
            self.country_polygons = self.fallback_polygons
            print("⚠️  使用備用邊界定義（GeoJSON 載入失敗）")

    def detect_country(self, lat: float, lng: float) -> Optional[str]:
        """Detect country using polygon boundaries"""
        point = (lng, lat)  # (經度, 緯度)

        for country, polygons in self.country_polygons.items():
            # polygons 是多邊形列表（從 GeoJSON 載入）或單個多邊形（備用）
            if isinstance(polygons[0], (tuple, list)) and not isinstance(polygons[0][0], (tuple, list)):
                # 單個多邊形（備用邊界格式）
                if point_in_polygon(point, polygons):
                    return country
            else:
                # 多個多邊形（GeoJSON 格式）
                for polygon in polygons:
                    if point_in_polygon(point, polygon):
                        return country

        return None

    def validate_poi(self, poi: POI) -> ValidationResult:
        """Validate single POI"""
        coords_str = f"({poi.latitude:.2f},{poi.longitude:.2f})"

        # Detect country
        detected_country = self.detect_country(poi.latitude, poi.longitude)

        if not detected_country:
            return ValidationResult(
                poi_name=poi.name,
                kml_coords=coords_str,
                wiki_path="",
                status="?",
                error_type="UNKNOWN_COUNTRY",
                suggestion="座標無法匹配已知國家"
            )

        # Find wiki file
        # Try to find in all cities of detected country
        cities = self.searcher.list_cities(detected_country)
        found_file = None
        found_city = None

        for city in cities:
            file_path = self.searcher.find_poi_file(poi.name, detected_country, city)
            if file_path:
                found_file = file_path
                found_city = city
                break

        if not found_file:
            return ValidationResult(
                poi_name=poi.name,
                kml_coords=coords_str,
                wiki_path="",
                status="?",
                error_type="NOT_FOUND",
                suggestion=f"在 {detected_country} 中未找到此 POI"
            )

        # Verify coordinates
        wiki_coords = self.searcher.get_wiki_coords(found_file)
        wiki_path = str(found_file.relative_to(self.searcher.wiki_path))

        if wiki_coords:
            lng_diff = abs(poi.longitude - wiki_coords[0])
            lat_diff = abs(poi.latitude - wiki_coords[1])

            if lng_diff > 0.01 or lat_diff > 0.01:
                return ValidationResult(
                    poi_name=poi.name,
                    kml_coords=coords_str,
                    wiki_path=wiki_path,
                    status="✗",
                    error_type="COORD_MISMATCH",
                    suggestion=f"座標不符。Wiki: ({wiki_coords[0]:.2f},{wiki_coords[1]:.2f})"
                )

        return ValidationResult(
            poi_name=poi.name,
            kml_coords=coords_str,
            wiki_path=wiki_path,
            status="✓",
            error_type="",
            suggestion="OK"
        )

    def validate_all(self) -> List[ValidationResult]:
        """Validate all POIs with progress reporting every 10 seconds"""
        import time

        pois = self.reader.read()
        total = len(pois)

        print(f"\n{'='*60}")
        print(f"驗證 {total} 個 POI (Zachary's World Trip.kml)")
        print(f"已載入邊界: {list(self.country_polygons.keys())}")
        print(f"{'='*60}\n")

        # 測試第一個 POI 用來調試
        if pois:
            test_poi = pois[0]
            test_country = self.detect_country(test_poi.latitude, test_poi.longitude)
            print(f"🔍 測試第一個 POI: {test_poi.name} ({test_poi.latitude:.2f},{test_poi.longitude:.2f})")
            print(f"   檢測到的國家: {test_country}")
            if test_country:
                cities = self.searcher.list_cities(test_country)
                print(f"   {test_country} 中有 {len(cities)} 個城市")
            print()

        start_time = time.time()
        last_report_time = start_time

        for i, poi in enumerate(pois, 1):
            result = self.validate_poi(poi)
            self.results.append(result)

            # 每 10 秒輸出進度
            current_time = time.time()
            if current_time - last_report_time >= 10:
                elapsed = current_time - start_time
                rate = i / elapsed
                remaining = (total - i) / rate if rate > 0 else 0

                ok = sum(1 for r in self.results if r.status == "✓")
                error = sum(1 for r in self.results if r.status == "✗")
                missing = sum(1 for r in self.results if r.status == "?")

                print(f"⏱️ [{elapsed:6.1f}s] 進度: {i:5d}/{total} ({i/total*100:5.1f}%) | " +
                      f"✓{ok:5d} ✗{error:4d} ?{missing:4d} | " +
                      f"預計剩餘: {remaining:.0f}s")
                sys.stdout.flush()

                last_report_time = current_time

        return self.results

    def generate_report(self, output_path: str = "kml_wiki_validation_errors.csv"):
        """Generate CSV report - only errors"""
        errors_only = [r for r in self.results if r.status != "✓"]

        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                "問題類型", "POI_Name", "KML_Coords", "Wiki_Path", "建議"
            ])

            for result in errors_only:
                # 分類標籤
                if result.error_type == "NOT_FOUND":
                    category = "❌ KML 未歸類到 Wiki"
                elif result.error_type == "WRONG_COUNTRY" or result.error_type == "WRONG_CITY":
                    category = "⚠️ 歸類到錯誤位置"
                else:
                    category = "⚠️ 其他問題"

                writer.writerow([
                    category,
                    result.poi_name,
                    result.kml_coords,
                    result.wiki_path,
                    result.suggestion
                ])

        print(f"✓ Error report saved to {output_path}")
        return output_path

    def find_unused_wiki_files(self, output_path: str = "kml_wiki_unused.csv"):
        """找出 Wiki 中有但 KML 沒有的檔案"""
        # 收集所有 KML 中出現的 POI 名稱
        kml_poi_names = {poi.name for poi in self.reader.pois}

        # 掃描 wiki 目錄找出所有檔案
        unused = []

        for country in self.searcher.list_countries():
            for city in self.searcher.list_cities(country):
                city_path = self.searcher.wiki_path / country / city
                for md_file in city_path.glob("*.md"):
                    if md_file.stem not in kml_poi_names:
                        unused.append({
                            "country": country,
                            "city": city,
                            "filename": md_file.name,
                            "path": str(md_file.relative_to(self.searcher.wiki_path))
                        })

        # 寫出報告
        if unused:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "問題類型", "Wiki_Path", "Country", "City", "Filename"
                ])

                for item in unused:
                    writer.writerow([
                        "📁 Wiki 有但 KML 無",
                        item["path"],
                        item["country"],
                        item["city"],
                        item["filename"]
                    ])

            print(f"✓ Unused files report saved to {output_path}")
            return output_path

        return None

    def print_summary(self):
        """Print validation summary"""
        ok = sum(1 for r in self.results if r.status == "✓")
        error = sum(1 for r in self.results if r.status == "✗")
        missing = sum(1 for r in self.results if r.status == "?")
        total = len(self.results)

        print("\n" + "="*60)
        print("KML-Wiki Validation Report")
        print("="*60)
        print(f"總 POI 數: {total}")

        if total == 0:
            print("沒有 POI 被載入（KML 檔案可能有問題）")
            return

        print(f"✓ 正確: {ok} ({ok/total*100:.1f}%)")
        print(f"✗ 錯誤: {error} ({error/total*100:.1f}%)")
        print(f"? 未找到: {missing} ({missing/total*100:.1f}%)")

        # Error breakdown
        error_types = {}
        for r in self.results:
            if r.error_type:
                error_types[r.error_type] = error_types.get(r.error_type, 0) + 1

        if error_types:
            print("\n錯誤分類:")
            for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
                print(f"  {error_type}: {count}")

        print("="*60)

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="KML-Wiki Validator (支援 WGII GeoJSON 邊界)")
    parser.add_argument("--kml", default="raw/travel/Zachary's World Trip.kml")
    parser.add_argument("--wiki", default="wiki")
    parser.add_argument("--wgii", default=None, help="WGII 資料路徑 (預設: ./wgii/data)")
    parser.add_argument("--errors-output", default="kml_wiki_validation_errors.csv")
    parser.add_argument("--unused-output", default="kml_wiki_unused.csv")
    parser.add_argument("--strict", action="store_true", default=True)

    args = parser.parse_args()

    print("🌍 KML-Wiki Validator")
    print("=" * 60)
    print(f"KML: {args.kml}")
    print(f"Wiki: {args.wiki}")
    if args.wgii:
        print(f"WGII 邊界: {args.wgii}")
    else:
        print("WGII 邊界: 自動偵測 (./wgii/data)")
    print("=" * 60)

    validator = KMLWikiValidator(args.kml, args.wiki, args.strict, args.wgii)
    validator.validate_all()
    validator.print_summary()

    # 生成報告
    print("\n📋 生成報告...")
    validator.generate_report(args.errors_output)
    validator.find_unused_wiki_files(args.unused_output)

    print("\n✅ 驗證完成")

if __name__ == "__main__":
    main()
