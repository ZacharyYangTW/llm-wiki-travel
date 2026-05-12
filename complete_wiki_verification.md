# Wiki 完整性驗證和清點規則

## 目的

根據 KML 檔案（Zachary's World Trip.kml）中的景點數據，對台灣和日本的 Wiki 目錄進行 **1:1 清點驗證**，確保：
1. KML 中的所有景點都在 Wiki 中有對應的檔案
2. Wiki 中的所有檔案都能在 KML 中找到對應景點
3. 缺失的景點從 KML 提取並建立檔案
4. 多餘的檔案（Wiki-only）被識別並標記

---

## 資料來源

**來源檔案**: `raw/travel/Zachary's World Trip.kml`

**檔案格式**: Google Maps KML 格式
- 包含全球 9,112 個 POI
- 台灣 POI：約 1,200+ 個
- 日本 POI：約 1,969 個

**KML 結構**:
```xml
<Placemark>
  <name>景點名稱</name>
  <description>景點描述</description>
  <Point>
    <coordinates>經度,緯度,0</coordinates>
  </Point>
</Placemark>
```

---

## 驗證流程

### Step 1: 逐個縣市/都道府縣處理

針對每個縣市（台灣 22 個）或都道府縣（日本 47 個），執行以下步驟：

```
台灣/台北市
├─ 中正區
├─ 大同區
├─ ... (11 個行政區)
└─ Wiki Only 檔案（KML 中找不到的）
```

### Step 2: 逐個鄉鎮市區清點

**對於每個鄉鎮市區（例如台灣/台北市/中正區）：**

#### A. 掃描 KML
- 根據座標範圍找出該區內的所有 POI
- 提取景點名稱、描述、座標

#### B. 掃描 Wiki
- 列出該區目錄下的所有 .md 檔案
- 提取每個檔案的座標和景點名稱

#### C. 進行 1:1 比對

```
KML 中的景點 ↔ Wiki 檔案

狀態分類：
✓ 完全匹配：景點名稱和座標都在 Wiki 中
✗ 缺失：KML 有但 Wiki 沒有 → 需要從 KML 建立檔案
⚠ 多餘：Wiki 有但 KML 沒有 → Wiki Only 檔案
```

**匹配邏輯**:
- 優先按景點名稱進行精確匹配
- 如名稱不完全匹配，則按座標近似度（誤差範圍 < 0.01 度）進行匹配
- 同一區內，座標相同或極近的檔案，認為是同一景點

### Step 3: 處理缺失的景點

**針對 KML 有但 Wiki 沒有的景點：**

1. 建立 Markdown 檔案位置：
   ```
   wiki/{國家}/{縣市}/{鄉鎮市區}/{景點名稱}.md
   ```

2. Frontmatter 格式：
   ```yaml
   ---
   title: {景點英文或本地名稱}
   slug: {小寫英文，以連字符分隔}
   location: {鄉鎮市區名稱}
   country: {國家中文名}
   city: {縣市名稱}
   category: 景點
   tags: ["景點"]
   coordinates: [{經度}, {緯度}]
   md5: 
   created_at: {ISO 8601 時間戳}
   processed: false
   graph-excluded: false
   source_url: raw/travel/Zachary's World Trip.kml
   source_type: kml-placemark
   ---
   ```

3. 內容格式：
   ```markdown
   # {景點名稱}
   
   ## 基本資訊
   
   **位置：** {鄉鎮市區名稱}
   **國家：** {國家中文名}
   **座標：** {經度}, {緯度}
   
   ## 描述
   
   {KML 中的描述文字，如無則顯示「待補充」}
   ```

4. 檔名規則：
   - 使用景點英文或本地名稱
   - 移除特殊字符（/, \, :, *, ?, ", <, >, |）
   - 保留空格
   - 若檔名過長（超過 255 字）：截短並加 `...`

### Step 4: 標記 Wiki Only 檔案

**針對 Wiki 有但 KML 沒有的檔案：**

1. 在控制台輸出標記為 `⚠ Wiki Only`
2. 記錄檔案位置和座標
3. 可能原因：
   - 使用者手動添加的景點
   - 重複檔案（名稱變體）
   - 座標誤差超過匹配範圍
   - 景點已從 Google Maps 移除

---

## 重複排除規則

### 名稱匹配

在進行 1:1 比對時，對景點名稱進行模糊匹配：

