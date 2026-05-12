# CSS 共用樣式規範

來自 `/.agent/skill/CSS_COMMON.md`。設計或修改 HTML 時必須參考。

## 適用範圍

| 手冊 | 類型 | 備註 |
|------|------|------|
| RNF_consideration.html | VP 風格（固定 sidebar + margin-left 佈局） | 以 VP_nb_transport_plan.html 為基準 |
| CMN-700 TRM | CMN 風格（flex sidebar + 搜尋框 + 展開式導覽） | 原 CSS_CMN.md |
| 新建手冊 | 建議使用 VP 風格 | 較簡潔，相容性佳 |

---

## 1. CSS 變數 (共用)

所有 HTML 手冊共用的基礎變數：

```css
:root {
    /* 基礎色 */
    --bg: #fafafa;
    --card: #fff;
    --border: #e8e8e8;
    --text: #1a1a1a;
    --muted: #666;
    --accent: #2b6ca3;
    --green: #2e7d32;

    /* 馬卡龍色系 */
    --pink: #ffb3ba;
    --peach: #ffdfba;
    --mint: #baffc9;
    --sky: #bae1ff;
    --purple: #e2baff;

    /* 語義色（note-box 用） */
    --macaron-blue: #dbeafe;
    --macaron-green: #dcfce7;
    --macaron-red: #fee2e2;
    --border-color: #e2e8f0;
}
```

---

## 2. 佈局

### VP 風格（RNF_consideration, VP_nb_transport_plan）

**特點**：固定左側 sidebar + margin-left 主內容

```css
body {
    font: 16px/1.7 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    overflow: hidden;
}

/* Sidebar: 固定左側 */
.sidebar {
    position: fixed;
    top: 0; left: 0;
    width: 260px;
    height: 100vh;
    background: var(--card);
    border-right: 1px solid var(--border);
    padding: 1rem 0;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0,0,0,.04);
}

.sidebar-header {
    padding: 0 1rem .8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: .5rem;
}

.sidebar-header h2 {
    font-size: 16px;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .05em;
}

.nav-group { margin-bottom: 15px; }

.nav-title {
    padding: 6px 1rem;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #999;
    font-weight: 700;
}

.nav-item {
    display: block;
    padding: 6px 1rem;
    color: var(--text);
    font-size: 16px;
    line-height: 1.5;
    border-left: 3px solid transparent;
    transition: all .15s;
    cursor: pointer;
}

.nav-item:hover {
    background: #f0f0f0;
    color: var(--accent);
}

.nav-item.active {
    background: #eef5ff;
    border-left-color: var(--sky);
    color: #3a7bd5;
    font-weight: 600;
}

/* Main content: margin-left 避開 sidebar */
.main-content {
    margin-left: 260px;
    height: 100vh;
    overflow-y: auto;
    background: white;
}

.page {
    padding: 2rem 3rem;
    display: none;
    max-width: 1400px;
    animation: fadeIn .3s ease;
}

.page.active { display: block; }

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### CMN 風格（CMN-700 TRM）

**特點**：flex 佈局 + sidebar 搜尋框 + 展開式導覽

```css
body { display: flex; height: 100vh; }

/* Sidebar: flex 佈局 + 搜尋框 */
.sidebar {
    width: 280px;
    min-width: 280px;
    background: var(--card);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 12px 0;
    display: flex;
    flex-direction: column;
}

.sidebar .search-box {
    margin: 0 12px 8px;
    padding: 8px 12px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 16px;
}

/* 展開式導覽 */
.chapter-group { border-bottom: 1px solid #f0f0f0; }

.chapter-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
}

.chapter-toggle.active {
    background: #eef5ff;
    color: var(--accent);
}

.chapter-toggle .arrow {
    font-size: 12px;
    transition: transform .2s;
    width: 14px;
}

.chapter-toggle .arrow.open { transform: rotate(90deg); }

.sub-item {
    display: block;
    padding: 8px 14px 8px 32px;
    font-size: 16px;
    color: var(--muted);
    cursor: pointer;
}

.sub-item.active {
    background: #eef5ff;
    border-left: 3px solid var(--sky);
    color: var(--accent);
    font-weight: 600;
}

