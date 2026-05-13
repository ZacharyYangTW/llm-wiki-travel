#!/usr/bin/env python3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

print("===== 開始測試 =====", flush=True)
print(f"Python 版本: {sys.version}", flush=True)
print(f"工作目錄: {os.getcwd()}", flush=True)

CSV_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\unknown_files_all.csv"
print(f"CSV 檔案: {CSV_FILE}", flush=True)
print(f"CSV 存在: {os.path.exists(CSV_FILE)}", flush=True)

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"CSV 行數: {len(lines)}", flush=True)

print("===== 測試完成 =====", flush=True)
