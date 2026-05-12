#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki 完全標準化：簡繁體、一字之差、日本繁體字、相似目錄、散落檔案分類
"""

import os
import sys
import shutil
import difflib
import re
import math
from collections import defaultdict
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"

# 導入日本市町村座標表
from japan_towns_coords import JAPAN_TOWNS_COORDS, get_nearest_town

# 簡體字→繁體字映射（詞組級別）
SIMPLIFIED_CITIES = {
    "兰州": "蘭州",
    "兰州市": "蘭州市",
    "苏州": "蘇州",
    "苏州市": "蘇州市",
    "贵阳": "貴陽",
    "贵阳市": "貴陽市",
    "云浮": "雲浮",
    "云浮市": "雲浮市",
    "武汉": "武漢",
    "武汉市": "武漢市",
    "宁夏": "寧夏",
    "宁波": "寧波",
    "肃州": "肅州",
    "陕西": "陝西",
    "陕西省": "陝西省",
    "辽宁": "遼寧",
    "辽宁省": "遼寧省",
}

# 日本繁體字→日文漢字映射
JAPAN_TRADITIONAL_MAP = {
    "神奈川縣": "神奈川県",
    "福岡縣": "福岡県",
    "長崎縣": "長崎県",
    "佐賀縣": "佐賀県",
    "青森縣": "青森県",
}

# 一字之差後綴
SUFFIXES = ['市', '縣', '區', '州', '府']

# 相似目錄檢測（高度相似的目錄應統一）
# 格式: (國家, 簡短版本) -> 完整版本
# 或: (國家,) -> 新國家名 (用於重命名國家目錄)
SIMILAR_DIRS_MAP = {
    ("韓國", "大邱"): "大邱廣域市",
    ("韓國", "首爾"): "首爾特別市",
    ("韓國", "仁川"): "仁川廣域市",
    ("韓國", "光州"): "光州廣域市",
    ("韓國", "大田"): "大田廣域市",
}

# 國家層級重命名（將舊名稱改為新名稱）
COUNTRY_RENAMES = {
    "南韓": "韓國",
}

# 第一級標準目錄（用於檢測違規目錄）
STANDARD_FIRST_LEVEL = {
    "台灣": [
        "台北市", "新北市", "基隆市", "桃園市",
        "新竹市", "新竹縣", "苗栗縣", "台中市",
        "彰化縣", "南投縣", "雲林縣", "嘉義市",
        "嘉義縣", "台南市", "高雄市", "屏東縣",
        "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣",
        "金門縣", "連江縣"
    ]
}

# 誤放檔案對應表：(國家, 誤放的目錄) -> (目標國家, 目標目錄)
MISPLACED_DIRS = {
    ("台灣", "沖繩縣豐見城市"): ("日本", "沖縄県"),
}

# 應該合併到另一個國家子目錄的國家目錄：(國家) -> (目標國家, 子目錄)
COUNTRY_MERGE_TO_SUBDIR = {
    "澳門": ("中國", "澳門"),
    "香港": ("中國", "香港"),
}

# 應該移到子目錄的一級目錄（格式：(國家, 錯誤目錄) -> (應該在的父目錄)）
DIRS_TO_MOVE_TO_SUBDIR = {
    ("台灣", "台北市內湖區"): "台北市",
    ("台灣", "新北市三芝區"): "新北市",
    ("台灣", "新北市石門區"): "新北市",
    ("台灣", "新北市新店區"): "新北市",
    ("澳洲", "雪梨港灣"): "雪梨",
}

# 重複目錄檢測（格式：(國家, 父級目錄, 子級目錄名) -> 應刪除）
# 用於檢測如 日本/青森県/青森県 這類重複結構
DUPLICATE_DIRS = {
    ("日本", "青森県", "青森県"),
}

# 日本二級目錄的繁體字→日文漢字映射（區→区、戶→戸等）
JAPAN_LEVEL2_FIXES = {
    "神戶市": "神戸市",  # 戶→戸
    "新宮市": "新宮市",  # 保留（已是正確的）
}

# 各國一級目錄是否需要檢查散落檔案
COUNTRIES_WITH_SCATTERED_CHECK = [
    "日本",
    "中國",
    "台灣",
]

def check_simplified_and_convert(name):
    """檢查是否包含簡體字並返回繁體版本"""
    for simplified, traditional in SIMPLIFIED_CITIES.items():
        if simplified in name:
            return name.replace(simplified, traditional)
    return None

def check_japan_level2_and_convert(name):
    """檢查日本二級目錄是否需要日文漢字修正"""
    if name in JAPAN_LEVEL2_FIXES:
        return JAPAN_LEVEL2_FIXES[name]

    # 檢查是否包含繁體字（區、戶等）
    if "區" in name:
        return name.replace("區", "区")
    if "戶" in name:
        return name.replace("戶", "戸")
    if "縣" in name:
        return name.replace("縣", "県")

    return None

def extract_coordinates(file_path):
    """從檔案的 frontmatter 提取座標"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'coordinates:\s*\[([^,]+),\s*([^\]]+)\]', content)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))
                return (lng, lat)
    except:
        pass
    return None