.page-viewport {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
}
```

---

## 3. 文字排版 (共用)

```css
/* VP 風格 h1: 漸層文字 */
h1 {
    font-size: 1.8rem;
    background: linear-gradient(135deg, var(--accent), #7b4f9e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: .5rem;
}

h2 {
    font-size: 1.4rem;
    color: var(--accent);
    margin: 1.5rem 0 .8rem;
    padding-bottom: .4rem;
    border-bottom: 1px solid var(--border);
}

h3 {
    font-size: 1.1rem;
    color: var(--green);
    margin: 1.2rem 0 .6rem;
}

p {
    color: #4a5568;
    line-height: 1.8;
}
```

---

## 4. 表格 (共用)

```css
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

th, td {
    padding: .6rem .8rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
    font-size: 16px;
    line-height: 1.6;
}

th {
    background: #e8f5e9;
    color: var(--green);
    font-weight: 600;
}

tr:hover { background: rgba(186,225,255,.12); }

/* 緊湊表格 */
.compact-table td,
.compact-table th {
    padding: 4px 8px !important;
    font-size: 16px;
    line-height: 1.4;
}
```

---

## 5. 程式碼 (共用)

```css
code {
    background: #f5f5f5;
    padding: .15rem .4rem;
    border-radius: 4px;
    font-family: 'Cascadia Code', 'Fira Code', monospace;
    font-size: 14px;
    color: #555;
}

pre {
    background: #f5f5f5;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    overflow-x: auto;
    margin: 1rem 0;
}

pre code {
    background: none;
    padding: 0;
}
```

---

## 6. 卡片與提示框 (共用)

```css
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

/* 左邊框提示 */
.note {
    background: rgba(186,225,255,.18);
    border-left: 3px solid var(--sky);
    padding: .8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}

.warn {
    background: rgba(255,223,186,.25);
    border-left: 3px solid var(--peach);
    padding: .8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}

.ok {
    background: rgba(186,255,201,.2);
    border-left: 3px solid var(--mint);
    padding: .8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}

.danger {
    background: rgba(255,179,186,.18);
    border-left: 3px solid var(--pink);
    padding: .8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}

/* 大色塊提示框 */
.note-box {
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border-left: 6px solid;
}

.note-blue   { background: var(--macaron-blue); border-color: #3b82f6; }
.note-green  { background: var(--macaron-green); border-color: #22c55e; }
.note-red    { background: var(--macaron-red); border-color: #ef4444; }
.note-orange { background: #fff7ed; border-color: #f97316; }

/* Mermaid 圖表容器 */
.mermaid-wrap {
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0 !important;
    margin: 2rem 0;
    overflow-x: auto;
}

.mermaid {
    width: 100%;
    padding: 0;
    margin: 0;
}
```

---

## 7. 徽章 (共用)

```css
.badge {
    display: inline-block;
    padding: .3rem .7rem;
    border-radius: 20px;
    font-size: 16px;
    font-weight: 600;
}

.badge-high { background: var(--pink); color: #b71c1c; }
.badge-mid  { background: var(--peach); color: #8d5b00; }
.badge-low  { background: var(--mint); color: var(--green); }
```

---

## 8. 來源標籤 (共用)

```css
/* 圓角藥丸標籤 */
.src-tag {
    display: inline-flex;
    align-items: center;
    background: var(--macaron-blue);
    color: #1e40af;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: .8em;
    font-weight: bold;
    margin-bottom: 10px;
}

.src-ref {
    display: inline-flex;
    align-items: center;
    background: #f3e8ff;
    color: #7e22ce;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: .8em;
    font-weight: bold;
    margin-bottom: 10px;
    margin-left: 10px;
    -webkit-text-fill-color: #7e22ce;
}

/* h1 內嵌小標籤（需 -webkit-text-fill-color 覆蓋 h1 漸層） */
.src-chi {
    font-size: .5em;
    background: #fde047;
    color: #000;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 5px;
    font-weight: bold;
    vertical-align: middle;
    border: 1px solid #eab308;
    display: inline-block;
    -webkit-text-fill-color: #000;
}

.src-cmn {
    font-size: .5em;
    background: #86efac;
    color: #000;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 5px;
    font-weight: bold;
    vertical-align: middle;
    border: 1px solid #22c55e;
    display: inline-block;
    -webkit-text-fill-color: #000;
}

.src-other {
    font-size: .5em;
    background: #fbcfe8;
    color: #000;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 5px;
    font-weight: bold;
    vertical-align: middle;
    border: 1px solid #ec4899;
    display: inline-block;
    -webkit-text-fill-color: #000;
}

/* CMN 專用 */
.src-wiki {
    background: var(--mint);
    color: #1b5e20;
}

.src-rmlink {
    background: var(--peach);
    color: #854d0e;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
    text-decoration: none;
    border: 1px solid rgba(133,77,14,0.2);
    display: inline-block;
    transition: all 0.2s;
}

.src-rmlink:hover {
    background: #ffcc80;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transform: translateY(-1px);
}
```

---

## 9. 優先級與特殊標籤 (共用)

```css
.tag-rnf {
    background: #fee2e2;
    color: #991b1b;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: .8em;
    font-weight: bold;
}

.highlight-red {
    color: #ef4444;
    font-weight: bold;
}

.priority-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: bold;
    font-size: .8em;
}

.p0 { background: #fee2e2; color: #b91c1c; }
.p1 { background: #ffedd5; color: #9a3412; }
.p2 { background: #fef9c3; color: #854d0e; }
.p3 { background: #f0fdf4; color: #15803d; }
.p4 { background: #f0f9ff; color: #0369a1; }
```

---

## 10. CMN 專用 — Architect Challenge 卡片

```css
.challenge {
    background: #f3e5f5;
    border-left: 4px solid #9c27b0;
    padding: 18px 22px;
    border-radius: 0 12px 12px 0;
    margin: 24px 0;
    box-shadow: 0 2px 8px rgba(156,39,176,0.1);
}

.challenge-title {
    font-weight: 800;
    color: #7b1fa2;
    margin-bottom: 14px;
    font-size: 16px;
    border-bottom: 1px solid rgba(156,39,176,0.2);
    padding-bottom: 8px;
}

.challenge-q {
    font-weight: 700;
    color: #4a148c;
    margin-top: 14px;
    font-size: 16px;
}

.challenge-a {
    margin-top: 10px;
    color: #311b92;
    font-size: 16px;
    line-height: 1.7;
    background: rgba(255,255,255,0.5);
    padding: 10px 14px;
    border-radius: 6px;
}
```

---

## 11. CMN 專用 — 進度條與計數器

```css
.progress-bar {
    height: 3px;
    background: var(--border);
    position: fixed;
    top: 0;
    left: 280px;
    right: 0;
    z-index: 100;
}

.progress-fill {
    height: 100%;
    background: var(--accent);
    transition: width .3s;
}

.chapter-counter {
    padding: 10px 16px;
    font-size: 16px;
    color: var(--muted);
    border-top: 1px solid var(--border);
    margin-top: auto;
}
```

---

**來源：** `/.agent/skill/CSS_COMMON.md`  
**最後更新：** 2026-05-09