```python
# 移除常見後綴
"高山-Country Hotel Takayama" → 匹配到 "高山市"
"台北101 觀景台" → 匹配到 "台北 101"

# 繁簡轉換
"北京" ↔ "北京" (保持一致)

# 日文標音和漢字
"東京(とうきょう)" → 匹配到 "東京"
```

### 座標近似匹配

- 誤差範圍：< 0.01 度（約 1.11 km）
- 用於處理 GPS 誤差或多個入口點

---

## 統計和報告

### 處理結果統計

每個鄉鎮市區的統計：

```
台灣/台北市/中正區:
├─ KML 景點: 45 個
├─ Wiki 檔案: 43 個
├─ ✓ 完全匹配: 42 個
├─ ✗ 缺失: 3 個 (需新增)
└─ ⚠ Wiki Only: 1 個 (需確認)
```

### 全國統計

```
台灣:
  縣市: 22 個
  鄉鎮市區: 368 個（含 23 個特殊行政區）
  總計 KML 景點: 1,200+ 個
  總計 Wiki 檔案: 1,289 個
  完全匹配: XXXX 個
  缺失景點: XXXX 個
  Wiki Only: XXXX 個

日本:
  都道府縣: 47 個
  市町村: 201+ 個
  總計 KML 景點: 1,969 個
  總計 Wiki 檔案: 2,757 個
  完全匹配: XXXX 個
  缺失景點: XXXX 個
  Wiki Only: XXXX 個
```

---

## 執行流程

### 日常執行

1. **按縣市/都道府縣順序**：台灣 22 個 → 日本 47 個
2. **按鄉鎮市區順序**：依縣市下的所有區進行清點
3. **產生報告**：輸出每個區的清點結果和差異摘要
4. **交互式處理**：
   - 提示用戶確認 Wiki Only 的檔案是否保留
   - 選擇是否自動建立缺失的景點檔案

### 驗證標準

清點完成的標準：
- ✓ 所有 KML 景點都有 Wiki 檔案（缺失 = 0）
- ✓ 所有 Wiki 檔案都能在 KML 中找到對應（Wiki Only 已確認）
- ✓ 座標驗證通過（所有檔案在正確的縣市/區）
- ✓ Frontmatter 格式正確
- ✓ 檔案編碼為 UTF-8

---

## 相關腳本

| 腳本名稱 | 功能 |
|---------|------|
| `complete_wiki_verification.py` | 1:1 清點驗證主程式 |
| `verify_district_completeness.py` | 按鄉鎮市區驗證 |
| `extract_missing_pois.py` | 從 KML 提取缺失景點並建立檔案 |
| `mark_wiki_only_files.py` | 識別和標記 Wiki Only 檔案 |
| `taiwan_cities_coords.py` | 台灣縣市/鄉鎮市區座標表 |
| `japan_towns_coords.py` | 日本都道府縣/市町村座標表 |
| `china_cities_coords.py` | 中國省份/城市座標表 |

---

## 執行注意事項

### 前置條件
- ✓ `raw/travel/Zachary's World Trip.kml` 存在且有效
- ✓ `wiki/台灣/` 目錄結構已建立（22 個縣市 + 368 個鄉鎮市區）
- ✓ `wiki/日本/` 目錄結構已建立（47 個都道府縣 + 201 個市町村）
- ✓ 所有現有 Wiki 檔案都有有效的座標 (coordinates 欄位)

### 執行時間估計
- 掃描 KML: 約 5-10 秒
- 掃描 Wiki: 約 10-20 秒
- 1:1 比對: 約 30-60 秒（按區計算，368 個台灣區 + 201 個日本區）
- 建立缺失檔案: 視缺失景點數量
- **總耗時**: 約 5-10 分鐘

### 背景執行
- 支持背景執行
- 建議在 Wiki 無人編輯時執行
- 不影響現有檔案（只新增缺失）
- 生成詳細的執行日誌

---

## 版本日期

- **建立日期**: 2026-05-10
- **規則版本**: 2.0（修正為 1:1 清點驗證）
- **對應系統**: wiki v2025+

---

## 相關文件

- `complete_wiki_verification.py` - Wiki 完整性驗證程式
- `taiwan_cities_coords.py` - 台灣縣市/鄉鎮市區座標表
- `japan_towns_coords.py` - 日本都道府縣/市町村座標表  
- `raw/travel/Zachary's World Trip.kml` - 景點 KML 原始檔
