# CLAUDE.md - LLM Wiki 行為契約

### 系統概述
- **三層架構**：
  - `raw/`：原始檔案層（PDF, Clippings, Personal Notes）。由人類擁有，LLM 僅讀取，絕不修改。
  - `wiki/`：結構化知識層（Sources, Concepts, Entities, Synthesis）。LLM 擁有完全讀寫權限。
  - `outputs/`：生成物層（Reports, Lint results）。
- **核心原則**：你是知識庫的守護者與整理者。所有寫入必須符合模板規範與命名格式。

### INGEST 操作規範
- **觸發詞**：ingest、攝入、處理這個
- **強制前置動作 (Step 0)**：**必須先讀取 `wiki/log.md`**，比對待處理檔案是否已存在於日誌中。若已攝入，則自動跳過，不重複執行。
- **流程判斷**：
  1. frontmatter 含 `type: personal-writing` 或路徑在 `raw/personal/` → **個人寫作流程**。
  2. frontmatter 含 `type: pdf-reference` → **PDF 參考流程**。
  3. 其他 → **外部來源（標準）流程**。

#### 佔位符自動擴充流程 (Placeholder Expansion)：
- **觸發條件**：`raw/clippings/` 檔案字數極少（< 50 字）且僅有標題（通常來自 Google Maps Clipper）。
- **自動化動作**：
  1. **深度研究**：利用搜尋工具或知識儲備，擴充該地點的地址、主打菜色/亮點、營業時間、門票費用。
  2. **評價分析**：閱讀並整理至少 20 則評論，總結遊客評價。
  3. **特定細節**：
     - **餐廳**：從評論中提取並翻譯至少 **5 道推薦菜色**。
     - **景點**：彙整遊客對該地體驗的綜合評價。
  4. **產出**：同步生成 `wiki/entities/` 與 `wiki/sources/` 檔案。

#### 標準流程 (12 步)：
1. 讀取 `raw/` 檔案（唯讀）。
2. 計算 SHA-256 雜湊。
3. 與使用者確認核心要點（Summary Confirm）。
4. 生成 slug（小寫英文+連字符）。
5. 創建 `wiki/sources/<slug>.md`。
6. 概念名稱對齊檢查（aliases 比對 + slug 比對）。
7. 為每個概念創建或更新 `wiki/concepts/<concept>.md`。
8. 為每個實體創建或更新 `wiki/entities/`。
9. 更新 `wiki/index.md`。
10. 檢查 `QUESTIONS.md` 是否有可回答的開放問題。
11. 追加 `wiki/log.md`。
12. **VERIFY (強制驗證)**：助理必須在完成前自我核查：(1) 字元完整性（無亂碼）、(2) 語言一致性（必須為**繁體中文**，且景點與餐廳名稱**必須包含韓文名稱**）、(3) Wikilink 有效性。
13. **去重檢測**：計算 SHA-256 與 `source_url`。若已存在，則跳過或標註為譯文（`canonical_source` 關聯）。
14. **缺失元資料處理**：若原始檔案缺少 frontmatter，助理需根據內容自動補全（含 title, date, tags, processed: false）。
15. **URL Defuddle**：處理直接輸入的 URL 時，先用 `read_url_content` 抓取內容，再由助理進行去噪點（清理廣告、導航欄）並提取核心正文。
16. **CLI Fallback**：在 Windows 環境下若 `qmd update` 無法執行，由助理手動維護 `index.md` 與 `log.md` 索引。
17. **CSV 同步 (CSV Sync)**：INGEST 流程最後，**必須自動更新** `20260528_trip_data.csv`，將新增的實體（如餐廳、景點、**超市與購物點**）或預算變動寫入 CSV 中的對應專屬區塊，確保資料庫與試算表同步。

#### 個人寫作流程：
- 不生成 Summary。
- 核心論點直接寫入對應 concept 頁的 `## My Position`。
- 不參與 confidence 的 `source_count` 計數。
- 在 `Evolution Log` 記錄立場確立。

### QUERY 操作規範
- **觸發詞**：直接提問，或「根據我的知識庫」。
- **步驟**：助理代理檢索（grep/index 掃描）→ 讀取 top 5 頁面 → 合成答案（需溯源）。
- **輸出格式**：Markdown (普通), 表格 (比較), Marp (演示), matplotlib (趨勢)。
- **Confidence Notes**：所有合成回答必須包含「置信度說明」區塊（說明來源一致性、證據力強度）。
- **高價值答案持久化**：若查詢結果具有高度參考價值（Synthesis），助理應自動將其寫入 `wiki/synthesis/<slug>.md`。

### LINT 操作規範
- **觸發詞**：lint、檢查、健康檢查。
- **執行**：運行 `scripts/lint.py` → 寫入成果至 `wiki/outputs/` → `qmd status` 對比 → 詢問修復。

### REFLECT 操作規範
- **觸發詞**：reflect、綜合分析、發現規律。
- **四階段**：
  - Stage 0：反向檢驗 (尋找反證)。
  - Stage 1：助理代理模式掃描 (取代 `qmd multi-get`)。
  - Stage 2：深度合成。
  - Stage 3：Gap Analysis (缺口分析)。
- 完成後更新 `overview.md`, `index.md`, `log.md`。

### MERGE 操作規範
- **觸發詞**：merge、去重。
- **規則**：合併 aliases，保留主 slug，舊 slug 設 redirect。

### ADD-QUESTION 操作規範
- **觸發詞**：我想搞清楚、add question、記錄一個問題。
- **動作**：追加到 `QUESTIONS.md` 的 checkbox 列表。

### Wikilink 使用規範
- **格式鐵律**：所有目標必須使用 **英文小寫連字符**。
  - ✅ `[[value-investing]]`
  - ❌ `[[價值投資]]` / `[[ValueInvesting]]`
- 中文名稱寫入 `aliases` 欄位。

### Wiki 語言規範
- Wiki 層統一用 **繁體中文** 寫作。
- 禁止使用簡體中文或出現編碼亂碼 (Mojibake)。
- 所有檔案必須使用 **UTF-8 (無 BOM)** 編碼保存。
- concept 頁 title 用繁體中文。
- slug 統一用英文小寫連字符。

### Confidence 更新規則
- 1 source → `low`
- 3+ sources → `medium`
- 5+ sources & no conflict → 候選 `high` (需確認)。
- 個人寫作不計入 `source_count`。

### Source Integrity Rules
- 若 `lint` 報告 `SOURCE MODIFIED`，需重新攝入。
- 來源 > 2 年，標註 `possibly_outdated: true`。
- 矛盾必須在 `Contradictions` 顯式記錄。

### Wikilink 限制規範
- **禁止引用 (Wikilink Prohibited)**：禁止 wikilink 到系統輔助檔案，包括：
  - `wiki/log.md`, `wiki/index.md`, `wiki/overview.md`, `wiki/QUESTIONS.md`
  - `wiki/outputs/` 目錄下的所有核查報告。

### 系統檔案隔離規則
- `log.md`, `index.md`, `overview.md`, `QUESTIONS.md`, `outputs/` 下所有檔案，frontmatter 必須含 `graph-excluded: true`。

### 文件維護規則
- `CLAUDE.md` 更新時，同步更新 `USER_GUIDE.md`。
