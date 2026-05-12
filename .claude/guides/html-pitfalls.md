# HTML 手冊常見問題與解決方案

來自 `/.agent/skill/modify-html.md`。遇到 HTML 結構或顯示問題時查詢。

---

## 問題 1️⃣ Sidebar 導航必須使用 JS showPage，禁止 href 錨點跳轉

### 症狀
- Sidebar 點擊後 URL 出現 `#Chapter-2` 這樣的 hash
- 首頁顯示為 `#Chapter-1` 而非乾淨 URL
- 行為與某些手冊不一致

### 根本原因
使用 `<a href="#Chapter-2">` 時，瀏覽器會：
1. 更新 URL 為 `#Chapter-2`
2. 嘗試跳到該錨點
3. 之後才被 JS `e.preventDefault()` 攔截 → URL 已被污染

### 修正方式

**Sidebar `<a>` 標籤：移除 `href`，改用 `data-id`**

```html
<!-- ❌ 錯誤 — 會觸發瀏覽器錨點跳轉 -->
<a href="#Chapter-2" class="chapter-toggle" data-id="Chapter-2">Chapter 2</a>

<!-- ✅ 正確 — 純 JS 控制，無 URL 變化 -->
<a class="chapter-toggle" data-id="Chapter-2" style="cursor:pointer">Chapter 2</a>
```

**JS showPage 函數：移除 URL hash 更新**

```javascript
// ❌ 錯誤 — 每次 showPage 都會更新 URL hash
history.replaceState(null, null, '#' + targetId);

// ✅ 正確 — 不更新 URL，保持乾淨
// 移除該行或註解掉
```

**初始載入：固定起始頁，不讀取 URL hash**

```javascript
// ❌ 錯誤 — 讀取 URL hash 決定首頁
const hash = window.location.hash.substring(1);
showPage(hash || 'Chapter-1');

// ✅ 正確 — 固定從 Chapter-1 開始
showPage('Chapter-1');
```

### 適用範圍

| HTML 檔案 | 導航機制 | 狀態 |
|-----------|---------|------|
| CMN700_TRM.html | `showPage(n)` 數字索引 | ✅ 正確（原生設計） |
| AMBA_CHI_Spec.html | `showPage(targetId)` 字串 ID | ✅ 已修正 |
| C2C.html | 待確認 | — |
| wiki_error.html | `showPage(id)` 字串 ID | 待確認 |

---

## 問題 2️⃣ 新增頁面後必須更新 TOTAL_PAGES 常數

### 症狀
- 新增了 page128-page161（34 個空白頁面）後，sidebar 點擊無反應
- 右邊頁面不顯示
- 只有 page0-127 能正常顯示

### 根本原因
JS 的 `showPage(n)` 函數有範圍檢查：

```javascript
const TOTAL_PAGES = 128;  // ← 舊值
if (n < 0 || n >= TOTAL_PAGES) return;  // n ≥ 128 全部被擋
```

### 修正

更新 `TOTAL_PAGES` 為新的頁面總數（0-indexed）：

```javascript
const TOTAL_PAGES = 162;  // 頁面 0-161，共 162 頁
```

### 檢查清單

新增頁面後必須確認：
- [ ] `TOTAL_PAGES` 常數已更新為新總數
- [ ] Sidebar 的 `data-index` 或 `data-id` 與 page div 的 `id` 匹配
- [ ] `showPage()` 函數能正確找到新頁面的 div
- [ ] 結構驗證通過（div balance = 0）
  ```bash
  python3 -c "
  with open('file.html','r',encoding='utf-8') as f:
      c = f.read()
  print(f'Div balance: {c.count(\"<div\") - c.count(\"</div>\")}')"
  ```

---

## 問題 3️⃣ bit-field 暫存器圖需要 CSS 支援

### 症狀
- 暫存器位元欄位圖呈現為散列純文字
- 位元無法正確排列或著色

### 根本原因
使用了 `<div class="bit-field">` 和 `<div class="bf bf-x">` 等 class，但缺少對應 CSS。

### 修正

在 `<style>` 區塊加入以下 CSS：

```css
.bit-field {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
    margin: 12px 0;
    padding: 8px;
    background: #f8f9fa;
    border: 1px solid var(--border);
    border-radius: 8px;
}

.bf {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-family: monospace;
    border: 1px solid rgba(0,0,0,0.1);
}

.bf-label { font-weight: 700; color: #555; font-size: 11px; }
.bf-p { background: #dbeafe; color: #1e40af; }  /* payload: srcid/tgtid */
.bf-y { background: #fef3c7; color: #92400e; }  /* target ID */
.bf-d { background: #dcfce7; color: #166534; }  /* control bits */
.bf-r { background: #f3f4f6; color: #9ca3af; font-style: italic; }  /* reserved */
.bf-x { background: #fee2e2; color: #991b1b; }  /* valid/special */
```