def find_all_issues():
    """掃描並找出所有命名問題"""
    issues = {
        'simplified': [],
        'single_char': [],
        'similar': [],
        'japan_traditional': [],
        'japan_level2_fixes': [],
        'country_renames': [],
        'illegal_first_level': [],
        'misplaced_dirs': [],
        'move_to_subdir': [],
        'country_merge_to_subdir': [],
        'duplicate_dirs': [],
        'scattered_files': [],
    }

    # 檢查國家層級重命名
    for old_country, new_country in COUNTRY_RENAMES.items():
        old_path = os.path.join(WIKI_BASE, old_country)
        new_path = os.path.join(WIKI_BASE, new_country)
        if os.path.isdir(old_path):
            try:
                old_files = len([f for f in os.listdir(old_path)
                               if f.endswith('.md') and os.path.isfile(os.path.join(old_path, f))])
                old_subdirs = len([d for d in os.listdir(old_path)
                                 if os.path.isdir(os.path.join(old_path, d))])
                if old_files > 0 or old_subdirs > 0:
                    issues['country_renames'].append({
                        'old_country': old_country,
                        'new_country': new_country,
                        'files': old_files,
                        'subdirs': old_subdirs,
                        'old_path': old_path,
                        'new_path': new_path
                    })
            except:
                pass

    # 檢查應該合併到另一國家子目錄的國家目錄
    for src_country, (tgt_country, tgt_subdir) in COUNTRY_MERGE_TO_SUBDIR.items():
        src_path = os.path.join(WIKI_BASE, src_country)
        if os.path.isdir(src_path):
            try:
                files = len([f for f in os.listdir(src_path)
                           if f.endswith('.md') and os.path.isfile(os.path.join(src_path, f))])
                subdirs = len([d for d in os.listdir(src_path)
                             if os.path.isdir(os.path.join(src_path, d))])
                if files > 0 or subdirs > 0:
                    tgt_path = os.path.join(WIKI_BASE, tgt_country, tgt_subdir)
                    issues['country_merge_to_subdir'].append({
                        'src_country': src_country,
                        'tgt_country': tgt_country,
                        'tgt_subdir': tgt_subdir,
                        'src_path': src_path,
                        'tgt_path': tgt_path,
                        'files': files,
                        'subdirs': subdirs,
                        'tgt_exists': os.path.isdir(tgt_path)
                    })
            except:
                pass

    # 檢查誤放的目錄
    for (src_country, src_dir), (tgt_country, tgt_dir) in MISPLACED_DIRS.items():
        src_path = os.path.join(WIKI_BASE, src_country, src_dir)
        if os.path.isdir(src_path):
            try:
                files = len([f for f in os.listdir(src_path)
                           if f.endswith('.md') and os.path.isfile(os.path.join(src_path, f))])
                subdirs = len([d for d in os.listdir(src_path)
                             if os.path.isdir(os.path.join(src_path, d))])
                # 即使是空目錄也列出來
                issues['misplaced_dirs'].append({
                    'src_country': src_country,
                    'src_dir': src_dir,
                    'tgt_country': tgt_country,
                    'tgt_dir': tgt_dir,
                    'src_path': src_path,
                    'tgt_path': os.path.join(WIKI_BASE, tgt_country, tgt_dir),
                    'files': files,
                    'subdirs': subdirs,
                    'is_empty': files == 0 and subdirs == 0
                })
            except:
                pass

    # 檢查應該移到子目錄的目錄
    for (country, wrong_dir), parent_dir in DIRS_TO_MOVE_TO_SUBDIR.items():
        wrong_path = os.path.join(WIKI_BASE, country, wrong_dir)
        if os.path.isdir(wrong_path):
            try:
                files = len([f for f in os.listdir(wrong_path)
                           if f.endswith('.md') and os.path.isfile(os.path.join(wrong_path, f))])
                subdirs = len([d for d in os.listdir(wrong_path)
                             if os.path.isdir(os.path.join(wrong_path, d))])
                # 即使是空目錄也列出來（files == 0 and subdirs == 0）
                target_path = os.path.join(WIKI_BASE, country, parent_dir, wrong_dir)
                issues['move_to_subdir'].append({
                    'country': country,
                    'wrong_dir': wrong_dir,
                    'parent_dir': parent_dir,
                    'wrong_path': wrong_path,
                    'target_path': target_path,
                    'files': files,
                    'subdirs': subdirs,
                    'is_empty': files == 0 and subdirs == 0
                })
            except:
                pass

    for country in sorted(os.listdir(WIKI_BASE)):
        country_path = os.path.join(WIKI_BASE, country)
        if not os.path.isdir(country_path):
            continue

        # 一級目錄
        level1_dirs = [d for d in os.listdir(country_path)
                      if os.path.isdir(os.path.join(country_path, d))]

        # 檢查台灣的一級目錄是否符合規定
        if country == "台灣" and country in STANDARD_FIRST_LEVEL:
            standard = STANDARD_FIRST_LEVEL[country]
            for dir_name in level1_dirs:
                if dir_name not in standard:
                    # 跳過已在 move_to_subdir 或 misplaced_dirs 中的
                    is_already_handled = any(
                        (country, dir_name) == item[0]
                        for item in list(DIRS_TO_MOVE_TO_SUBDIR.keys()) +
                                   list(MISPLACED_DIRS.keys())
                    )
                    if not is_already_handled:
                        try:
                            files = len([f for f in os.listdir(os.path.join(country_path, dir_name))
                                       if f.endswith('.md') and os.path.isfile(os.path.join(country_path, dir_name, f))])
                            if files > 0:
                                issues['illegal_first_level'].append({
                                    'country': country,
                                    'dir_name': dir_name,
                                    'path': os.path.join(country_path, dir_name),
                                    'files': files
                                })
                        except:
                            pass

        # 檢查簡體字（一級）
        for dir_name in level1_dirs:
            traditional = check_simplified_and_convert(dir_name)
            if traditional:
                issues['simplified'].append({
                    'country': country,
                    'current': dir_name,
                    'target': traditional,
                    'level': 1,
                    'path': country_path
                })

        # 檢查相似目錄（一級）
        for key, target in SIMILAR_DIRS_MAP.items():
            if key[0] == country:  # 檢查國家是否匹配
                short_name = key[1]
                if short_name in level1_dirs and target in level1_dirs:
                    short_path = os.path.join(country_path, short_name)
                    target_path = os.path.join(country_path, target)
                    try:
                        short_files = len([f for f in os.listdir(short_path)
                                         if f.endswith('.md') and os.path.isfile(os.path.join(short_path, f))])
                        target_files = len([f for f in os.listdir(target_path)
                                          if f.endswith('.md') and os.path.isfile(os.path.join(target_path, f))])
                        if short_files > 0 or target_files > 0:
                            issues['similar'].append({
                                'country': country,
                                'short': short_name,
                                'long': target,
                                'short_files': short_files,
                                'long_files': target_files,
                                'level': 1,
                                'short_path': short_path,
                                'long_path': target_path
                            })
                    except:
                        pass

        # 檢查一字之差（一級）
        for i, dir1 in enumerate(level1_dirs):
            for dir2 in level1_dirs[i+1:]:
                if abs(len(dir1) - len(dir2)) <= 1:
                    for suffix in SUFFIXES:
                        if dir1 == dir2 + suffix or dir2 == dir1 + suffix:
                            short = dir1 if len(dir1) < len(dir2) else dir2
                            long = dir2 if len(dir1) < len(dir2) else dir1

                            short_path = os.path.join(country_path, short)
                            long_path = os.path.join(country_path, long)

                            try:
                                short_files = len([f for f in os.listdir(short_path)
                                                 if f.endswith('.md') and os.path.isfile(os.path.join(short_path, f))])
                                long_files = len([f for f in os.listdir(long_path)
                                                if f.endswith('.md') and os.path.isfile(os.path.join(long_path, f))])

                                if short_files > 0 or long_files > 0:
                                    issues['single_char'].append({
                                        'country': country,
                                        'short': short,
                                        'long': long,
                                        'short_files': short_files,
                                        'long_files': long_files,
                                        'level': 1,
                                        'short_path': short_path,
                                        'long_path': long_path
                                    })
                            except:
                                pass

        # 掃描二級目錄
        for level1 in level1_dirs:
            level1_path = os.path.join(country_path, level1)
            try:
                level2_dirs = [d for d in os.listdir(level1_path)
                              if os.path.isdir(os.path.join(level1_path, d))]
            except:
                continue

            # 檢查重複目錄（如青森県/青森県）
            for country_dup, parent_dup, child_dup in DUPLICATE_DIRS:
                if country == country_dup and level1 == parent_dup and child_dup in level2_dirs:
                    child_path = os.path.join(level1_path, child_dup)
                    try:
                        files = len([f for f in os.listdir(child_path)
                                   if f.endswith('.md') and os.path.isfile(os.path.join(child_path, f))])
                        subdirs = len([d for d in os.listdir(child_path)
                                     if os.path.isdir(os.path.join(child_path, d))])
                        if files > 0 or subdirs > 0:
                            issues['duplicate_dirs'].append({
                                'country': country,
                                'parent': level1,
                                'duplicate': child_dup,
                                'path': child_path,
                                'files': files,
                                'subdirs': subdirs
                            })
                    except:
                        pass

            # 檢查簡體字（二級）
            for dir_name in level2_dirs:
                traditional = check_simplified_and_convert(dir_name)
                if traditional:
                    issues['simplified'].append({
                        'country': country,
                        'parent': level1,
                        'current': dir_name,
                        'target': traditional,
                        'level': 2,
                        'path': level1_path
                    })

            # 檢查日本繁體字（日本二級）
            if country == "日本":
                for dir_name in level2_dirs:
                    if dir_name in JAPAN_TRADITIONAL_MAP:
                        target = JAPAN_TRADITIONAL_MAP[dir_name]
                        if target not in level2_dirs:
                            # 如果目標版本不存在，建議改名
                            issues['japan_traditional'].append({
                                'country': country,
                                'parent': level1,
                                'current': dir_name,
                                'target': target,
                                'level': 2,
                                'path': level1_path
                            })
                        else:
                            # 如果兩個版本都存在，應該合併
                            current_path = os.path.join(level1_path, dir_name)
                            target_path = os.path.join(level1_path, target)
                            try:
                                current_files = len([f for f in os.listdir(current_path)
                                                    if f.endswith('.md') and os.path.isfile(os.path.join(current_path, f))])
                                target_files = len([f for f in os.listdir(target_path)
                                                  if f.endswith('.md') and os.path.isfile(os.path.join(target_path, f))])
                                if current_files > 0 or target_files > 0:
                                    issues['japan_traditional'].append({
                                        'country': country,
                                        'parent': level1,
                                        'current': dir_name,
                                        'target': target,
                                        'level': 2,
                                        'path': level1_path,
                                        'current_files': current_files,
                                        'target_files': target_files,
                                        'current_path': current_path,
                                        'target_path': target_path
                                    })
                            except:
                                pass

            # 檢查日本二級目錄的日文漢字修正（區→区、戶→戸等）
            if country == "日本":
                for dir_name in level2_dirs:
                    fixed_name = check_japan_level2_and_convert(dir_name)
                    if fixed_name and fixed_name != dir_name:
                        fixed_path = os.path.join(level1_path, fixed_name)
                        if os.path.exists(fixed_path):
                            # 如果目標已存在，需要合併
                            try:
                                fixed_files = len([f for f in os.listdir(fixed_path)
                                                  if f.endswith('.md') and os.path.isfile(os.path.join(fixed_path, f))])
                                current_files = len([f for f in os.listdir(os.path.join(level1_path, dir_name))
                                                    if f.endswith('.md') and os.path.isfile(os.path.join(level1_path, dir_name, f))])
                                if fixed_files > 0 or current_files > 0:
                                    issues['japan_level2_fixes'].append({
                                        'country': country,
                                        'parent': level1,
                                        'current': dir_name,
                                        'target': fixed_name,
                                        'current_path': os.path.join(level1_path, dir_name),
                                        'target_path': fixed_path,
                                        'both_exist': True,
                                        'current_files': current_files,
                                        'target_files': fixed_files
                                    })
                            except:
                                pass
                        else:
                            # 只需要改名
                            try:
                                files = len([f for f in os.listdir(os.path.join(level1_path, dir_name))
                                           if f.endswith('.md') and os.path.isfile(os.path.join(level1_path, dir_name, f))])
                                subdirs = len([d for d in os.listdir(os.path.join(level1_path, dir_name))
                                            if os.path.isdir(os.path.join(level1_path, dir_name, d))])
                                if files > 0 or subdirs > 0:
                                    issues['japan_level2_fixes'].append({
                                        'country': country,
                                        'parent': level1,
                                        'current': dir_name,
                                        'target': fixed_name,
                                        'path': os.path.join(level1_path, dir_name),
                                        'both_exist': False,
                                        'files': files,
                                        'subdirs': subdirs
                                    })
                            except:
                                pass

            # 檢查一字之差（二級）
            for i, dir1 in enumerate(level2_dirs):
                for dir2 in level2_dirs[i+1:]:
                    if abs(len(dir1) - len(dir2)) <= 1:
                        for suffix in SUFFIXES:
                            if dir1 == dir2 + suffix or dir2 == dir1 + suffix:
                                short = dir1 if len(dir1) < len(dir2) else dir2
                                long = dir2 if len(dir1) < len(dir2) else dir1

                                short_path = os.path.join(level1_path, short)
                                long_path = os.path.join(level1_path, long)

                                try:
                                    short_files = len([f for f in os.listdir(short_path)
                                                     if f.endswith('.md') and os.path.isfile(os.path.join(short_path, f))])
                                    long_files = len([f for f in os.listdir(long_path)
                                                    if f.endswith('.md') and os.path.isfile(os.path.join(long_path, f))])

                                    if short_files > 0 or long_files > 0:
                                        issues['single_char'].append({
                                            'country': country,
                                            'parent': level1,
                                            'short': short,
                                            'long': long,
                                            'short_files': short_files,
                                            'long_files': long_files,
                                            'level': 2,
                                            'short_path': short_path,
                                            'long_path': long_path
                                        })
                                except:
                                    pass

    # 檢測散落檔案（日本各都道府縣下的直接 .md 檔案）
    japan_path = os.path.join(WIKI_BASE, "日本")
    if os.path.isdir(japan_path):
        try:
            scattered = []
            for pref_name in os.listdir(japan_path):
                pref_path = os.path.join(japan_path, pref_name)
                if not os.path.isdir(pref_path):
                    continue

                # 檢查這個都道府縣目錄下是否有直接的 .md 檔案（散落檔案）
                for file_name in os.listdir(pref_path):
                    file_path = os.path.join(pref_path, file_name)
                    if os.path.isfile(file_path) and file_name.endswith('.md'):
                        coords = extract_coordinates(file_path)
                        if coords and pref_name in JAPAN_TOWNS_COORDS:
                            # 根據座標找到最接近的市町村
                            nearest_town = get_nearest_town(coords, pref_name)
                            if nearest_town:
                                scattered.append({
                                    'file': file_name,
                                    'coords': coords,
                                    'target_country': "日本",
                                    'target_pref': pref_name,
                                    'target_city': nearest_town,
                                    'path': file_path
                                })

            if scattered:
                issues['scattered_files'].extend(scattered)
        except Exception as e:
            pass

    return issues

