# HTML 手冊編輯 7 大規則

來自 `/.agent/skill/SKILL.md`。修改任何 HTML 手冊時必須遵守。

## 規則 1️⃣ 精確手動編輯 (Manual Precision Editing)

### 原則
**禁止** 使用 Python 腳本或自動化工具「重建」或「重新生成」整個 HTML 結構。

### 正確做法
使用 `Edit` 工具進行 **局部且精確的內容替換**，確保原始佈局、導覽 ID 及微小細節不被破壞。

### ❌ 反例
```bash
# 錯誤 — 重寫整個檔案
python rebuild_html.py inputs/manual.md outputs/result.html
```

### ✅ 正例
```
Edit 工具：old_string → new_string 局部替換
```

---

## 規則 2️⃣ 自動化備份機制

### 步驟
修改任何 HTML **前**，自動執行備份。

### 備份命令
```bash
cp filename.html filename_20260509_1530.html
```

### 備份命名格式
`filename_YYYYMMDD_HHMM.html`（使用當前系統時間）

### 為什麼重要
出錯時能立刻還原。這是修改前 **不可省略的預置步驟**。

---

## 規則 3️⃣ 資料誠信 (Data Fidelity)

### 原則
同步內容到 HTML 時，**必須 1:1 忠實還原**。

### 禁止項
- 內容縮減
- 文字簡化
- 欄位省略
- 任何形式的資訊損失

### 檢查清單
- [ ] 每一行字完全一致
- [ ] 每一個符號完全一致
- [ ] 原始文件與 HTML 內容映射 100% 對應

---

## 規則 4️⃣ 樣式同步 (CSS Synchronization)

### 必須自動校對
每次修改 HTML 時，必須檢查 `guides/css-standards.md` 中的樣式定義。

### 確保事項
- 所有標籤與類別符合 CSS 參考文件
- 若樣式發生變動，**同步更新** `guides/css-standards.md`（或 `/.agent/skill/CSS_COMMON.md`）

### 分類
| 節次 | 用途 |
|------|------|
| 第 1~9 節 | 所有 HTML 手冊共用（變數、表格、卡片、徽章、來源標籤） |
| 第 10~11 節 | CMN-700 TRM 專用（Challenge 卡片、進度條） |

---

## 規則 5️⃣ 搜尋引擎系統

### 何時觸發
當涉及全局檢索或查閱 CHI spec 知識庫時。

### 必須行為
**自動載入並閱讀** `guides/search-engine.md` 以取得詳細操作規範。不在此重複，按需載入。

---

## 規則 6️⃣ 高效搜尋指令 (Ripgrep Integration)

### 場景
全域檢查、跨檔案校驗、欄位比對。

### 必須優先使用
**Grep 工具**（底層為 ripgrep）。

### 為什麼
- 確保修改範圍精確
- 無遺漏地檢查全部匹配項

---

## 規則 7️⃣ 文字顏色與對比度 (High Contrast Requirement)

### 原則
**禁止在 HTML 中使用淺灰色或低對比度的文字**。

### 禁止色彩
- `#999`、`#666`、`var(--muted)`（如其值為灰色）

### 預設顏色
- 優先使用 `#000` (Black) 或 `#1a1a1a` (Deep Grey)

### 例外
- 無意義的裝飾線
- Placeholder 文字

### CSS 變數建議
```css
:root {
    --text: #000;        /* 正文 → 黑色 */
    --muted: #000;       /* 副標題 → 深色，確保對比度 */
}
```

### 檢查清單
- [ ] 所有技術描述文字均為黑色 (`#000`)
- [ ] 導覽列標題 (nav-title) 與標籤對比度足夠
- [ ] 程式碼區塊內文清晰

---

## 檔案位置總覽

| 檔案 | 用途 | 載入時機 |
|------|------|---------|
| `guides/html-editing-rules.md` | 本檔案 — 7 大規則 | 每次修改 HTML 時 |
| `guides/css-standards.md` | CSS 樣式規範 | 修改任何 HTML 時 |
| `guides/html-pitfalls.md` | 常見問題與解決方案 | 遇到問題時 |
| `guides/search-engine.md` | 搜尋引擎操作規範 | 需要全局檢索時 |

---

## HTML 手冊清單

| 手冊 | 位置 | CSS 樣式來源 | 佈局類型 |
|------|------|----------|---------|
| RNF_consideration.html | `outputs/` | VP 風格（內嵌） | 固定 sidebar + margin-left |
| CMN-700 TRM | `outputs/` | `guides/css-standards.md` | flex sidebar + 搜尋框 |
| AMBA_CHI_Spec.html | `outputs/` | 同上 | 展開式導覽 |
| 新建手冊 | `outputs/` | 建議 VP 風格 | 較簡潔，相容性佳 |

---

## 修改前檢查清單

- [ ] 已備份原始 HTML 檔案（`filename_YYYYMMDD_HHMM.html`）
- [ ] 已讀取 `guides/css-standards.md`
- [ ] 已讀取 `guides/html-pitfalls.md`（若涉及已知問題）
- [ ] 使用 `Edit` 工具進行局部修改（非全文重寫）
- [ ] 修改後驗證 div balance：`<div>` 數 = `</div>` 數
- [ ] 修改後驗證樣式一致性（檢查新增 class 是否在 CSS 中定義）

---

**來源：** `/.agent/skill/SKILL.md`  
**最後更新：** 2026-05-09
