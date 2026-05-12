# Wiki 目錄結構命名規則

## 原則
- **中國、日本、台灣**：使用中文/日文目錄名
- **其他所有國家**：使用英文目錄名

## 詳細規則

### 🇨🇳 中國
| 層級 | 格式 | 例子 |
|------|------|------|
| 國家 | 中文 | 中國 |
| 省份 | 繁體中文 | 浙江省、廣西壯族自治區 |
| 城市 | 繁體中文 | 杭州、南寧 |
| POI | 繁體中文 | 西湖、靈隱寺 |

### 🇯🇵 日本
| 層級 | 格式 | 例子 |
|------|------|------|
| 國家 | 日文 | 日本 |
| 都道府縣 | 日語漢字 | 東京都、京都府 |
| 市區町村 | 日語漢字 | 新宿区、中央区 |
| POI | 日語漢字 | 浅草寺、スカイツリー |

### 🇹🇼 台灣
| 層級 | 格式 | 例子 |
|------|------|------|
| 國家 | 繁體中文 | 台灣 |
| 縣市 | 繁體中文 | 台北市、高雄市、連江縣 |
| 鄉鎮 | 繁體中文 | 信義區、北竿鎮 |
| POI | 繁體中文 | 101大樓、中正紀念堂 |

### 🌍 其他所有國家
| 層級 | 格式 | 例子 |
|------|------|------|
| 國家 | 英文 | Vietnam, Peru, Brazil, USA |
| 城市/州 | **英文** | Hanoi, Cusco, Arequipa, Texas |
| POI | 英文（或原語言） | Plaza de Armas, Machu Picchu |

## 案例

### ✅ 正確
```
wiki/
├─ 中國/
│  └─ 浙江省/
│     └─ 杭州/
│        └─ 西湖.md
├─ 日本/
│  └─ 東京都/
│     └─ 新宿区/
│        └─ 歌舞伎町.md
├─ 台灣/
│  └─ 台北市/
│     └─ 信義區/
│        └─ 101大樓.md
├─ Vietnam/
│  ├─ Hanoi/
│  │  └─ POI/
│  │     └─ Hoan Kiem Lake.md
│  └─ Ho Chi Minh City/
│     └─ POI/
│        └─ Ben Thanh Market.md
└─ Peru/
   ├─ Cusco/
   │  └─ Machu Picchu.md
   └─ Lima/
      └─ Plaza Mayor.md
```

### ❌ 錯誤
```
wiki/
├─ 越南/              # ❌ 不應該改成中文
│  └─ 河內/           # ❌ 應該是 Hanoi
├─ 秘魯/              # ❌ 不應該改成中文
│  └─ 庫斯科/         # ❌ 應該是 Cusco
│     └─ 馬丘比丘.md  # ❌ 應該是 Machu Picchu
```

## 執行步驟

1. **識別需要修正的目錄**
   - 檢查非中日台國家的目錄
   - 識別使用中文的目錄名

2. **映射英文名稱**
   - 使用座標或景點名稱判斷城市
   - 查詢標準英文名稱

3. **重新命名目錄**
   - 用 Python `os.rename()` 重新命名
   - 保留目錄下的所有檔案和子結構

4. **驗證**
   - 確認檔案數量不變
   - 確認目錄結構完整

## 例外處理

- **已有英文和中文重複目錄**：合併到英文目錄，刪除中文目錄
- **檔案名稱**：不改變（保留原始格式）
- **中日台國家**：保持現狀，不做修改

## 相關國家清單

### 需要檢查的國家
- Vietnam (越南) → English: Hanoi, Da Nang, Ho Chi Minh City...
- Peru (秘魯) → English: Cusco, Lima, Arequipa...
- Brazil (巴西) → English: São Paulo, Rio de Janeiro...
- Egypt (埃及) → English: Cairo, Giza, Luxor...
- Thailand (泰國) → English: Bangkok, Chiang Mai, Phuket...
- Malaysia (馬來西亞) → English: Kuala Lumpur, Penang, Malacca...
- Singapore (新加坡) → English: Singapore
- Indonesia (印尼) → English: Jakarta, Bali, Yogyakarta...
- India (印度) → English: Delhi, Mumbai, Goa...
- 等所有其他國家

### 不需要檢查
- ✅ 中國 (已是繁體中文)
- ✅ 日本 (已是日語漢字)
- ✅ 台灣 (已是繁體中文)
