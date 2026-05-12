# Classify Unknown Locations Skill

## 目的
自動將 `wiki/未知` 和 `wiki/其他` 中的檔案根據地理編碼結果重新分類到正確的國家/城市資料夾。

## 使用方式
```
/classifyUnknown
```

## 工作流程

### Step 1: 讀取成功的地理編碼 CSV
- 尋找最新的 `batch2_success.csv` 或用戶指定的 CSV 檔案
- 解析 CSV 並建立座標映射表：`{lng,lat} → {city, country}`

### Step 2: 國家名稱標準化
使用以下對應表將英文國家名轉換為中文：
```
China → 中國
Taiwan → 台灣
Japan → 日本
Thailand → 泰國
Vietnam → 越南
Cambodia → 柬埔寨
Malaysia → 馬來西亞
Singapore → 新加坡
United States → 美國
Canada → 加拿大
Hong Kong → 香港
Macao → 澳門
South Korea → 韓國
India → 印度
Egypt → 埃及
Netherlands → 荷蘭
New Zealand → 紐西蘭
```

### Step 3: 掃描並重新分類
遍歷所有檔案：
1. 從檔案的 YAML frontmatter 提取 `coordinates: [lng, lat]`
2. 在座標映射中查詢 `{lng,lat}`
3. 如果找到，讀取 city 和 country
4. 標準化國家名稱
5. 建立目錄結構：
   - **日本**：`wiki/日本/{都道府県}/{市町村}` （兩層）
   - **台灣**：`wiki/台灣/{縣市}/{鄉鎮市區}` （兩層）
   - **中國**：`wiki/中國/{省}/{城市}` （兩層）
   - **其他國家**：`wiki/{country}/{city}` （一層）
6. 將檔案移動到新位置

### Step 4: 生成報告
輸出統計資訊：
- ✅ 已移動: N 個檔案
- ⚠️ 座標未找到: N 個檔案
- ❌ 失敗: N 個檔案
- 📊 總計: N 個檔案

## 預期輸入
使用者應該事先：
1. 上傳 `batch2_retry.csv` 到 Google Sheets
2. 執行 Google Apps Script 的 `reverseGeocode()` 函數
3. 將編碼結果下載為 CSV，並命名為 `batch2_success_<batch-number>.csv` 或告訴我檔案位置

## 檔案位置
- 源檔案：`h:\我的雲端硬碟\llm_wiki_travel\wiki\未知\未分類\*.md`
- 源檔案：`h:\我的雲端硬碟\llm_wiki_travel\wiki\其他\*\*.md`
- CSV 檔案：`h:\我的雲端硬碟\llm_wiki_travel\batch2_success*.csv`
- 目標：`h:\我的雲端硬碟\llm_wiki_travel\wiki\{country}\{city}\*.md`

## 技術詳節

### 座標提取正則表達式
```regex
coordinates:\s*\[([^,]+),\s*([^\]]+)\]
```

### CSV 格式
```
Title,Longitude,Latitude,City,Country
"location-name",lng,lat,"city-name",country-name
```

### 成功標準
- City 欄位有值（非空）
- Country 欄位有值且不是 "未知"

## 上次執行結果 (2026-05-09)
- 總檔案數: 4,646
- 已分類: 689 個
- 座標未找到: 3,953 個（需要下一批地理編碼）
- 失敗: 4 個

## 注意事項
- 檔案移動是破壞性操作，確保 CSV 資料正確無誤
- 如果坐標映射表為空或很小，會提示警告
- 目錄創建失敗會被記錄但不會停止整個流程
