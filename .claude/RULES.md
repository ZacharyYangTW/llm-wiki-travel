# 項目操作規範 (RULES.md)

核心指導文件，來自 `/CLAUDE.md`。

## 系統概述 (三層架構)

| 層級 | 目錄 | 權限 | 用途 |
|------|------|------|------|
| **原始層** | `raw/` | 只讀 | 原始檔案 (PDF、Clippings、筆記) |
| **知識層** | `wiki/` | 讀寫 | 結構化知識 (Sources、Concepts、Entities、Synthesis) |
| **生成層** | `outputs/` | 讀寫 | 生成物 (Reports、Lint 結果) |

## INGEST 操作規範 (最常用)

### 觸發詞
`ingest`、`攝入`、`處理這個`

### 強制前置動作 (Step 0)
**必須先讀取 `wiki/log.md`** → 比對待處理檔案是否已存在。若已攝入，自動跳過。

### 流程判斷 (判斷用哪個流程)

1. **個人寫作流程**：frontmatter 含 `type: personal-writing` 或路徑在 `raw/personal/`
2. **PDF 參考流程**：frontmatter 含 `type: pdf-reference`
3. **標準流程**：其他（最常見）

### 佔位符自動擴充 (Placeholder Expansion)

**觸發條件**：`raw/travel/` 檔案，不管文字多少（Google Maps Clipper）

**自動化動作**：
1. 深度研究：搜尋工具 → 擴充地址、主打菜色/景觀、營業時間、門票費用
2. 評價分析：整理至少 20 則評論或用戶評論
3. 特定細節：
   - **餐廳**：提取至少 5 道推薦菜色（含英文翻譯）
   - **景點**：遊客對該地體驗的綜合評價
4. 同步生成 `wiki/entities/` 與 `wiki/sources/`

### 標準流程 (12 步 + 5 個強化步驟)

**基礎 12 步：**
1. 讀取 `raw/` 檔案（唯讀）
2. 計算 SHA-256 雜湊
3. 與使用者確認核心要點（Summary Confirm）
4. 生成 slug（小寫英文+連字符）
5. 創建 `wiki/sources/<slug>.md`
6. 概念名稱對齊檢查（aliases + slug）
7. 為每個概念創建或更新 `wiki/concepts/<concept>.md`
8. 為每個實體創建或更新 `wiki/entities/`
9. 更新 `wiki/index.md`
10. 檢查 `QUESTIONS.md` 是否有可回答的開放問題
11. 追加 `wiki/log.md`
12. **VERIFY**：(1) 字元完整性、(2) 語言一致性、(3) Wikilink 有效性

**強化步驟：**
13. **去重檢測**：SHA-256 + `source_url`，若已存在則跳過或標註為譯文
14. **缺失元資料處理**：根據內容自動補全 frontmatter（title, date, tags, processed）
15. **URL Defuddle**：直接處理 URL 時，先抓取內容 → 去噪點（清理廣告、導航） → 提取核心正文
16. **CLI Fallback**：Windows 環境下若 `qmd update` 無法執行，由助理手動維護 `index.md` 與 `log.md` 索引
17. **CSV 同步**：更新 `20260528_trip_data.csv`（餐廳、景點、超市與購物點等）

### 語言一致性特別規則 (INGEST Step 12)

- **繁體中文**：所有 wiki 內容統一繁體中文
- **景點與餐廳名稱**：**預設使用英文名稱**，別名中記錄其他語言變體
- **UTF-8 編碼**：所有檔案保存為 UTF-8 (無 BOM)

### 個人寫作流程 (簡化版)

- 不生成 Summary
- 核心論點 → 對應 concept 頁的 `## My Position`
- 不參與 confidence 的 `source_count` 計數
- 在 `Evolution Log` 記錄立場確立

## QUERY 操作規範

### 觸發詞
直接提問、或「根據我的知識庫」

### 執行步驟
1. 代理檢索（grep/index 掃描）
2. 讀取 top 5 頁面
3. 合成答案（需溯源）

### 輸出格式
Markdown、表格、Marp 演示、matplotlib 趨勢圖

