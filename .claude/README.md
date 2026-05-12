# Claude Code 項目指南 (`.claude/` 目錄)

這個目錄包含所有給 Claude 讀取和遵守的項目規範。

## 核心檔案

| 檔案 | 用途 | 優先級 |
|------|------|--------|
| `RULES.md` | 專案核心操作規範（INGEST、QUERY、LINT 等） | 🔴 必讀 |
| `guides/html-editing-rules.md` | HTML 手冊編輯的 7 大規則 + 檢查清單 | 🟡 修改 HTML 時讀 |
| `guides/css-standards.md` | CSS 全部樣式與佈局規範 | 🟡 設計 HTML 時讀 |
| `guides/html-pitfalls.md` | 常見的 HTML 結構問題與解決方案 | 🟡 遇到問題時讀 |
| `guides/search-engine.md` | 本地搜尋引擎的使用方式與規範 | 🟢 需要時查詢 |

## 使用流程

### 1️⃣ 初次了解項目
閱讀 `RULES.md` 了解核心操作（INGEST、QUERY、LINT 等）。

### 2️⃣ 執行 INGEST 操作
- 參考 `RULES.md` 中的「INGEST 操作規範」
- 遵循 12 步流程 + 強制前置動作
- 完成後檢查 CSV 同步

### 3️⃣ 修改或新建 HTML 手冊
1. 閱讀 `guides/html-editing-rules.md` 的 7 大規則
2. 參考 `guides/css-standards.md` 瞭解樣式規範
3. 遇到問題查詢 `guides/html-pitfalls.md`
4. 使用 `Edit` 工具進行局部修改，禁止全文重寫

### 4️⃣ 執行全域檢索
使用 `guides/search-engine.md` 中的命令進行精確知識庫搜尋。

## 文件來源對照

| `.claude/` 中的檔案 | 原始來源 |
|------------------|---------|
| `RULES.md` | `/ALLotherAI.md`（給其他 AI 的備份檔） |
| `guides/html-editing-rules.md` | `/.agent/skill/SKILL.md` |
| `guides/css-standards.md` | `/.agent/skill/CSS_COMMON.md` |
| `guides/html-pitfalls.md` | `/.agent/skill/modify-html.md` |
| `guides/search-engine.md` | `/.agent/skill/search_engine.md` |

## 按需載入規則 🎯

我會根據使用者的觸發詞和任務自動讀取相應的文件。**無須手動指定。**

### 自動觸發規則

| 觸發詞 / 情境 | 自動讀取 | 優先級 |
|-------------|---------|--------|
| **任務初始化** | `RULES.md` | 🔴 必讀 |
| `ingest`, `攝入`, `處理這個` | `RULES.md` (INGEST 章節) | 🔴 必讀 |
| `修改 HTML`, `編輯 HTML`, `HTML 結構` | `guides/html-editing-rules.md` | 🟡 修改前 |
| `新建 HTML`, `設計 HTML`, `CSS` | `guides/css-standards.md` | 🟡 修改前 |
| `錯誤`, `問題`, `出現`, `不工作`, `無法` (+ HTML 上下文) | `guides/html-pitfalls.md` | 🟠 有問題時 |
| `搜尋`, `查詢`, `找`, `檢索`, `全局` (+ wiki 上下文) | `guides/search-engine.md` | 🟢 需要時 |
| `query`, `根據我的知識庫` | `RULES.md` (QUERY 章節) | 🟡 查詢時 |
| `lint`, `檢查`, `健康檢查` | `RULES.md` (LINT 章節) | 🟢 檢查時 |

### 檔名的語義

- **RULES.md** — 核心操作規範（5 大操作：INGEST、QUERY、LINT、REFLECT、MERGE）
- **html-editing-rules.md** — HTML 編輯的 7 大規則 + 檢查清單
- **css-standards.md** — 完整 CSS 樣式參考（佈局、色彩、卡片、表格等）
- **html-pitfalls.md** — 6 大常見問題 + 修正方案
- **search-engine.md** — 搜尋引擎使用方法 + 場景舉例

### Token 優化策略

✅ **我只會讀取當前任務需要的文件** → 其他文件留在磁碟上，不污染上下文
✅ **同一檔案內，我會精確定位所需章節** → 避免讀取不相關內容
✅ **相同任務不重複讀檔** → 在一個 session 內快取已讀內容

---

## 快速參考

**何時讀哪份文件：**

- 📝 「我要攝入一個新文件」→ `RULES.md` § INGEST 操作規範
- 🎨 「我要修改 HTML 手冊」→ `guides/html-editing-rules.md`
- 🔍 「我需要找某個知識點」→ `guides/search-engine.md`
- ❌ 「HTML 出現問題」→ `guides/html-pitfalls.md`
- 📊 「我要寫一個 wiki 頁面」→ `RULES.md` § Wiki 語言規範

## 設定

`settings.local.json` 記錄了本地權限設定。

---

**最後更新：** 2026-05-09  
**維護者：** Claude Code
