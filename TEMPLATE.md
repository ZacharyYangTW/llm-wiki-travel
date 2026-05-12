# LLM Wiki Template

一個可複製的知識庫系統 template，用於組織和管理結構化知識。

## 快速開始 🚀

### 1️⃣ 複製此資料夾
```bash
cp -r llm_wiki_template/ my_wiki/
```

### 2️⃣ 準備原始檔案
在 `raw/` 中放入你的原始資料：
- `raw/articles/` — 文章或筆記
- `raw/clippings/` — 網頁剪輯或短摘要
- `raw/pdfs/` — PDF 檔案
- `raw/notes/` — 個人筆記
- `raw/personal/` — 個人寫作
- `raw/travel/` — 旅遊相關（Google Maps Clipper）自動擴充
- `raw/images/` — 圖片或媒體

### 3️⃣ 執行 INGEST 操作
告訴 Claude 處理這個檔案：
```
@Claude: ingest 這個檔案
```

Claude 會自動：
- 讀取原始檔案
- 生成 `wiki/sources/` 條目
- 建立或更新 `wiki/concepts/`
- 記錄到 `wiki/log.md`

### 4️⃣ 查詢和綜合
```
@Claude: 根據我的知識庫，回答這個問題...
```

## 系統架構 (三層)

| 層級 | 目錄 | 用途 | 權限 |
|------|------|------|------|
| **原始層** | `raw/` | 原始檔案 (PDF、Clippings、筆記) | 唯讀 |
| **知識層** | `wiki/` | 結構化知識 (Sources、Concepts、Entities、Synthesis) | 讀寫 |
| **生成層** | `outputs/` | 生成物 (Reports、Lint 結果) | 讀寫 |

## 檔案說明

```
llm_wiki_template/
├── .claude/                      ← Claude Code 的規範與指南（核心）
│   ├── README.md                 ← 導航 + 按需載入規則
│   ├── RULES.md                  ← 完整操作規範
│   ├── guides/                   ← 專題指南
│   │   ├── html-editing-rules.md
│   │   ├── css-standards.md
│   │   ├── html-pitfalls.md
│   │   └── search-engine.md
│   └── settings.local.json       ← 本地權限設定
├── .agent/                       ← 其他 AI agent 的配置
│   └── skill/                    ← 自訂 skill 定義
├── raw/                          ← 原始檔案層（人類擁有，LLM 唯讀）
│   ├── articles/
│   ├── clippings/
│   ├── pdfs/
│   ├── notes/
│   ├── personal/
│   ├── travel/                    ← 旅遊相關（Google Maps 自動擴充）
│   └── images/
├── wiki/                         ← 結構化知識層（LLM 讀寫）
│   ├── sources/                  ← 來源文獻索引
│   ├── concepts/                 ← 概念定義與論述
│   ├── entities/                 ← 實體目錄（人名、地名等）
│   ├── synthesis/                ← 綜合分析與報告
│   ├── outputs/                  ← 生成物 (HTML、Lint 報告)
│   ├── templates/                ← 檔案模板
│   ├── index.md                  ← 索引（系統檔案）
│   ├── log.md                    ← 操作日誌（系統檔案）
│   ├── overview.md               ← 知識庫總覽（系統檔案）
│   └── QUESTIONS.md              ← 開放問題清單（系統檔案）
├── scripts/                      ← 工具腳本
│   ├── lint.py                   ← 檢查工具
│   ├── search_engine/            ← 搜尋引擎
│   └── ...
├── ALLotherAI.md                 ← 給其他 AI 的規範備份
├── TEMPLATE.md                   ← 本檔案
└── README.md                     ← (可選) 你的 wiki 說明
```

## 多語言支援

- **主要語言**：繁體中文
- **名稱約定**：景點/餐廳以英文名稱為主（預設英文）
- **別名系統**：使用 `aliases` 欄位記錄多語言變體

## 核心概念

### INGEST（攝入）
把原始檔案轉換成結構化知識：
- 觸發詞：`ingest`、`攝入`、`處理這個`
- 產出：`wiki/sources/` + `wiki/concepts/` + `wiki/entities/`

### QUERY（查詢）
從知識庫檢索並合成答案：
- 觸發詞：直接提問、或「根據我的知識庫」
- 產出：Markdown、表格、或圖表

### LINT（檢查）
驗證知識庫的健康度：
- 觸發詞：`lint`、`檢查`、`健康檢查`
- 產出：`wiki/outputs/lint-report.md`

### REFLECT（綜合分析）
挖掘知識之間的規律與洞見：
- 觸發詞：`reflect`、`綜合分析`、`發現規律`
- 產出：`wiki/synthesis/` + 更新 `overview.md`

## 語言規範

- **Wiki 層統一繁體中文**
- **Wikilink 使用英文小寫連字符**：`[[concept-name]]`
- **中文名稱放在 `aliases` 欄位**
- **UTF-8 (無 BOM) 編碼保存**

## 快速查詢

**詳細規範見：**
- 📖 操作規範 → `.claude/RULES.md`
- 🎯 按需載入規則 → `.claude/README.md`
- 📝 HTML 編輯 → `.claude/guides/html-editing-rules.md`
- 🔍 知識庫搜尋 → `.claude/guides/search-engine.md`

---

**Template 版本**：1.0  
**最後更新**：2026-05-09  
**維護者**：Claude Code
