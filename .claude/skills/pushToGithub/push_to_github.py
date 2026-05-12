#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Push Skill
Skill: /pushToGithub

用法：
  python push_to_github.py          # 交互模式，引導推送過程
  python push_to_github.py mode=auto   # 自動模式，自動添加和推送
  python push_to_github.py mode=check  # 檢查模式，只顯示狀態
"""

import os
import sys
import io
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# 修復 Windows 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置
REPO_ROOT = Path(__file__).parent.parent.parent.parent
GITHUB_URL = "https://github.com/ZacharyYangTW/llm-wiki-travel.git"
REMOTE_NAME = "origin"

def run_command(cmd: List[str], cwd=None) -> Tuple[bool, str]:
    """執行 shell 命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_git_status() -> dict:
    """檢查 git 狀態"""
    success, output = run_command(["git", "status", "--porcelain"])

    if not success:
        return {"error": "無法執行 git status"}

    staged = []
    unstaged = []
    untracked = []

    for line in output.strip().split('\n'):
        if not line:
            continue
        status = line[:2]
        file = line[3:]

        if status[0] != ' ':
            staged.append(file)
        if status[1] != ' ':
            unstaged.append(file)
        if status == '??':
            untracked.append(file)

    return {
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "has_changes": bool(staged or unstaged or untracked)
    }

def get_remote_status() -> dict:
    """檢查遠程狀態"""
    # 檢查是否已設定 remote
    success, output = run_command(["git", "remote", "-v"])

    if not success or REMOTE_NAME not in output:
        return {
            "remote_exists": False,
            "needs_setup": True
        }

    return {
        "remote_exists": True,
        "needs_setup": False
    }

def setup_remote() -> bool:
    """設定 GitHub remote"""
    print("🔧 設定 GitHub remote...")

    # 檢查是否已存在
    success, output = run_command(["git", "remote", "-v"])
    if success and REMOTE_NAME in output:
        print(f"✓ Remote '{REMOTE_NAME}' 已存在")
        return True

    # 添加 remote
    success, output = run_command(["git", "remote", "add", REMOTE_NAME, GITHUB_URL])
    if success:
        print(f"✓ 已添加 remote: {GITHUB_URL}")
        return True
    else:
        print(f"❌ 添加 remote 失敗: {output}")
        return False

def add_files(files: List[str]) -> bool:
    """添加檔案到 staging area"""
    if not files:
        print("⚠️  沒有檔案要添加")
        return True

    print(f"📝 添加 {len(files)} 個檔案...")
    cmd = ["git", "add"] + files
    success, output = run_command(cmd)

    if success:
        print(f"✓ 已添加 {len(files)} 個檔案")
        return True
    else:
        print(f"❌ 添加檔案失敗: {output}")
        return False

def create_commit(message: str) -> bool:
    """建立 commit"""
    print(f"💾 建立 commit...")

    cmd = ["git", "commit", "-m", message]
    success, output = run_command(cmd)

    if success:
        print(f"✓ Commit 已建立")
        return True
    else:
        print(f"❌ Commit 失敗: {output}")
        return False

def push_to_github() -> bool:
    """推送到 GitHub"""
    print("🚀 推送到 GitHub...")

    # 先 fetch 以同步遠程信息
    print("  同步遠程信息...")
    run_command(["git", "fetch", REMOTE_NAME])

    # 推送
    success, output = run_command(["git", "push", "-u", REMOTE_NAME, "HEAD"])

    if success:
        print(f"✓ 已推送到 GitHub")
        return True
    else:
        print(f"❌ 推送失敗: {output}")
        return False

