/**
 * 從 Google Drive 資料夾自動匯入 CSV 到指定工作表
 * 
 * 使用方式：
 *   1. 在 Google Sheets 中，點選「擴充功能 → Apps Script」
 *   2. 將此檔案內容貼入編輯器
 *   3. 執行 importTripData() 函式進行首次匯入
 *   4. (選用) 執行 setupTrigger() 函式，自動設定「每小時自動同步」
 *   
 * 手動設定觸發器 (UI 方式)：
 *   - 點擊左側「鬧鐘圖示 (觸發條件)」→「新增觸發條件」
 *   - 選擇執行函式：importTripData
 *   - 選擇活動來源：時間驅動
 *   - 選擇時間型觸發器類型：小時計時器 → 每小時
 */

// ==================== 設定區 ====================
const CONFIG = {
  // CSV 檔名（在 Google Drive 中的名稱）
  CSV_FILENAME: "20260528_trip_data.csv",
  
  // Google Drive 資料夾路徑（用來搜尋 CSV）
  // 若 CSV 就在根目錄或你知道資料夾名稱，可填入
  FOLDER_NAME: "20260528-0602_江陵雪嶽山",
  
  // 目標工作表名稱
  SHEET_NAME: "20260528",
};

// ==================== 主函式 ====================

/**
 * 主要進入點：從 Drive 讀取 CSV 並寫入工作表
 */
function importTripData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. 取得或建立目標工作表
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    Logger.log("已建立新工作表: " + CONFIG.SHEET_NAME);
  }
  
  // 2. 在 Drive 中尋找 CSV 檔案
  const csvContent = findAndReadCSV_();
  if (!csvContent) {
    const errorTitle = "找不到檔案";
    const errorMessage = "無法在 Google Drive 中找到 " + CONFIG.CSV_FILENAME + "\n" + "請確認檔案已同步到雲端硬碟。";
    
    Logger.log("ERROR: " + errorTitle + " - " + errorMessage);
    
    // 只有在有 UI 的情況下才顯示警告 (例如手動執行)
    try {
      SpreadsheetApp.getUi().alert(
        errorTitle,
        errorMessage,
        SpreadsheetApp.getUi().ButtonSet.OK
      );
    } catch (e) {
      // 靜默失敗 (觸發器執行時沒有 UI)
    }
    return;
  }
  
  // 3. 解析 CSV
  const data = parseCSV_(csvContent);
  Logger.log("已解析 " + data.length + " 行資料");
  
  // 4. 清除舊資料並寫入新資料
  sheet.clearContents();
  sheet.clearFormats();
  
  if (data.length > 0) {
    const maxCols = Math.max(...data.map(row => row.length));
    // 補齊每行的欄數
    const normalizedData = data.map(row => {
      while (row.length < maxCols) row.push("");
      return row;
    });
    
    sheet.getRange(1, 1, normalizedData.length, maxCols)
         .setValues(normalizedData);
    
    // 5. 套用格式
    applyFormatting_(sheet, normalizedData);
  }
  
  const successMessage = "已成功匯入 " + data.length + " 行資料到「" + CONFIG.SHEET_NAME + "」工作表。";
  Logger.log("SUCCESS: " + successMessage);

  // 只有在有 UI 的情況下才顯示通知
  try {
    SpreadsheetApp.getUi().alert(
      "匯入完成",
      successMessage,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  } catch (e) {
    // 靜默失敗 (觸發器執行時沒有 UI)
  }
}

// ==================== Drive 搜尋 ====================

/**
 * 在 Drive 中搜尋 CSV 檔案並讀取內容
 * 優先在指定資料夾中搜尋，找不到則全域搜尋
 */
function findAndReadCSV_() {
  let file = null;
  
  // 策略 1：在指定資料夾名稱中搜尋
  if (CONFIG.FOLDER_NAME) {
    const folders = DriveApp.getFoldersByName(CONFIG.FOLDER_NAME);
    while (folders.hasNext()) {
      const folder = folders.next();
      const files = folder.getFilesByName(CONFIG.CSV_FILENAME);
      if (files.hasNext()) {
        file = files.next();
        Logger.log("在資料夾「" + CONFIG.FOLDER_NAME + "」中找到 CSV");
        break;
      }
    }
  }
  
  // 策略 2：全域搜尋檔名
  if (!file) {
    const allFiles = DriveApp.getFilesByName(CONFIG.CSV_FILENAME);
    if (allFiles.hasNext()) {
      file = allFiles.next();
      Logger.log("在全域 Drive 中找到 CSV");
    }
  }
  
  if (!file) {
    Logger.log("找不到 CSV 檔案: " + CONFIG.CSV_FILENAME);
    return null;
  }
  
  Logger.log("讀取檔案: " + file.getName() + " (" + file.getSize() + " bytes)");
  return file.getBlob().getDataAsString("UTF-8");
}