def apply_fixes(issues, auto_fix=False):
    """應用修正"""
    results = {
        'simplified_fixed': 0,
        'single_char_fixed': 0,
        'similar_fixed': 0,
        'japan_traditional_fixed': 0,
        'japan_level2_fixed': 0,
        'country_renames_fixed': 0,
        'misplaced_fixed': 0,
        'move_to_subdir_fixed': 0,
        'country_merge_fixed': 0,
        'duplicate_dirs_fixed': 0,
        'scattered_fixed': 0,
        'errors': []
    }

    # 修正國家目錄應合併到子目錄
    for issue in issues['country_merge_to_subdir']:
        src_path = issue['src_path']
        tgt_path = issue['tgt_path']

        if not os.path.exists(src_path):
            continue

        os.makedirs(tgt_path, exist_ok=True)

        try:
            for item in os.listdir(src_path):
                src = os.path.join(src_path, item)
                dst = os.path.join(tgt_path, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        # 合併子目錄（遞迴移動）
                        for sub_item in os.listdir(src):
                            sub_src = os.path.join(src, sub_item)
                            sub_dst = os.path.join(dst, sub_item)
                            if os.path.exists(sub_dst):
                                if os.path.isdir(sub_dst):
                                    shutil.rmtree(sub_dst)
                                else:
                                    os.remove(sub_dst)
                            shutil.move(sub_src, sub_dst)
                        os.rmdir(src)
                    else:
                        os.remove(dst)
                        shutil.move(src, dst)
                else:
                    shutil.move(src, dst)

            # 刪除空的源國家目錄
            try:
                os.rmdir(src_path)
            except:
                pass

            results['country_merge_fixed'] += 1
            print(f"✓ 國家合併: {issue['src_country']} → {issue['tgt_country']}/{issue['tgt_subdir']}", flush=True)
        except Exception as e:
            results['errors'].append(f"國家合併失敗: {issue['src_country']} - {str(e)}")
            print(f"❌ {issue['src_country']}: {str(e)}", flush=True)

    # 修正重複目錄（如青森県/青森県 → 青森県/...）
    for issue in issues['duplicate_dirs']:
        dup_path = issue['path']
        parent_path = os.path.dirname(dup_path)

        if not os.path.exists(dup_path):
            continue

        try:
            # 將重複目錄中的所有檔案和子目錄移動到父目錄
            for item in os.listdir(dup_path):
                src = os.path.join(dup_path, item)
                dst = os.path.join(parent_path, item)

                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        # 如果目標已存在且是目錄，遞迴移動
                        for sub_item in os.listdir(src):
                            sub_src = os.path.join(src, sub_item)
                            sub_dst = os.path.join(dst, sub_item)
                            if os.path.exists(sub_dst):
                                if os.path.isdir(sub_dst):
                                    shutil.rmtree(sub_dst)
                                else:
                                    os.remove(sub_dst)
                            shutil.move(sub_src, sub_dst)
                        os.rmdir(src)
                    else:
                        os.remove(dst)
                        shutil.move(src, dst)
                else:
                    shutil.move(src, dst)

            # 刪除空的重複目錄
            try:
                os.rmdir(dup_path)
            except:
                pass

            results['duplicate_dirs_fixed'] += 1
            print(f"✓ 重複目錄: {issue['country']}/{issue['parent']}/{issue['duplicate']} → 內容已移到 {issue['country']}/{issue['parent']}/", flush=True)
        except Exception as e:
            results['errors'].append(f"重複目錄修正失敗: {issue['duplicate']} - {str(e)}")
            print(f"❌ {issue['duplicate']}: {str(e)}", flush=True)

    # 修正國家層級重命名
    for issue in issues['country_renames']:
        old_path = issue['old_path']
        new_path = issue['new_path']

        if not os.path.exists(old_path):
            continue

        os.makedirs(new_path, exist_ok=True)

        try:
            for item in os.listdir(old_path):
                src = os.path.join(old_path, item)
                dst = os.path.join(new_path, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        # 合併子目錄
                        for sub_item in os.listdir(src):
                            sub_src = os.path.join(src, sub_item)
                            sub_dst = os.path.join(dst, sub_item)
                            if os.path.exists(sub_dst):
                                if os.path.isdir(sub_dst):
                                    shutil.rmtree(sub_dst)
                                else:
                                    os.remove(sub_dst)
                            shutil.move(sub_src, sub_dst)
                        os.rmdir(src)
                    else:
                        os.remove(dst)
                        shutil.move(src, dst)
                else:
                    shutil.move(src, dst)

            # 刪除空的舊國家目錄
            try:
                os.rmdir(old_path)
            except:
                pass

            results['country_renames_fixed'] += 1
            print(f"✓ 國家重命名: {issue['old_country']} → {issue['new_country']}", flush=True)
        except Exception as e:
            results['errors'].append(f"國家重命名失敗: {issue['old_country']} - {str(e)}")
            print(f"❌ {issue['old_country']}: {str(e)}", flush=True)

    # 修正簡體字
    for issue in issues['simplified']:
        current_path = os.path.join(issue['path'], issue['current'])
        target_path = os.path.join(issue['path'], issue['target'])

        if not os.path.exists(current_path):
            continue

        try:
            if os.path.exists(target_path):
                # 目標已存在，合併檔案
                for item in os.listdir(current_path):
                    src = os.path.join(current_path, item)
                    dst = os.path.join(target_path, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, dst)
            else:
                # 直接重命名
                os.rename(current_path, target_path)

            results['simplified_fixed'] += 1
            print(f"✓ 簡繁體: {issue['current']} → {issue['target']}", flush=True)
        except Exception as e:
            results['errors'].append(f"簡繁體修正失敗: {issue['current']} - {str(e)}")
            print(f"❌ {issue['current']}: {str(e)}", flush=True)

    # 修正一字之差
    for issue in issues['single_char']:
        short_path = issue['short_path']
        long_path = issue['long_path']

        if not os.path.exists(short_path):
            continue

        os.makedirs(long_path, exist_ok=True)

        try:
            for item in os.listdir(short_path):
                src = os.path.join(short_path, item)
                dst = os.path.join(long_path, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)

            # 刪除空的短版本目錄
            try:
                os.rmdir(short_path)
            except:
                pass

            results['single_char_fixed'] += 1
            location = f"{issue['country']}/{issue['parent']}" if 'parent' in issue else issue['country']
            print(f"✓ 一字之差: {location}/{issue['short']} → {issue['long']}", flush=True)
        except Exception as e:
            results['errors'].append(f"一字之差修正失敗: {issue['short']} - {str(e)}")
            print(f"❌ {issue['short']}: {str(e)}", flush=True)

    # 修正相似目錄
    for issue in issues['similar']:
        short_path = issue['short_path']
        long_path = issue['long_path']

        if not os.path.exists(short_path):
            continue

        os.makedirs(long_path, exist_ok=True)

        try:
            for item in os.listdir(short_path):
                src = os.path.join(short_path, item)
                dst = os.path.join(long_path, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)

            # 刪除空的短版本目錄
            try:
                os.rmdir(short_path)
            except:
                pass

            results['similar_fixed'] += 1
            print(f"✓ 相似目錄: {issue['country']}/{issue['short']} → {issue['long']}", flush=True)
        except Exception as e:
            results['errors'].append(f"相似目錄修正失敗: {issue['short']} - {str(e)}")
            print(f"❌ {issue['short']}: {str(e)}", flush=True)

    # 修正誤放的目錄
    for issue in issues['misplaced_dirs']:
        src_path = issue['src_path']
        tgt_path = issue['tgt_path']

        if not os.path.exists(src_path):
            continue

        try:
            # 如果是空目錄，直接刪除
            if issue.get('is_empty', False):
                os.rmdir(src_path)
                results['misplaced_fixed'] += 1
                print(f"✓ 誤放目錄（刪除空目錄）: {issue['src_country']}/{issue['src_dir']}", flush=True)
            else:
                # 否則移動檔案和子目錄
                os.makedirs(tgt_path, exist_ok=True)

                for item in os.listdir(src_path):
                    src = os.path.join(src_path, item)
                    dst = os.path.join(tgt_path, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, dst)

                try:
                    os.rmdir(src_path)
                except:
                    pass

                results['misplaced_fixed'] += 1
                print(f"✓ 誤放目錄: {issue['src_country']}/{issue['src_dir']} → {issue['tgt_country']}/{issue['tgt_dir']}", flush=True)
        except Exception as e:
            results['errors'].append(f"誤放目錄修正失敗: {issue['src_dir']} - {str(e)}")
            print(f"❌ {issue['src_dir']}: {str(e)}", flush=True)

    # 修正應該移到子目錄的目錄
    for issue in issues['move_to_subdir']:
        wrong_path = issue['wrong_path']
        target_path = issue['target_path']

        if not os.path.exists(wrong_path):
            continue

        try:
            # 如果是空目錄，直接刪除
            if issue.get('is_empty', False):
                os.rmdir(wrong_path)
                results['move_to_subdir_fixed'] += 1
                print(f"✓ 移到子目錄（刪除空目錄）: {issue['country']}/{issue['wrong_dir']}", flush=True)
            else:
                # 否則移動檔案和子目錄
                os.makedirs(target_path, exist_ok=True)

                for item in os.listdir(wrong_path):
                    src = os.path.join(wrong_path, item)
                    dst = os.path.join(target_path, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, dst)

                try:
                    os.rmdir(wrong_path)
                except:
                    pass

                results['move_to_subdir_fixed'] += 1
                print(f"✓ 移到子目錄: {issue['country']}/{issue['wrong_dir']} → {issue['country']}/{issue['parent_dir']}/{issue['wrong_dir']}", flush=True)
        except Exception as e:
            results['errors'].append(f"移到子目錄失敗: {issue['wrong_dir']} - {str(e)}")
            print(f"❌ {issue['wrong_dir']}: {str(e)}", flush=True)

    # 修正日本繁體字
    for issue in issues['japan_traditional']:
        current_path = os.path.join(issue['path'], issue['current'])
        target_path = os.path.join(issue['path'], issue['target'])

        if not os.path.exists(current_path):
            continue

        try:
            if os.path.exists(target_path):
                # 目標已存在，合併檔案
                for item in os.listdir(current_path):
                    src = os.path.join(current_path, item)
                    dst = os.path.join(target_path, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, dst)
            else:
                # 直接重命名
                os.rename(current_path, target_path)

            # 刪除空目錄
            try:
                os.rmdir(current_path)
            except:
                pass

            results['japan_traditional_fixed'] += 1
            print(f"✓ 日本繁體字: {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)
        except Exception as e:
            results['errors'].append(f"日本繁體字修正失敗: {issue['current']} - {str(e)}")
            print(f"❌ {issue['current']}: {str(e)}", flush=True)

    # 修正日本二級目錄的日文漢字（區→区、戶→戸等）
    for issue in issues['japan_level2_fixes']:
        current_path = issue.get('path') or issue.get('current_path')
        target_path = issue.get('target_path')

        if not os.path.exists(current_path):
            continue

        try:
            if issue.get('both_exist'):
                # 目標已存在，需要合併
                target_path = issue['target_path']
                os.makedirs(target_path, exist_ok=True)

                for item in os.listdir(current_path):
                    src = os.path.join(current_path, item)
                    dst = os.path.join(target_path, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, dst)

                try:
                    os.rmdir(current_path)
                except:
                    pass

                results['japan_level2_fixed'] += 1
                print(f"✓ 日本二級漢字（合併）: {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)
            else:
                # 只需要改名
                target_path = os.path.join(os.path.dirname(current_path), issue['target'])
                os.rename(current_path, target_path)
                results['japan_level2_fixed'] += 1
                print(f"✓ 日本二級漢字: {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)
        except Exception as e:
            results['errors'].append(f"日本二級漢字修正失敗: {issue['current']} - {str(e)}")
            print(f"❌ {issue['current']}: {str(e)}", flush=True)

    # 分類散落檔案
    for issue in issues['scattered_files']:
        src_path = issue['path']

        if not os.path.exists(src_path):
            continue

        try:
            if issue.get('target_pref'):
                # 日本的散落檔案
                target_country = issue['target_country']
                target_pref = issue['target_pref']
                target_city = issue['target_city']

                # 建立目標路徑
                target_path = os.path.join(WIKI_BASE, target_country, target_pref, target_city, issue['file'])
                target_dir = os.path.dirname(target_path)
                os.makedirs(target_dir, exist_ok=True)

                # 移動檔案
                shutil.move(src_path, target_path)
                results['scattered_fixed'] += 1
                print(f"✓ 散落檔案分類: {issue['file']} → {target_country}/{target_pref}/{target_city}/", flush=True)
            else:
                # 其他國家的散落檔案（中國、台灣）- 暫時跳過
                pass
        except Exception as e:
            results['errors'].append(f"散落檔案分類失敗: {issue['file']} - {str(e)}")
            print(f"❌ {issue['file']}: {str(e)}", flush=True)

    return results

# 主程序
print("=" * 80, flush=True)
print("🔍 Wiki 完全標準化掃描", flush=True)
print("=" * 80, flush=True)

issues = find_all_issues()

print(f"\n發現問題:", flush=True)
print(f"  簡繁體混用: {len(issues['simplified'])} 個", flush=True)
print(f"  一字之差重複: {len(issues['single_char'])} 個", flush=True)
print(f"  相似目錄: {len(issues['similar'])} 個", flush=True)
print(f"  日本繁體字: {len(issues['japan_traditional'])} 個", flush=True)
print(f"  日本二級漢字: {len(issues['japan_level2_fixes'])} 個", flush=True)
print(f"  國家重命名: {len(issues['country_renames'])} 個", flush=True)
print(f"  國家合併到子目錄: {len(issues['country_merge_to_subdir'])} 個", flush=True)
print(f"  誤放目錄: {len(issues['misplaced_dirs'])} 個", flush=True)
print(f"  應移到子目錄: {len(issues['move_to_subdir'])} 個", flush=True)
print(f"  重複目錄: {len(issues['duplicate_dirs'])} 個", flush=True)
print(f"  散落檔案: {len(issues['scattered_files'])} 個", flush=True)
print(f"  非法一級目錄: {len(issues['illegal_first_level'])} 個", flush=True)

# 顯示詳情
if issues['simplified']:
    print(f"\n📝 簡繁體混用:", flush=True)
    for issue in issues['simplified']:
        if 'parent' in issue:
            print(f"  {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)
        else:
            print(f"  {issue['country']}/{issue['current']} → {issue['target']}", flush=True)

if issues['single_char']:
    print(f"\n📝 一字之差重複:", flush=True)
    for issue in issues['single_char']:
        if 'parent' in issue:
            print(f"  {issue['country']}/{issue['parent']}/{issue['short']} → {issue['long']}", flush=True)
        else:
            print(f"  {issue['country']}/{issue['short']} → {issue['long']}", flush=True)

if issues['similar']:
    print(f"\n📝 相似目錄:", flush=True)
    for issue in issues['similar']:
        print(f"  {issue['country']}/{issue['short']} → {issue['long']}", flush=True)

if issues['japan_traditional']:
    print(f"\n📝 日本繁體字:", flush=True)
    for issue in issues['japan_traditional']:
        if 'parent' in issue:
            print(f"  {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)
        else:
            print(f"  {issue['country']}/{issue['current']} → {issue['target']}", flush=True)

if issues['japan_level2_fixes']:
    print(f"\n📝 日本二級漢字修正:", flush=True)
    for issue in issues['japan_level2_fixes']:
        if issue.get('both_exist'):
            print(f"  {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']} (需合併)", flush=True)
        else:
            print(f"  {issue['country']}/{issue['parent']}/{issue['current']} → {issue['target']}", flush=True)

if issues['country_merge_to_subdir']:
    print(f"\n📝 國家合併到子目錄:", flush=True)
    for issue in issues['country_merge_to_subdir']:
        print(f"  {issue['src_country']} → {issue['tgt_country']}/{issue['tgt_subdir']}", flush=True)

if issues['country_renames']:
    print(f"\n📝 國家重命名:", flush=True)
    for issue in issues['country_renames']:
        print(f"  {issue['old_country']} → {issue['new_country']}", flush=True)

if issues['misplaced_dirs']:
    print(f"\n📝 誤放目錄:", flush=True)
    for issue in issues['misplaced_dirs']:
        print(f"  {issue['src_country']}/{issue['src_dir']} → {issue['tgt_country']}/{issue['tgt_dir']}", flush=True)

if issues['move_to_subdir']:
    print(f"\n📝 應移到子目錄:", flush=True)
    for issue in issues['move_to_subdir']:
        print(f"  {issue['country']}/{issue['wrong_dir']} → {issue['country']}/{issue['parent_dir']}/{issue['wrong_dir']}", flush=True)

if issues['duplicate_dirs']:
    print(f"\n📝 重複目錄:", flush=True)
    for issue in issues['duplicate_dirs']:
        print(f"  {issue['country']}/{issue['parent']}/{issue['duplicate']} (含 {issue['files']} 個檔案 + {issue['subdirs']} 個子目錄)", flush=True)

if issues['scattered_files']:
    print(f"\n📝 散落檔案（前 20 個）:", flush=True)
    for i, issue in enumerate(issues['scattered_files'][:20]):
        if issue.get('target_pref'):
            print(f"  {issue['file']} → {issue['target_country']}/{issue['target_pref']}/{issue['target_city']}/", flush=True)
        else:
            print(f"  {issue['file']} → (待分類)", flush=True)
    if len(issues['scattered_files']) > 20:
        print(f"  ... 還有 {len(issues['scattered_files']) - 20} 個檔案", flush=True)

if issues['illegal_first_level']:
    print(f"\n📝 非法一級目錄:", flush=True)
    for issue in issues['illegal_first_level']:
        print(f"  {issue['country']}/{issue['dir_name']}", flush=True)

# 自動修正
print(f"\n{'='*80}", flush=True)
print(f"🔧 自動應用修正...", flush=True)
print(f"{'='*80}\n", flush=True)

results = apply_fixes(issues, auto_fix=True)

print(f"\n{'='*80}", flush=True)
print(f"✅ 完成!", flush=True)
print(f"  簡繁體修正: {results['simplified_fixed']} 個", flush=True)
print(f"  一字之差修正: {results['single_char_fixed']} 個", flush=True)
print(f"  相似目錄修正: {results['similar_fixed']} 個", flush=True)
print(f"  日本繁體字修正: {results['japan_traditional_fixed']} 個", flush=True)
print(f"  日本二級漢字修正: {results['japan_level2_fixed']} 個", flush=True)
print(f"  國家重命名修正: {results['country_renames_fixed']} 個", flush=True)
print(f"  國家合併修正: {results['country_merge_fixed']} 個", flush=True)
print(f"  誤放目錄修正: {results['misplaced_fixed']} 個", flush=True)
print(f"  移到子目錄修正: {results['move_to_subdir_fixed']} 個", flush=True)
print(f"  重複目錄修正: {results['duplicate_dirs_fixed']} 個", flush=True)
print(f"  散落檔案分類: {results['scattered_fixed']} 個", flush=True)
if results['errors']:
    print(f"  錯誤: {len(results['errors'])} 個", flush=True)
    for error in results['errors']:
        print(f"    - {error}", flush=True)
print(f"{'='*80}", flush=True)