def interactive_mode():
    """交互模式"""
    print("=" * 60)
    print("🌐 GitHub Push 工具 - 交互模式")
    print("=" * 60)

    # 檢查狀態
    print("\n1️⃣  檢查 git 狀態...")
    status = check_git_status()

    if status.get("error"):
        print(f"❌ {status['error']}")
        return False

    print(f"  已暫存: {len(status['staged'])} 個")
    print(f"  未暫存: {len(status['unstaged'])} 個")
    print(f"  未追蹤: {len(status['untracked'])} 個")

    # 如果沒有變更，詢問是否要添加
    if not status['has_changes']:
        print("\n⚠️  沒有變更")
        response = input("是否要添加 wiki/ 和 twgeojson/ ? (y/n): ")
        if response.lower() == 'y':
            if not add_files(["wiki/", "twgeojson/"]):
                return False
        else:
            print("取消")
            return False
    else:
        print("\n2️⃣  已檢測到變更")

        # 詢問是否添加未暫存的
        if status['unstaged'] or status['untracked']:
            response = input("是否要添加所有變更? (y/n): ")
            if response.lower() == 'y':
                to_add = status['unstaged'] + status['untracked']
                if not add_files(to_add):
                    return False

    # 檢查 remote
    print("\n3️⃣  檢查 GitHub remote...")
    remote_status = get_remote_status()

    if remote_status['needs_setup']:
        if not setup_remote():
            return False
    else:
        print("✓ Remote 已設定")

    # 詢問 commit message
    print("\n4️⃣  準備 commit...")
    default_msg = f"Update wiki and GeoJSON - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg = input(f"Commit message [{default_msg}]: ").strip()
    if not msg:
        msg = default_msg

    if not create_commit(msg):
        return False

    # 推送
    print("\n5️⃣  推送到 GitHub...")
    if not push_to_github():
        return False

    print("\n" + "=" * 60)
    print("✅ 推送完成！")
    print("=" * 60)
    return True

def auto_mode():
    """自動模式"""
    print("=" * 60)
    print("🌐 GitHub Push 工具 - 自動模式")
    print("=" * 60)

    # 檢查狀態
    print("\n檢查 git 狀態...")
    status = check_git_status()

    if status.get("error"):
        print(f"❌ {status['error']}")
        return False

    if not status['has_changes']:
        print("⚠️  沒有變更，跳過")
        return True

    # 添加變更
    files = status['unstaged'] + status['untracked']
    print(f"添加 {len(files)} 個檔案...")
    if not add_files(files):
        return False

    # 設定 remote
    remote_status = get_remote_status()
    if remote_status['needs_setup']:
        if not setup_remote():
            return False

    # 自動 commit
    msg = f"Auto update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print(f"建立 commit: {msg}")
    if not create_commit(msg):
        return False

    # 推送
    print("推送到 GitHub...")
    if not push_to_github():
        return False

    print("\n✅ 推送完成！")
    return True

def check_mode():
    """檢查模式"""
    print("=" * 60)
    print("🌐 GitHub Push 工具 - 檢查模式")
    print("=" * 60)

    print("\n檢查 git 狀態...")
    status = check_git_status()

    if status.get("error"):
        print(f"❌ {status['error']}")
        return False

    print(f"\n已暫存: {len(status['staged'])} 個檔案")
    for f in status['staged'][:5]:
        print(f"  {f}")
    if len(status['staged']) > 5:
        print(f"  ... 等 {len(status['staged']) - 5} 個")

    print(f"\n未暫存: {len(status['unstaged'])} 個檔案")
    for f in status['unstaged'][:5]:
        print(f"  {f}")
    if len(status['unstaged']) > 5:
        print(f"  ... 等 {len(status['unstaged']) - 5} 個")

    print(f"\n未追蹤: {len(status['untracked'])} 個檔案")
    for f in status['untracked'][:5]:
        print(f"  {f}")
    if len(status['untracked']) > 5:
        print(f"  ... 等 {len(status['untracked']) - 5} 個")

    print(f"\n遠程狀態: ", end="")
    remote_status = get_remote_status()
    if remote_status['needs_setup']:
        print("❌ 未設定")
    else:
        print("✓ 已設定")

    return True

def main():
    # 解析命令行參數
    mode = "interactive"
    for arg in sys.argv[1:]:
        if arg.startswith("mode="):
            mode = arg.split("=")[1]

    if mode == "auto":
        auto_mode()
    elif mode == "check":
        check_mode()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