// ==================== CSV 解析 ====================

/**
 * 解析 CSV 字串為二維陣列
 * 支援含逗號的引號欄位與中文內容
 */
function parseCSV_(csvString) {
  const lines = csvString.split(/\r?\n/);
  const result = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === "") {
      // 保留空行（作為區塊分隔）
      result.push([""]);
      continue;
    }
    
    const row = [];
    let current = "";
    let inQuotes = false;
    
    for (let j = 0; j < line.length; j++) {
      const ch = line[j];
      if (inQuotes) {
        if (ch === '"' && (j + 1 >= line.length || line[j + 1] !== '"')) {
          inQuotes = false;
        } else if (ch === '"' && line[j + 1] === '"') {
          current += '"';
          j++; // 跳過轉義的引號
        } else {
          current += ch;
        }
      } else {
        if (ch === '"') {
          inQuotes = true;
        } else if (ch === ',') {
          row.push(current.trim());
          current = "";
        } else {
          current += ch;
        }
      }
    }
    row.push(current.trim());
    result.push(row);
  }
  
  // 移除尾部空行
  while (result.length > 0 && 
         result[result.length - 1].length === 1 && 
         result[result.length - 1][0] === "") {
    result.pop();
  }
  
  return result;
}

// ==================== 格式美化 ====================

/**
 * 套用區塊標題與表頭的格式
 */
function applyFormatting_(sheet, data) {
  const maxCols = data[0] ? data[0].length : 1;
  
  // 定義區塊標題（這些行會加粗加底色）
  const sectionHeaders = ["行程表", "景點資訊", "餐廳與咖啡廳資訊", "其他實用資訊"];
  
  for (let i = 0; i < data.length; i++) {
    const firstCell = data[i][0] || "";
    
    // 區塊大標題：深藍底白字
    if (sectionHeaders.includes(firstCell)) {
      const range = sheet.getRange(i + 1, 1, 1, maxCols);
      range.setBackground("#1a73e8")
           .setFontColor("#ffffff")
           .setFontWeight("bold")
           .setFontSize(12);
    }
    
    // 表頭行（日期/景點名稱/店名/項目）：淺灰底加粗
    if (["日期", "景點名稱", "店名", "項目"].includes(firstCell)) {
      const range = sheet.getRange(i + 1, 1, 1, maxCols);
      range.setBackground("#e8eaed")
           .setFontWeight("bold")
           .setFontSize(10);
    }
  }
  
  // 自動調整欄寬
  for (let col = 1; col <= maxCols; col++) {
    sheet.autoResizeColumn(col);
  }
  
  // 凍結第一行
  sheet.setFrozenRows(0);
  
  Logger.log("格式套用完成");
}

// ==================== 選單整合 ====================

/**
 * 在 Sheets 開啟時自動加入自訂選單
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("旅行助手")
    .addItem("匯入行程 CSV", "importTripData")
    .addItem("重新整理格式", "refreshFormatting")
    .addToUi();
}

/**
 * 重新套用格式（不重新匯入資料）
 */
function refreshFormatting() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {
    SpreadsheetApp.getUi().alert("找不到工作表: " + CONFIG.SHEET_NAME);
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  applyFormatting_(sheet, data);
  
  SpreadsheetApp.getUi().alert("格式已重新套用");
}

// ==================== 自動化觸發器 ====================

/**
 * 自動設定「每小時」執行一次 importTripData 的觸發器
 */
function setupTrigger() {
  // 先清除舊的相同觸發器，避免重複
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "importTripData") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  
  // 建立新的每小時觸發器
  ScriptApp.newTrigger("importTripData")
    .timeBased()
    .everyHours(1)
    .create();
    
  SpreadsheetApp.getUi().alert("自動同步已啟動", "已成功設定每小時自動從 Drive 匯入資料一次。", SpreadsheetApp.getUi().ButtonSet.OK);
}
