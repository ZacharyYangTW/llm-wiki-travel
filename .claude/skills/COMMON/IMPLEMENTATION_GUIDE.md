# 📋 Wiki 重新整理 - 實現指南（所有國家通用）

## 概述
每個國家都要執行相同的三個 CASE：
- **Case 1**: 驗證已在正確位置的檔案
- **Case 2**: 清空"其他"目錄，移動檔案到正確位置  
- **Case 3**: 處理缺少二級區域層級的檔案

---

## 實現步驟

### 步驟 1: 複製範本
```bash
# 為新國家建立新檔案
cp reorganize_template.py reorganize_{country}.py
cp {country}_rules.md   # 國家特定規則
```

### 步驟 2: 修改配置部分（僅需改 3 個地方）

在新建的 `reorganize_{country}.py` 中，找到「配置部分」，修改：

```python
# 【配置部分 - 針對各國修改】
COUNTRY_NAME = "台灣"              # ← 改為國家名
WIKI_PATH = r"...path...\台灣"    # ← 改為國家 wiki 目錄
GEOJSON_PATH = r"...path...\geojson.json"  # ← 改為國家 GeoJSON 檔案
```

### 步驟 3: 驗證 GeoJSON 格式

確保 GeoJSON 中的 `properties` 包含：
```json
{
  "properties": {
    "level1": "一級區域名",    // 省份、州、都道府縣等
    "level2": "二級區域名"     // 城市、郡、市區町村等
  },
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [...]
  }
}
```

### 步驟 4: 執行三個 CASE

```bash
# Case 1: 驗證正確位置的檔案
python reorganize_{country}.py case=1

# Case 2: 清空"其他"目錄
python reorganize_{country}.py case=2

# Case 3: 處理缺少二級區域層級的檔案
python reorganize_{country}.py case=3
```

### 步驟 5: 檢查結果

每個 case 都會報告：
- 已處理檔案數
- 成功/失敗數
- 無法定位的檔案數
- 執行時間

---

## 國家實作計劃

### 已完成 ✅
| 國家 | 一級區域 | 二級區域 | GeoJSON | Status |
|------|---------|---------|---------|--------|
| 台灣 | 縣市 (22) | 鄉鎮市區 | twtown2010.json | ✅ 進行中 (CASE 2) |

### 待完成 ⏳
| 國家 | 一級區域 | 二級區域 | GeoJSON | Status |
|------|---------|---------|---------|--------|
| 中國 | 省份 (34) | 城市 | - | 🔄 待提供 GeoJSON |
| 日本 | 都道府縣 (47) | 市區町村 | - | 🔄 待提供 GeoJSON |
| 韓國 | 特別市/道 (17) | 市/郡/區 | - | 🔄 待提供 GeoJSON |
| 美國 | 州 (50) | 城市 | - | 🔄 待提供 GeoJSON |
| 越南 | 省份 (63) | 城市 | - | 🔄 待提供 GeoJSON |
| 泰國 | 府 (77) | 縣 | - | 🔄 待提供 GeoJSON |

---

## 常見問題排查

### 問題 1: GeoJSON 無法載入
**檢查**：
- 檔案路徑正確？
- JSON 格式有效？
- `properties` 中有 `level1` 和 `level2`？

### 問題 2: CASE 2 中檔案移動失敗
**可能原因**：
- 源檔案已被移動
- 目標目錄無法建立（權限問題）
- 座標無法找到匹配的區域

**解決**：
- 檢查 `find_correct_region()` 的多邊形邊界
- 驗證座標格式是否正確（`[lng, lat]`）
- 檢查 GeoJSON 的邊界座標是否準確

### 問題 3: 進度報告顯示很多"無位"
**原因**：座標不在任何已定義的區域邊界內
**解決**：
- 檢查座標是否超出國家範圍
- 驗證 GeoJSON 邊界資料的準確性
- 考慮使用備用地理編碼服務

---

## 文件組織結構

```
.claude/skills/
├── COMMON/
│   ├── RULES_TEMPLATE.md           # 規則範本（所有國家共用）
│   ├── reorganize_template.py      # 腳本範本（通用邏輯）
│   ├── IMPLEMENTATION_GUIDE.md     # 本檔案
│   └── GEOJSON_STANDARD.md        # GeoJSON 格式標準
│
├── reorganizeTaiwanDistricts/      # 台灣實現
│   ├── reorganize_taiwan_districts.py
│   └── RULES.md
│
├── reorganizeChina/                # 中國實現（待建）
│   ├── reorganize_china_districts.py
│   └── RULES.md
│
├── reorganizeJapan/                # 日本實現（待建）
│   ├── reorganize_japan_districts.py
│   └── RULES.md
│
└── ...其他國家...
```

---

## 執行時間預估

基於台灣經驗（1000+ 檔案）：
- **CASE 1**: ~1分鐘
- **CASE 2**: ~15-20分鐘（取決於檔案數量）
- **CASE 3**: ~5分鐘

---

## 進度監控

所有腳本都使用相同的進度報告格式：
```
⏱️ [時間] 進度: N/總數 (百分比) | 統計數據 | 預計剩餘時間
```

可以安心看著進度跑，無需人工干預。

---

**文件版本**: v1.0
**最後更新**: 2026-05-12
