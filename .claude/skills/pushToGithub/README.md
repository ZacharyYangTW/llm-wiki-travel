# pushToGithub Skill

自動化推送項目變更到 GitHub

## 配置

- **GitHub URL**: `https://github.com/ZacharyYangTW/llm-wiki-travel.git`
- **Remote**: `origin`

## 用法

### 交互模式（預設）
```bash
python push_to_github.py
```
引導你完整地進行推送流程：
1. 檢查 git 狀態
2. 選擇要添加的檔案
3. 設定 GitHub remote（如果需要）
4. 輸入 commit message
5. 推送到 GitHub

### 自動模式
```bash
python push_to_github.py mode=auto
```
自動添加所有變更、創建 commit 並推送

### 檢查模式
```bash
python push_to_github.py mode=check
```
只顯示 git 狀態，不進行任何操作

## 功能

- ✅ 檢查 git 狀態（已暫存、未暫存、未追蹤）
- ✅ 自動設定 GitHub remote
- ✅ 添加檔案到 staging area
- ✅ 建立 commit
- ✅ 推送到 GitHub

## 示例

### 推送 wiki 和 GeoJSON 變更
```bash
# 交互模式，詢問確認
python push_to_github.py

# 自動模式，直接推送
python push_to_github.py mode=auto
```

### 檢查狀態
```bash
python push_to_github.py mode=check
```
