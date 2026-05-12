#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 Wiki 目錄中的重複檔案

使用方式：
  python find_duplicates.py [wiki_path]

輸出：
  - 重複檔名清單
  - 每個重複檔名的位置
  - 統計資訊
"""

import os
import sys
import json
from collections import defaultdict
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    wiki_path = sys.argv[1] if len(sys.argv) > 1 else 'wiki'
    
    if not os.path.isdir(wiki_path):
        print(f"❌ 目錄不存在: {wiki_path}")
        sys.exit(1)
    
    print("=" * 100)
    print("檢查重複檔案".center(100))
    print("=" * 100)
    print()
    
    # 掃描檔案
    duplicates = defaultdict(list)
    total_files = 0
    
    for md_file in Path(wiki_path).rglob('*.md'):
        title = md_file.stem
        rel_path = str(md_file.relative_to(wiki_path)).replace(chr(92), '/')
        duplicates[title].append(rel_path)
        total_files += 1
    
    # 找重複
    real_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    print(f"總檔案數: {total_files}")
    print(f"重複檔名: {len(real_duplicates)}")
    print(f"涉及檔案: {sum(len(v) for v in real_duplicates.values())}")
    print()
    
    if len(real_duplicates) == 0:
        print("✅ 沒有發現重複檔名！")
        return
    
    # 按重複數量排序
    sorted_dups = sorted(real_duplicates.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"{'#':<4} {'檔名':<50} {'位置數':<10} {'位置':<100}")
    print("-" * 100)
    
    for idx, (filename, paths) in enumerate(sorted_dups[:50], 1):
        locations = " | ".join(paths)
        if len(locations) > 100:
            locations = locations[:97] + "..."
        print(f"{idx:<4} {filename:<50} {len(paths):<10} {locations:<100}")
    
    if len(real_duplicates) > 50:
        print(f"\n... 還有 {len(real_duplicates) - 50} 個重複檔名未顯示")
    
    # 保存詳細報告
    report = {
        'timestamp': str(Path(wiki_path).stat().st_mtime),
        'summary': {
            'total_files': total_files,
            'duplicate_filenames': len(real_duplicates),
            'affected_files': sum(len(v) for v in real_duplicates.values())
        },
        'duplicates': {k: v for k, v in list(real_duplicates.items())[:100]}
    }
    
    with open('duplicate_check_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 詳細報告已保存到 duplicate_check_report.json")

if __name__ == '__main__':
    main()
