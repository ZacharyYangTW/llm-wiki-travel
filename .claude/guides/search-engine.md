# 本地搜尋引擎使用指南

來自 `/.agent/skill/search_engine.md`。需要全局檢索知識庫時參考。

---

## 系統規格

| 項目 | 規格 |
|------|------|
| **資料庫引擎** | SQLite 3（內建 FTS5 擴充模組） |
| **開發語言** | Python 3.x |
| **索引資料庫** | `knowledge_index.db`（專案根目錄） |

---

## 核心組件

| 組件 | 路徑 | 用途 |
|------|------|------|
| **indexer.py** | `scripts/search_engine/indexer.py` | 掃描 wiki/ + outputs/ 建立 FTS5 索引 |
| **searcher.py** | `scripts/search_engine/searcher.py` | 命令列搜尋介面（支援分類過濾） |
| **knowledge_index.db** | 專案根目錄 | FTS5 索引資料庫 |

---

## 索引範圍

### Wiki 目錄（遞迴掃描）

```
wiki/
├── concepts/
│   ├── CHI/**/*.md
│   ├── CMN700/**/*.md
│   ├── CXL/**/*.md
│   ├── C2C/**/*.md
│   ├── AXI/**/*.md
│   └── 其他 spec/**/*.md
├── sources/
│   ├── AMBA/**/*.md
│   ├── CMN700/**/*.md
│   └── CXL/**/*.md
├── synthesis/
│   ├── CHI/**/*.md
│   └── CMN700/**/*.md
├── entities/*.md
└── 系統檔案（index.md, log.md, overview.md）
```

### HTML 輸出（outputs/）

| 檔案 | 索引方式 | 備註 |
|------|---------|------|
| CMN700_TRM.html | 按 page div 切片 + 按 card 切片 | 自動跳過備份 |
| AMBA_CHI_Spec.html | 同上 | 自動跳過備份 |
| C2C.html | 同上 | 自動跳過備份 |
| wiki_error.html | 同上 | 自動跳過備份 |
| 備份檔（*_bak, *_old, *_日期） | 跳過 | 不索引 |

### 最新索引統計

| 類別 | 條目數 |
|------|--------|
| HTML (cards + pages) | 1,450 |
| CHI | 310 |
| CMN700 | 64 |
| 其他 spec (AXI/AHB/APB/...) | 各 1+ |
| **總計** | ~1,920 |

索引支援 **中文 Unigram 分詞**，實現精準中文檢索。

---

## 使用方式

### 基本搜尋

```bash
PYTHONIOENCODING=utf-8 python scripts/search_engine/searcher.py "RN SAM"
```

**輸出**：所有包含「RN」和「SAM」的頁面

### 限定分類搜尋

```bash
PYTHONIOENCODING=utf-8 python scripts/search_engine/searcher.py "CPAG" --category CMN700
```

**輸出**：CMN700 分類中包含「CPAG」的條目

### 限制結果數量

```bash
PYTHONIOENCODING=utf-8 python scripts/search_engine/searcher.py "Sliding Set Address" --limit 5
```

**輸出**：前 5 條結果

### 參數參考

| 參數 | 說明 | 例子 |
|------|------|------|
| 位置參數 | 搜尋關鍵字 | `"RN SAM"` |
| `--category CAT` | 限定分類 | `--category CMN700` |
| `--limit N` | 限制回傳筆數 | `--limit 5` |

### 可用分類

```
CHI, CMN700, CXL, C2C, AXI, AHB, APB, ATB, GFB, ATP, DTI, LTI, LPI, CXS, HTML, AMBA, other
```

---

## 分類規則

indexer.py 根據檔案路徑自動分類：

| 路徑模式 | 分類 |
|---------|------|
| `wiki/concepts/CHI/**` | CHI |
| `wiki/concepts/CMN700/**` | CMN700 |
| `wiki/concepts/CXL/**` | CXL |
| `wiki/concepts/C2C/**` | C2C |
| `wiki/concepts/AXI/**` | AXI |
| `wiki/sources/AMBA/**` | AMBA |
| `wiki/sources/CMN700/**` | CMN700 |
| `outputs/*.html` | HTML |
| 其他 | other |

