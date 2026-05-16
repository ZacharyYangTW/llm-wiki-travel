# Sidebar Toggle-Slide 實作指南

修改任何 CMN 風格 HTML 手冊時，若需要為側邊欄加入收起／展開功能，參考本文件。

## 適用條件

- HTML 結構：`body` 為 flex row，`.sidebar` 和 `.page-viewport` 為直接子元素
- 不修改既有 DOM 結構，僅需插入一個 `<button>` 並調整三段 CSS

---

## 1. CSS 修改（三處）

### 1-a. 更新 `.sidebar`

在 `.sidebar` 規則最後加入 transition，並新增 collapsed 狀態和 toggle button：

```css
.sidebar {
  /* 原有規則不變，加入 transition */
  transition: width .25s ease, min-width .25s ease;
}

.sidebar.collapsed {
  width: 0;
  min-width: 0;
  overflow: hidden;
  padding: 0;
}

.sidebar-toggle {
  width: 16px;
  flex-shrink: 0;
  background: var(--card);
  border: none;
  border-right: 1px solid var(--border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--muted);
  transition: background .15s, color .15s;
  padding: 0;
  user-select: none;
  outline: none;
}

.sidebar-toggle:hover {
  background: #eef5ff;
  color: var(--accent);
}
```

### 1-b. 更新 `.page-viewport`

原本 `max-width: calc(100vw - 280px)` 要加上 toggle 按鈕寬度（16px）和 transition：

```css
.page-viewport {
  /* 原有規則，修改 max-width 並加 transition */
  max-width: calc(100vw - 296px);   /* 280px sidebar + 16px toggle */
  transition: max-width .25s ease;
}
```

---

## 2. HTML 修改

在 `.sidebar` 結尾 `</div>` 和 `.page-viewport` 開頭 `<div>` 之間插入一個按鈕：

```html
</div>  <!-- sidebar 結尾 -->
<button class="sidebar-toggle" id="sidebarToggle" title="收起／展開側邊欄">&#9664;</button>

<div class="page-viewport" id="viewport">
```

- `&#9664;` = `◀`（展開狀態）
- `&#9654;` = `▶`（收起狀態）

---

## 3. JavaScript 修改

在 `<script>` 區塊最前面（mermaid.initialize 之後）加入：

```javascript
// Sidebar toggle
(function(){
  const btn = document.getElementById('sidebarToggle');
  const sb  = document.getElementById('sidebar') || document.querySelector('.sidebar');
  const vp  = document.getElementById('viewport');
  btn.addEventListener('click', function(){
    const collapsed = sb.classList.toggle('collapsed');
    btn.innerHTML   = collapsed ? '&#9654;' : '&#9664;';
    btn.title       = collapsed ? '展開側邊欄' : '收起側邊欄';
    vp.style.maxWidth = collapsed ? 'calc(100vw - 16px)' : 'calc(100vw - 296px)';
  });
})();
```

---

## 行為規格

| 狀態 | 按鈕符號 | sidebar 寬度 | page-viewport max-width |
|------|----------|-------------|------------------------|
| 展開（預設） | `◀` | 280px | `calc(100vw - 296px)` |
| 收起 | `▶` | 0px | `calc(100vw - 16px)` |

- 動畫時長：`0.25s ease`，sidebar width 與 page-viewport max-width 同步滑動
- Toggle button 固定 16px 寬，始終可見，hover 時變藍（`--accent`）
- 收起後主內容區自動填滿畫面

---

## 驗證

修改完成後執行：

```bash
python scripts/validate_html_structure.py --quiet --trm-only
```

確認 V-S2 (div balance = 0) 通過。
