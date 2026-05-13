#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 ProgressReporter - 確認 10 秒回報是否正常
"""

import sys
import time
from progress_reporter import ProgressReporter

# 模擬 100 個任務，每個任務 0.1 秒
print("開始測試 ProgressReporter...")
print("=" * 60)

reporter = ProgressReporter(total=100, name="測試任務")

for i in range(100):
    time.sleep(0.1)  # 每個任務 0.1 秒，總共 ~10 秒
    reporter.update(success=1)

reporter.finish()
print("\n測試完成！應該看到大約 1 次 10 秒回報")
