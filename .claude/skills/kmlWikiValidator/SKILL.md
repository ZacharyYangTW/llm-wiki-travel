# KML-Wiki Validator Skill

⭐ **已整合 WGII GeoJSON 邊界資料** (2026-05-12)
- 從 `wgii/data/` 動態載入各國邊界
- 台灣作為獨立國家，有獨立的邊界檔案 (`Asia/TWN/country.wgs84.geo.json`)
- 中國邊界已移除台灣部分 (`CHN/country.gcj02.geo.json`)
- 精確的邊界檢測（多邊形而非矩形）

## 目的
驗證 KML 中的每一筆 POI 是否在 wiki 目錄中正確的國家、城市、甚至第二級行政區。

特別對中國、日本、台灣進行嚴格的第二級城市驗證。

## 使用方式
```
/kmlWikiValidator [options]
```

## 選項
- `--kml-path <path>` - KML 檔案路徑（預設：raw/travel/Zachary's World Trip.kml）
- `--wiki-path <path>` - Wiki 目錄路徑（預設：wiki/）
- `--output <file>` - 輸出報告路徑（預設：kml_wiki_validation_report.csv）
- `--strict` - 嚴格模式（中日台強制檢驗第二級）
- `--country <code>` - 只檢驗特定國家（如 CN, JP, TW）

## 工作流程

### Step 1: 解析 KML
- 讀取 Zachary's World Trip.kml
- 提取每個 Placemark：
  - 名稱 (name)
  - 座標 (latitude, longitude)
  - 描述 (description)
  - 其他元數據

### Step 2: 逆地理編碼 (Reverse Geocoding)
- 根據座標判斷國家
- 根據座標判斷城市/地區
- 針對中日台額外判斷第二級行政區

### Step 3: 搜尋 Wiki 檔案
- 在 wiki/{國家}/{城市}/ 中搜尋同名檔案
- 或使用 searcher.py 進行全文搜尋

### Step 4: 驗證規則

**基礎驗證**
- ✓ POI 名稱與 wiki 檔案名稱匹配
- ✓ 座標誤差 < 0.01°（約 1 公里）
- ✓ POI 在正確的國家目錄下

**進階驗證（中日台）**
- ✓ 檔案位置：`wiki/{國家}/{第一級}/{第二級}/`
- ✓ 中國：在正確的省/直轄市下
- ✓ 日本：在正確的都道府縣下
- ✓ 台灣：在正確的縣市下
- ✓ 座標與檔案內 frontmatter 匹配

### Step 5: 生成報告
生成**兩份 CSV 報告**（只含問題項目）：

**kml_wiki_validation_errors.csv** - KML 中的問題
```
問題類型,POI_Name,KML_Coords,Wiki_Path,建議
"❌ KML 未歸類到 Wiki","景點1","(25.1,121.6)","","Wiki 中無此檔案"
"⚠️ 歸類到錯誤位置","景點2","(25.1,121.6)","台灣/新北市/景點2.md","應在台北市"
```

**kml_wiki_unused.csv** - Wiki 中但 KML 無的檔案
```
問題類型,Wiki_Path,Country,City,Filename
"📁 Wiki 有但 KML 無","台灣/台北市/中山區/景點3.md","台灣","台北市","景點3.md"
```

## 錯誤類型

| 代碼 | 描述 |
|------|------|
| `OK` | 完全正確 |
| `WRONG_COUNTRY` | 檔案在錯誤的國家 |
| `WRONG_CITY` | 檔案在錯誤的城市 |
| `WRONG_LEVEL2` | 檔案在錯誤的第二級行政區（中日台） |
| `COORD_MISMATCH` | 座標不符（誤差 > 0.01°） |
| `NOT_FOUND` | Wiki 中未找到此 POI |
| `NAME_MISMATCH` | 檔案名稱與 POI 名稱不符 |
| `MISSING_FRONTMATTER` | Wiki 檔案缺少座標 frontmatter |

## 統計輸出

```
=== KML-Wiki Validation Report ===
總 POI 數: 8,384
✓ 正確: 8,200 (97.8%)
✗ 錯誤: 150 (1.8%)
? 未找到: 34 (0.4%)

錯誤分類:
  WRONG_COUNTRY: 12
  WRONG_CITY: 85
  WRONG_LEVEL2: 45
  COORD_MISMATCH: 8
  NOT_FOUND: 34
```

## 技術細節

### 坐標誤差容許
- 同城市內：±0.01°（約 1 公里）
- 跨城市：不允許

### 第二級行政區判斷
- 中國：22 個省份 + 直轄市
- 日本：47 個都道府縣
- 台灣：22 個縣市

### Wiki 搜尋方式
選項：
1. **Python 目錄遍歷** - 快速，適合已知名稱
2. **searcher.py** - 全文搜尋，適合模糊匹配

## 輸出檔案

| 檔案 | 內容 | 用途 |
|------|------|------|
| `kml_wiki_validation_errors.csv` | 只含 KML 中的問題 POI | 批量修正 KML → Wiki 對應 |
| `kml_wiki_unused.csv` | Wiki 中有但 KML 無的檔案 | 清理多餘的 Wiki 檔案 |

### 三大問題類型

1. **❌ KML 未歸類到 Wiki**
   - KML 中有此 POI，但 wiki 中找不到對應檔案
   - 動作：在 wiki 中建立檔案 或 刪除 KML 中的多餘 POI

2. **⚠️ KML 歸類到錯誤位置**
   - KML POI 被歸類到錯誤的國家/城市
   - 動作：移動 wiki 檔案到正確位置 或 修正 KML 座標

3. **📁 Wiki 有但 KML 無**
   - Wiki 中有此檔案，但 KML 中沒有對應 POI
   - 動作：刪除此 wiki 檔案 或 在 KML 中新增 POI

## 相關

- KML 格式：https://developers.google.com/kml/documentation
- Wiki 結構：已驗證的 22 國家 + 22 台灣縣市 + 47 日本都道府縣
- Searcher：scripts/search_engine/searcher.py
