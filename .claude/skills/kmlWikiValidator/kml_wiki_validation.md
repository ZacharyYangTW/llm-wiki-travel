# KML Wiki 驗證工作進度

## 完成項目 ✅

### 1. KML 資料載入與基本驗證
- ✅ 從 Zachary's World Trip.kml 載入 8,383 個 POI
- ✅ 實現 KML 解析器（使用 lxml recovery mode）
- ✅ 建立基本的點對多邊形地理邊界檢測

### 2. Wiki 結構映射
- ✅ 掃描 wiki 資料夾並建立檔案索引
- ✅ 提取檔案的座標資訊（YAML frontmatter）
- ✅ 實現 POI 位置驗證

### 3. 世界地理資料整合 (WGII)
- ✅ 複製 wgii 版本庫（193 個國家邊界）
- ✅ 將 wgii 所有檔案翻譯成繁體中文（台灣口吻）
- ✅ 添加台灣到 countries.info.json（194 個國家）
  - 首都：臺北 (Taipei)
  - 國家名稱：臺灣 (Taiwan)
  - ISO 代碼：TWN
  - 電話區號：+886
  - 大洲：Asia、次區域：Eastern Asia

---

## 進行中的任務 🔄

### 1. 台灣邊界資料
- ✅ 狀態：完成並已整合到 skill
- 已建立：
  - `wgii/data/Asia/TWN/country.wgs84.geo.json` - WGS84 座標系邊界（MultiPolygon）
  - `wgii/data/Asia/TWN/country.info.json` - 台灣邊界資訊檔案
- 資料來源：taiwan-atlas 專案（Ministry of the Interior）
- ✅ 整合到 skill：GeoJSONBoundaryLoader 類別自動載入

### 2. 中國邊界修改
- ✅ 狀態：完成
- 已移除：8,661 個台灣座標（220 個多邊形環）
- 檔案：`wgii/data/CHN/country.gcj02.geo.json`
- 備份：`wgii/data/CHN/country.gcj02.geo.json.backup`
- ✅ 驗證通過：中國邊界不再包含台灣座標

### 3. Skill 整合 WGII GeoJSON
- ✅ 狀態：完成並已測試
- 新增類別：GeoJSONBoundaryLoader
  - 自動載入 `wgii/data/` 下的所有邊界檔案
  - 支援 Polygon 和 MultiPolygon 格式
  - 動態轉換坐標系統（GCJ02、WGS84）
- 改進的 KMLWikiValidator
  - 使用真實 GeoJSON 邊界而非簡化矩形
  - 精確的點在多邊形內判定
  - 自動備用到簡化邊界（如載入失敗）

---

## 待完成項目 📋

### 1. Taiwan 邊界資料
- [ ] 建立 `wgii/data/Asia/TWN/` 目錄
- [ ] 創建 `country.wgs84.geo.json`（WGS84 座標系）
- [ ] 創建 `country.gcj02.geo.json`（GCJ02 座標系，中國境內使用）
- [ ] 驗證邊界包含範圍：
  - [ ] 臺灣本島
  - [ ] 澎湖縣群島
  - [ ] 金門縣
  - [ ] 連江縣（馬祖）
  - [ ] 其他離島
- [ ] 與 taiwan-atlas 邊界資料比對確認一致性

### 2. 改進 KML 驗證邏輯
- [ ] 集成 wgii GeoJSON 邊界資料
- [ ] 實現精確的點在多邊形內判定
- [ ] 處理邊界爭議地區（例如：9 段線相關地區）
- [ ] 重新運行完整驗證
- [ ] 生成改進後的驗證報告

### 3. POI 重新分類
- [ ] 根據改進的邊界檢測重新分類 POI
- [ ] 處理 NOT_FOUND POI
- [ ] 處理位置錯誤的 POI
- [ ] 生成修正清單

### 4. 座標系統轉換
- [ ] 為台灣添加 GCJ02 座標版本（中國境內使用）
- [ ] 為台灣添加 BD09 座標版本（百度地圖）
- [ ] 驗證坐標轉換精度

---

## 技術規格

### 邊界資料格式
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], ...]]
      },
      "properties": {
        "name": "Taiwan",
        "name_zh": "臺灣",
        "country_code": "TWN",
        "country_code2": "TW"
      }
    }
  ]
}
```

### 座標系說明
- **WGS84**: 國際標準（GPS 使用）
- **GCJ02**: 中國標準（高德、騰訊地圖）
- **BD09**: 百度地圖標準

### POI 驗證邏輯
1. 讀取 KML 中的 POI 座標（WGS84）
2. 從 wiki 檔案提取座標資訊
3. 使用點在多邊形內判定演算法檢測 POI 位置
4. 比對 KML POI 與 wiki 檔案的對應關係
5. 產生驗證報告（正確、錯誤位置、未找到）

---

## 重要注意事項 ⚠️

### 台灣地位聲明
本驗證系統將**臺灣作為獨立國家實體**處理：
- 在 `countries.info.json` 中註冊為 TWN（獨立國家代碼）
- 邊界資料獨立於中國邊界
- POI 驗證時臺灣地區不視為中國領土

### 座標系法律規範
根據《中華人民共和國測繪法》：
- 中國境內使用地圖必須採用 GCJ02 或 BD09
- WGS84 僅供國際交流和學術研究使用

---

## 相關檔案位置

| 檔案 | 位置 | 說明 |
|------|------|------|
| KML 驗證工具 | `.claude/skills/kmlWikiValidator/kml_wiki_validator.py` | 主驗證程式 |
| 國家資訊 | `wgii/data/countries.info.json` | 194 個國家資訊（新增台灣） |
| 邊界資料 | `wgii/data/Asia/*/country.wgs84.geo.json` | GeoJSON 邊界檔案 |
| 台灣邊界工具 | `taiwan-atlas/compBordersGeo.js` | 台灣邊界產生器 |
| KML 來源 | `raw/travel/Zachary's World Trip.kml` | 8,383 個 POI |
| 驗證報告 | `kml_wiki_validation_errors.csv` | 錯誤 POI 清單 |

---

## 下一步行動

1. **優先** 建立台灣邊界 GeoJSON 檔案（`wgii/data/Asia/TWN/`）
2. 集成新邊界資料到驗證工具
3. 重新執行完整驗證
4. 生成改進的驗證報告
5. 根據報告進行 POI 重新分類

---

**最後更新**: 2026-05-12  
**責任人**: Zachary Yang  
**狀態**: 進行中 🔄