---

## 問題 4️⃣ Summary Card 錯誤描述（常見模式）

### 症狀
Summary card 的描述與該頁面的章節號和元件名稱不匹配。

### 常見情況

| 頁面 | Summary Card 描述的 | 應該是 |
|------|-------------------|--------|
| page112 (§4.3.4 CCLA) | §4.3.5 CFGM | CCLA |
| page113 (§4.3.5 CFGM) | §4.3.6 CXLAPB | CFGM |
| page111 (§4.3.3 CCG_RA) | §4.3.4 CCLA | CCG_RA |

### 原因推測
HTML 生成時 summary card 的內容被偏移了一個章節。

### 修正規則

**每次完善暫存器頁面時，第一步必須驗證：**
1. Summary card 的內容是否匹配該頁面的 **章節號**
2. Summary card 的元件名稱是否匹配該頁面的 **實際元件**

---

## 問題 5️⃣ Div 不平衡（結構驗證失敗）

### 症狀
- 執行 `Edit` 後出現 div balance 錯誤
- HTML 結構破損

### 檢查方法

```bash
python3 -c "
with open('outputs/file.html','r',encoding='utf-8') as f:
    c = f.read()
opens = c.count('<div')
closes = c.count('</div>')
print(f'<div>: {opens}, </div>: {closes}, balance: {opens - closes}')
"
```

### 預期結果
Balance = 0（開閉標籤數相等）

### 修正
- 檢查 `Edit` 時是否誤刪了 `</div>` 或漏加 `<div>`
- 重新執行 `Edit`，確保新舊字串的括號對稱

---

## 修改前必備步驟

### 檢查清單

```bash
# 1. 備份（使用當前時間戳記）
cp outputs/CMN700_TRM.html "outputs/CMN700_TRM_$(date +%Y%m%d_%H%M).html"

# 2. 修改（使用 Edit 工具，不用 Python 重寫）
# — 使用 Claude 的 Edit 工具進行局部替換

# 3. 驗證 div balance
python3 -c "
with open('outputs/CMN700_TRM.html','r',encoding='utf-8') as f:
    c = f.read()
print(f'Div: {c.count(\"<div\")}/{c.count(\"</div>\")}')"

# 4. 結構驗證（如有驗證腳本）
python scripts/validate_html_structure.py --quiet --trm-only
```

---

## 問題 6️⃣ HTML 總覽手冊必須標註知識庫來源

### 規範
當建立或修改「總覽型 (Synthesis)」的 HTML 手冊時，必須包含一個專屬分頁來標註資料來源。

### 實作方式

1. **Sidebar 導航**：在導覽列末尾新增一個 `sources` 連結
2. **內容分頁**：新增一個 `id="sources"` 的 `page` div，列出所有參考的原始 `.md` 檔案路徑

### 範例程式碼

**Sidebar:**
```html
<div class="nav-item" onclick="showPage('sources')">知識庫來源檔案</div>
```

**Main Content:**
```html
<div id="sources" class="page">
    <h2>知識庫來源檔案 (Spec Sources)</h2>
    <div class="nav-group">
        <div class="nav-title">相關知識庫檔案</div>
        <a class="nav-item" style="border:none" href="file:///C:/absolute/path/to/source.md">source.md</a>
    </div>
</div>
```

### 檢查清單
- [ ] 總覽手冊具備 `sources` 分頁
- [ ] 連結使用絕對路徑 `file:///` 確保本地端可點擊
- [ ] 樣式與 CSS 規範保持一致

---

## 修改前終極檢查清單

- [ ] 已備份原始 HTML 檔案（`filename_YYYYMMDD_HHMM.html`）
- [ ] 已讀取 `guides/html-editing-rules.md`（7 大規則）
- [ ] 已讀取 `guides/css-standards.md`（確保樣式一致）
- [ ] 使用 `Edit` 工具進行 **局部修改**（禁止全文重寫）
- [ ] 修改後驗證 **div balance**（`<div>` 數 = `</div>` 數）
- [ ] 修改後驗證 **樣式一致性**（新增 class 已在 CSS 中定義）
- [ ] 修改後驗證 **資料誠信**（1:1 忠實還原，無縮減或簡化）

---

**來源：** `/.agent/skill/modify-html.md`  
**最後更新：** 2026-05-09
