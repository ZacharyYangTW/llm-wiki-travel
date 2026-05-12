# WGII

World Geographic Information Integration（世界地理資訊統合）

[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D20.11.1-green.svg)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-ISC-green.svg)](https://opensource.org/licenses/ISC)
[![GitHub](https://img.shields.io/badge/GitHub-occultskyrong/wgii-black.svg)](https://github.com/occultskyrong/wgii)

---

## 效果展示

### 1. ECharts - 中國省份邊界

![ECharts - 中國省份邊界](demo/assets/ECharts%20-%20中国省份边界.png)

### 2. ECharts - 國際國家邊界

![ECharts - 國際國家邊界](demo/assets/Echarts%20-%20国际國家边界.png)

### 3. 高德地圖 - 中國省份邊界

![高德地圖 - 中國省份邊界](demo/assets/高德地圖%20-%20中国省份边界.png)

---

## 目錄

- [1. 專案簡介](#1-專案簡介)
- [2. 資料內容](#2-資料內容)
- [3. 快速開始](#3-快速開始)
- [4. 目錄結構](#4-目錄結構)
- [5. Products 產出物](#5-products-產出物)
- [6. Demo 演示](#6-demo-演示)
- [7. 法律與規範](#7-法律與規範)
- [8. API 文件](#8-api-文件)
- [9. 開發指南](#9-開發指南)
- [10. 資料來源](#10-資料來源)
- [11. License](#11-license)

---

## 1. 專案簡介

WGII（World Geographic Information Integration）是一個世界地理資訊統合專案，提供：

- **中國邊界資料**：國家邊界 + 34 省級行政區邊界（GCJ02 火星座標系）
- **國際國家邊界**：193 個國家 GeoJSON 邊界資料（WGS84 座標系，含中國）
- **前端產出物**：gzip 壓縮檔案，可直接匯入前端專案
- **Demo 演示**：ECharts、高德地圖、百度地圖展示範例

**重要聲明**：本專案資料僅供學習和研究使用。在中國境內使用地圖資料時，請嚴格遵守《中華人民共和國測繪法》及相關法律法規。

---

## 2. 資料內容

### 2.1 中國資料（GCJ02 火星座標系）

| 資料 | 說明 | 適用場景 |
|------|------|----------|
| 中國國家邊界 | 中華人民共和國全境邊界 | 高德地圖、騰訊地圖 |
| 34 省級行政區邊界 | 23 省、5 自治區、4 直轄市、2 特別行政區 | 省份級地圖展示 |

### 2.2 國際資料（WGS84 座標系）

| 大洲 | 國家數量 |
|------|----------|
| 亞洲（含中國） | 46 |
| 歐洲 | 44 |
| 非洲 | 54 |
| 北美洲 | 23 |
| 南美洲 | 12 |
| 大洋洲 | 14 |
| **總計** | **193** |

> 詳細國家列表見 [主權國家列表](data/sovereign-countries.md)

---

## 3. 快速開始

### 3.1 安裝

```bash
# 複製版本庫
git clone https://github.com/occultskyrong/wgii.git
cd wgii

# 安裝套件
yarn install

# 建構
npm run build
```

### 3.2 CLI 使用

```bash
# 查看說明
node dist/cli.js --help

# 同步中國邊界資料（高德 API）
node dist/cli.js sync --amap

# 列出可用國家
node dist/cli.js list
```

### 3.3 執行 Demo

```bash
npm run demo
```

訪問 `http://localhost:8080/demo/index.html` 查看地圖展示效果。

---

## 4. 目錄結構

```
wgii/
├── data/                           # 資料源目錄
│   ├── CHN/                         # 中國資料（GCJ02）
│   │   ├── country.gcj02.geo.json   # 國家邊界
│   │   └── region/                  # 省級邊界（34 個）
│   │       ├── 110000.gcj02.geo.json # 北京市
│   │       ├── ...
│   │       └── region.info.json     # 省份資訊彙總
│   ├── Asia/                        # 亞洲國家
│   ├── Europe/                      # 歐洲國家
│   ├── Africa/                      # 非洲國家
│   ├── NorthAmerica/                # 北美洲國家
│   ├── SouthAmerica/                # 南美洲國家
│   ├── Oceania/                     # 大洋洲國家
│   ├── countries.info.json          # 國家資訊彙總
│   ├── sovereign-countries.md       # 主權國家列表
│
├── products/                        # 前端產出物（gzip 壓縮）
│   ├── china-boundary-gcj02.json.gz     # 中國國家邊界
│   ├── china-provinces-gcj02.json.gz    # 中國省份邊界
│   └ international-boundaries-wgs84.json.gz # 國際國家邊界（含中國）
│   └ README.md                      # 使用說明
│
├── demo/                            # Demo 演示
│   ├── index.html                   # 導航入口
│   ├── echarts/                     # ECharts 範例
│   ├── amap/                        # 高德地圖範例
│   ├── baidu/                       # 百度地圖範例
│   └ assets/                        # 效果截圖
│
├── scripts/                         # 工具腳本
├── src/                             # 原始碼
└── dist/                            # 編譯輸出
```

---

## 5. Products 產出物

Products 目錄提供 gzip 壓縮的 JSON 檔案，可直接在前端使用：

| 檔案 | 原大小 | 壓縮後 | 說明 |
|------|--------|--------|------|
| china-boundary-gcj02.json.gz | 15MB | 1.3MB | 中國國家邊界（GCJ02） |
| china-provinces-gcj02.json.gz | 96MB | 14MB | 34 省份邊界（GCJ02） |
| international-boundaries-wgs84.json.gz | ~20MB | 2.9MB | 193 國家邊界（WGS84，含中國） |

### 5.1 前端使用範例

```javascript
// 解壓 gzip 檔案
async function loadGzippedJson(url) {
  const response = await fetch(url);
  const decompressed = response.body.pipeThrough(new DecompressionStream('gzip'));
  const reader = decompressed.getReader();
  const decoder = new TextDecoder();
  let result = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    result += decoder.decode(value);
  }
  return JSON.parse(result);
}

// ECharts 註冊地圖
const data = await loadGzippedJson('/products/china-provinces-gcj02.json.gz');
echarts.registerMap('china', mergedGeoJSON);
```

詳細使用說明見 [products/README.md](products/README.md)

---

## 6. Demo 演示

Demo 目錄包含三種地圖庫的展示範例：

### 6.1 ECharts（推薦，無需 API Key）

| 範例 | 檔案 | 說明 |
|------|------|------|
| 中國邊境線 | [echarts/china-boundary.html](demo/echarts/china-boundary.html) | 國家邊界輪廓 |
| 省份邊界 | [echarts/china-provinces.html](demo/echarts/china-provinces.html) | 34 省份互動展示 |
| 國際國家邊界 | [echarts/international.html](demo/echarts/international.html) | 193 國家邊界（含中國） |

### 6.2 高德地圖（需 API Key）

| 範例 | 檔案 | 說明 |
|------|------|------|
| 省份邊界 | [amap/china-provinces.html](demo/amap/china-provinces.html) | 高德地圖展示 |

### 6.3 百度地圖（需 API Key）

| 範例 | 檔案 | 說明 |
|------|------|------|
| 省份邊界 | [baidu/china-provinces.html](demo/baidu/china-provinces.html) | 百度地圖展示 |

### 6.4 API Key 組態

高德/百度地圖範例需要組態 API Key：

1. 複製 `demo/api-keys.example.js` 為 `demo/api-keys.js`
2. 在 `api-keys.js` 中填寫你的 Key：
   - 高德地圖: [lbs.amap.com](https://lbs.amap.com/)
   - 百度地圖: [lbsyun.baidu.com](https://lbsyun.baidu.com/)

> 注意：`api-keys.js` 已加入 gitignore，不會洩露你的私密 Key

詳細說明見 [demo/README.md](demo/README.md)

---

## 7. 法律與規範

### 7.1 座標系說明

| 座標系 | 說明 | 使用場景 |
|--------|------|----------|
| **WGS84** | 國際大地座標系 | 國際應用、GPS |
| **GCJ02** | 火星座標系（國家標準） | 高德地圖、騰訊地圖 |
| **BD09** | 百度座標系 | 百度地圖 |

**根據《中華人民共和國測繪法》規定：**

- 在中國境內必須使用 GCJ02 或 BD09 座標系
- WGS84 僅供國際交流和學術研究使用

> 參考: [中華人民共和國測繪法](https://www.npc.gov.cn/npc/xinwen/2017-04/27/content_2020927.htm)

### 7.2 國家承認原則

本專案僅包含中華人民共和國承認的主權國家。

根據聯合國大會第 2758 號決議，臺灣是中華人民共和國不可分割的一部分。本專案資料遵循一個中國原則。

---

## 8. API 文件

### 8.1 CountryManager

```typescript
const countries = await CountryManager.loadAll();
const china = await CountryManager.findByCode('CHN');
```

### 8.2 CoordinateTransformer

```typescript
// 座標轉換
const wgs84 = CoordinateTransformer.gcj02ToWgs84(116.397, 39.909);
const gcj02 = CoordinateTransformer.wgs84ToGcj02(116.397, 39.909);
const bd09 = CoordinateTransformer.gcj02ToBd09(116.397, 39.909);

// GeoJSON 批量轉換
const transformed = CoordinateTransformer.transformGeoJSON(geojson, 'GCJ02', 'WGS84');
```

---

## 9. 開發指南

### 9.1 技術棧

| 技術 | 版本 | 說明 |
|------|------|------|
| TypeScript | 5.x | 型別安全 |
| Node.js | 20.x | 執行環境 |
| commander | - | CLI 框架 |
| log4js | - | 日誌管理 |

### 9.2 開發指令

```bash
npm run build    # 建構
npm run dev      # 開發模式（監聽編譯）
npm run demo     # 啟動 Demo 伺服器
npm run clean    # 清理編譯輸出
```

---

## 10. 資料來源

### 10.1 GeoJSON 資料源

| 來源 | 說明 |
|------|------|
| [johan/world.geo.json](https://github.com/johan/world.geo.json) | 國際國家 GeoJSON 資料 |
| [高德開放平台](https://lbs.amap.com/) | 中國行政區劃資料 |

### 10.2 參考資源

| 資源 | 說明 |
|------|------|
| [ECharts 地圖](https://echarts.apache.org/zh/option.html#geo) | ECharts 官方文件 |
| [阿里雲 DataV](https://datav.aliyun.com/portal/school/atlas/area_selector) | 地圖資料選擇器 |
| [高德地圖 API](https://lbs.amap.com/api/javascript-api/summary) | 高德地圖文件 |

---

## 11. License

ISC