### 必須包含「置信度說明」
說明來源一致性、證據力強度

### 高價值答案持久化
查詢結果具高度參考價值 → 自動寫入 `wiki/synthesis/<slug>.md`

## LINT 操作規範

### 觸發詞
`lint`、`檢查`、`健康檢查`

### 執行
1. 運行 `scripts/lint.py`
2. 寫入成果至 `wiki/outputs/`
3. `qmd status` 對比
4. 詢問修復

## REFLECT 操作規範

### 觸發詞
`reflect`、`綜合分析`、`發現規律`

### 四階段
1. **Stage 0**：反向檢驗（尋找反證）
2. **Stage 1**：助理代理掃描
3. **Stage 2**：深度合成
4. **Stage 3**：Gap Analysis（缺口分析）

### 完成後
更新 `overview.md`, `index.md`, `log.md`

## MERGE 操作規範

### 觸發詞
`merge`、`去重`

### 規則
合併 aliases → 保留主 slug → 舊 slug 設 redirect

## ADD-QUESTION 操作規範

### 觸發詞
`我想搞清楚`、`add question`、`記錄一個問題`

### 動作
追加到 `QUESTIONS.md` 的 checkbox 列表

## Wiki 語言規範

### 統一用繁體中文
- 禁止簡體中文或編碼亂碼 (Mojibake)
- 所有檔案必須 UTF-8 (無 BOM) 編碼

### Wiki 檔案名規則

**命名優先級（由高到低）：**
1. **繁體中文**（優先使用）
   - ✅ `燕山大酒店大堂吧.md`、`機場一號客運大樓.md`
2. **該國語言**（如果無中文名稱）
   - 韓語景點：用韓語名稱
   - 日語景點：用日語名稱（如 `富士山.md` 或 `ふじさん.md`）
   - 若該國有特殊語言標準，以該標準為準
3. **英文**（最後備選）
   - ✅ `Eiffel Tower.md`（無中文、無該國語言譯法）

**非英文語言名稱的補充規則：**
- 檔案名可包含該國語言 + 英文
  - ✅ `東大門.md` 或 `Dongdaemun.md`（韓語景點）
  - ✅ `築地市場 Tsukiji Market.md`（日語景點）
  - ✅ `寺院名 Shrine Name.md`（日本寺廟）

**內容編寫規則：**
- **檔案內容一律用繁體中文**（不論景點的原語言）
- 景點的原語言名稱在 frontmatter 或內文中以 `原語言: 名稱` 格式記錄

**目錄結構：**
- ✅ `wiki/中國/北京/`、`wiki/日本/東京/`、`wiki/韓國/首爾/`
- ❌ `wiki/china/beijing/`、`wiki/中国/北京/`

### Wikilink 格式鐵律
所有目標用英文小寫連字符：
- ✅ `[[value-investing]]`
- ❌ `[[價值投資]]` / `[[ValueInvesting]]`

### 中文名稱放 aliases 欄位

## Confidence 更新規則

| 來源數 | 信心度 |
|--------|--------|
| 1 source | `low` |
| 3+ sources | `medium` |
| 5+ sources & no conflict | 候選 `high`（需確認） |
| 個人寫作 | 不計入 `source_count` |

## Source Integrity Rules

- `lint` 報告 `SOURCE MODIFIED` → 需重新攝入
- 來源 > 2 年 → 標註 `possibly_outdated: true`
- 矛盾 → 在 `Contradictions` 顯式記錄

## Wikilink 限制規範 (禁止引用)

禁止 wikilink 到系統輔助檔案：
- `wiki/log.md`, `wiki/index.md`, `wiki/overview.md`, `wiki/QUESTIONS.md`
- `wiki/outputs/` 下所有文件

## 系統檔案隔離規則

以下檔案 frontmatter 必須含 `graph-excluded: true`：
- `log.md`, `index.md`, `overview.md`, `QUESTIONS.md`
- `outputs/` 下所有檔案

---

**來源：** `/CLAUDE.md`  
**最後更新：** 2026-05-09