---

## 何時執行更新索引

偵測到以下情況時，**必須主動執行**：

```bash
python scripts/search_engine/indexer.py
```

### 觸發條件
- wiki/ 目錄有新增或大幅修改的 .md 檔案
- outputs/ 目錄有新增或重建的 HTML 檔案
- 執行 deep ingest 後
- 目錄結構變動（新增子目錄、檔案搬移）

---

## 搜尋盲點與替代方案

本搜尋引擎基於 SQLite FTS5，存在以下盲點及替代方案：

| 盲點類型 | 描述 | 建議替代方案 |
|---------|------|----------|
| **特殊符號** | `-` (排除), `:` (欄位), `*` (前綴), `"` (短語) 會被解析為指令 | 將符號替換為空格。例如搜 `Table 3 53` 而非 `Table 3-53` |
| **標點符號** | `, . ( ) / \ [ ]` 等會被當成分隔符號忽略 | 改用純關鍵字組合，或改用 **`grep`** 進行精確字串比對 |
| **大小寫** | 系統預設不分大小寫 | 若需區分大小寫（如特定縮寫），改用 **`grep`** |
| **中文雜訊** | 單字索引 (Unigram) 可能搜到語意不符的結果 | 增加關鍵字長度（如搜「原子操作」而非「原子」） |
| **長度限制** | HTML 檔案內容僅索引前 3000 字元 | 若資訊在檔案深處，直接開啟檔案或按章節縮小範圍 |
| **代碼符號** | `->`, `::`, `=>` 等無法被索引 | 涉及代碼細節時，改用 **`grep`** |

### 何時使用 Grep 代替

```bash
# 當需要精確字串比對時（例如代碼或特殊符號）
grep -r "Table 3-53" wiki/
grep -r "src-chi" outputs/

# 當需要區分大小寫時
grep -i "CPAG" wiki/
```

---

## 自動檢索規範

在處理以下任務時，**必須先執行 searcher.py** 檢索相關檔案：

- **CHI / CMN-700 spec 規格查詢**（opcode、暫存器、transaction flow）
- **HTML 手冊內容更新**（確保引用資料為最新）
- **跨檔案技術諮詢**（確認 Single Source of Truth）
- **wiki 概念頁交叉驗證**（檢查概念是否已定義）

---

## 注意事項

### 系統環境
- **Windows console**：可能無法正確顯示 UTF-8，務必加 `PYTHONIOENCODING=utf-8`
- **環境變數**：確保 Python 3.x 在 PATH 中

### 檔案處理
- **Redirect 頁面**：內容以 `redirect:` 開頭的檔案會被自動跳過
- **備份檔**：檔名含 `_bak`、`_old` 或日期戳記的檔案會被自動跳過
- **搜尋無結果**：searcher.py 會自動嘗試拆分關鍵字逐一搜尋

---

## 常見搜尋場景

### 場景 1️⃣：查詢特定 Register

```bash
PYTHONIOENCODING=utf-8 python scripts/search_engine/searcher.py "CCLA" --category CMN700
```

預期：找到 CMN700 中所有關於 CCLA register 的頁面。

### 場景 2️⃣：跨檔案尋找概念定義

```bash
PYTHONIOENCODING=utf-8 python scripts/search_engine/searcher.py "transaction flow"
```

預期：尋找所有提到「transaction flow」的 wiki 頁面。

### 場景 3️⃣：HTML 手冊內容檢索

```bash
PYTHONIOENCODING=utf-8 python scripts/search_engine/searcher.py "Challenge" --category HTML
```

預期：在所有 HTML 手冊中尋找「Challenge」卡片。

### 場景 4️⃣：精確字串查詢（使用 Grep）

```bash
grep -r "src-chi" outputs/
```

預期：找到所有使用 `src-chi` CSS 類別的 HTML 檔案。

---

**來源：** `/.agent/skill/search_engine.md`  
**最後更新：** 2026-05-09
