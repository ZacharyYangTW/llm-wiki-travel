# Classify Unknown Locations - Reusable Script
# 用法: .\classify_unknown_batch.ps1 -CsvPath "path\to\success.csv"

param(
    [string]$CsvPath = "h:\我的雲端硬碟\llm_wiki_travel\batch2_success.csv"
)

Write-Host "================== 重新分類未知位置 =================="
Write-Host "CSV 檔案: $CsvPath"
Write-Host ""

# 檢查 CSV 是否存在
if (-not (Test-Path $CsvPath)) {
    Write-Host "❌ CSV 檔案未找到: $CsvPath"
    exit 1
}

# 讀取座標映射
$csv = Import-Csv -Path $CsvPath -Encoding UTF8
$coordsMap = @{}

foreach ($row in $csv) {
    $lng = $row.Longitude.Trim()
    $lat = $row.Latitude.Trim()
    $city = $row.City.Trim()
    $country = $row.Country.Trim()

    $key = "$lng,$lat"
    $coordsMap[$key] = @{
        city = $city
        country = $country
    }
}

Write-Host "✅ 已讀取 $($coordsMap.Count) 個座標映射"
Write-Host ""

if ($coordsMap.Count -eq 0) {
    Write-Host "❌ 座標映射表為空，終止"
    exit 1
}

# 國家名稱標準化對應表
$countryNameMap = @{
    "China" = "中國"
    "Taiwan" = "台灣"
    "Japan" = "日本"
    "Thailand" = "泰國"
    "Vietnam" = "越南"
    "Cambodia" = "柬埔寨"
    "Malaysia" = "馬來西亞"
    "Singapore" = "新加坡"
    "United States" = "美國"
    "Canada" = "加拿大"
    "Hong Kong" = "香港"
    "Macao" = "澳門"
    "South Korea" = "韓國"
    "India" = "印度"
    "Egypt" = "埃及"
    "Netherlands" = "荷蘭"
    "New Zealand" = "紐西蘭"
}

# 掃描並重新分類
$unknownPath = "h:\我的雲端硬碟\llm_wiki_travel\wiki\未知\未分類"
$otherPath = "h:\我的雲端硬碟\llm_wiki_travel\wiki\其他"
$wikiPath = "h:\我的雲端硬碟\llm_wiki_travel\wiki"

$movedCount = 0
$notFoundCount = 0
$failedCount = 0
$processCount = 0

Write-Host "🔍 掃描 wiki/未知/未分類..."

Get-ChildItem -Path $unknownPath -File -Filter "*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    $file = $_
    $processCount++

    if ($processCount % 500 -eq 0) {
        Write-Host "  進度: $processCount"
    }

    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8

        # 提取座標
        if ($content -match 'coordinates:\s*\[([^,]+),\s*([^\]]+)\]') {
            $lng = $matches[1].Trim()
            $lat = $matches[2].Trim()
            $coordKey = "$lng,$lat"

            if ($coordsMap.ContainsKey($coordKey)) {
                $mapping = $coordsMap[$coordKey]
                $newCountry = $mapping.country
                $newCity = $mapping.city

                # 標準化國家名稱
                if ($countryNameMap.ContainsKey($newCountry)) {
                    $newCountry = $countryNameMap[$newCountry]
                }

                # 建立新目錄
                $newDir = "$wikiPath\$newCountry\$newCity"
                if (-not (Test-Path $newDir)) {
                    New-Item -ItemType Directory -Path $newDir -Force | Out-Null
                }

                # 移動檔案
                $newPath = "$newDir\$($file.Name)"
                if ((Test-Path $newDir) -and ($newPath -ne $file.FullName)) {
                    Move-Item -Path $file.FullName -Destination $newPath -Force
                    $movedCount++
                } else {
                    $failedCount++
                }
            } else {
                $notFoundCount++
            }
        }
    } catch {
        $failedCount++
    }
}

Write-Host "  ✅ 完成 ($processCount 個檔案)"
Write-Host ""

# 掃描 wiki/其他
Write-Host "🔍 掃描 wiki/其他..."
$otherProcessCount = 0
$otherMovedCount = 0

Get-ChildItem -Path $otherPath -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    $file = $_
    $otherProcessCount++

    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8

        if ($content -match 'coordinates:\s*\[([^,]+),\s*([^\]]+)\]') {
            $lng = $matches[1].Trim()
            $lat = $matches[2].Trim()
            $coordKey = "$lng,$lat"

            if ($coordsMap.ContainsKey($coordKey)) {
                $mapping = $coordsMap[$coordKey]
                $newCountry = $mapping.country
                $newCity = $mapping.city

                if ($countryNameMap.ContainsKey($newCountry)) {
                    $newCountry = $countryNameMap[$newCountry]
                }

                $newDir = "$wikiPath\$newCountry\$newCity"
                if (-not (Test-Path $newDir)) {
                    New-Item -ItemType Directory -Path $newDir -Force | Out-Null
                }

                $newPath = "$newDir\$($file.Name)"
                if ((Test-Path $newDir) -and ($newPath -ne $file.FullName)) {
                    Move-Item -Path $file.FullName -Destination $newPath -Force
                    $otherMovedCount++
                    $movedCount++
                } else {
                    $failedCount++
                }
            } else {
                $notFoundCount++
            }
        }
    } catch {
        $failedCount++
    }
}

Write-Host "  ✅ 完成 ($otherProcessCount 個檔案，移動 $otherMovedCount 個)"
Write-Host ""

# 統計
Write-Host "=================================================="
Write-Host "✅ 已移動: $movedCount"
Write-Host "⚠️ 座標未找到: $notFoundCount"
Write-Host "❌ 失敗: $failedCount"
Write-Host "📊 總計: $($processCount + $otherProcessCount)"
Write-Host "=================================================="
