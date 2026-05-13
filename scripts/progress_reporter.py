#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress Reporter Module
Auto-reports progress every 10 seconds for long-running tasks
"""

import sys
import time
from typing import Optional

class ProgressReporter:
    """10-second interval progress reporter"""

    def __init__(self, total: int, name: str = ""):
        self.total = total
        self.name = name
        self.current = 0
        self.start_time = time.time()
        self.last_report = self.start_time
        self.stats = {}

    def update(self, increment: int = 1, **kwargs) -> Optional[str]:
        """Update progress, auto-report every 10 seconds

        Args:
            increment: amount to increment (default 1)
            **kwargs: additional stats (e.g. success=100, failed=5)

        Returns:
            Report string if reported, otherwise None
        """
        self.current += increment
        self.stats.update(kwargs)

        current_time = time.time()
        if current_time - self.last_report >= 10:
            report = self.get_report()
            print(report)
            sys.stdout.flush()
            self.last_report = current_time
            return report

        return None

    def get_report(self) -> str:
        """Generate progress report text"""
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0
        remaining = (self.total - self.current) / rate if rate > 0 else 0
        percentage = (self.current / self.total * 100) if self.total > 0 else 0

        stats_str = " ".join([f"{k}{v:4d}" for k, v in self.stats.items()])
        stats_part = f" | {stats_str}" if stats_str else ""

        return (f"[TIME] [{elapsed:6.1f}s] Progress: {self.current:5d}/{self.total} ({percentage:5.1f}%){stats_part} | "
                f"ETA: {remaining:.0f}s")

    def finish(self):
        """Finish and output final statistics"""
        elapsed = time.time() - self.start_time
        print(f"\n{'=' * 60}")
        print(f"[OK] {self.name or 'Task'} completed")
        print(f"[OK] Processed: {self.current} / {self.total}")
        print(f"[OK] Elapsed: {elapsed:.1f}s")
        if self.stats:
            for k, v in self.stats.items():
                print(f"[OK] {k}: {v}")
        print(f"{'=' * 60}")
