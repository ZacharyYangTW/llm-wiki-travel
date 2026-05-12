import os
import re
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

WIKI_DIR = Path("wiki")
RAW_DIR = Path("raw")
OUTPUT_DIR = WIKI_DIR / "outputs"

def get_jaccard_similarity(s1, s2):
    set1 = set(s1.split('-'))
    set2 = set(s2.split('-'))
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    if not union:
        return 0
    return len(intersection) / len(union)

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def lint():
    report = []
    report.append("---")
    report.append("graph-excluded: true")
    report.append("---")
    report.append(f"# Lint Report - {datetime.now().strftime('%Y-%m-%d')}")
    
    all_wiki_files = list(WIKI_DIR.rglob("*.md"))
    all_slugs = [f.stem for f in all_wiki_files]
    
    # 1. YAML frontmatter validity & 4. Stub pages
    invalid_yaml = []
    stubs = []
    broken_links = []
    stale_pages = []
    wikilink_format_errors = []
    
    # Pre-load for broken link check
    valid_slugs = set(all_slugs)
    
    for file_path in all_wiki_files:
        relative_path = file_path.relative_to(WIKI_DIR)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # YAML check
        try:
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    
                    # 7. Stale pages check
                    if fm and 'updated' in fm and 'domain_volatility' in fm:
                        updated_date = fm['updated']
                        volatility = fm['domain_volatility']
                        if isinstance(updated_date, str):
                            updated_date = datetime.strptime(updated_date, '%Y-%m-%d').date()
                        
                        thresholds = {'high': 90, 'medium': 180, 'low': 365}
                        days = thresholds.get(volatility, 365)
                        if (datetime.now().date() - updated_date).days > days:
                            stale_pages.append(f"{relative_path} (updated: {updated_date}, volatility: {volatility})")
                else:
                    invalid_yaml.append(f"{relative_path} (Missing closing ---)")
            else:
                invalid_yaml.append(f"{relative_path} (Missing starting ---)")
        except Exception as e:
            invalid_yaml.append(f"{relative_path} ({str(e)})")
        
        # 4. Stub check
        body = content.split('---')[-1].strip()
        if len(body) < 100:
            stubs.append(f"{relative_path} ({len(body)} chars)")
            
        # 2. Broken Wikilinks & 9. Wikilink format
        links = re.findall(r'\[\[(.*?)\]\]', content)
        for link in links:
            clean_link = link.split('|')[0].strip()
            # 9. Format check (lowercase-hyphen)
            if not re.match(r'^[a-z0-9\-]+$', clean_link):
                wikilink_format_errors.append(f"{relative_path} -> [[{link}]]")
            
            # 2. Broken link check
            if clean_link not in valid_slugs and clean_link not in ["slug"]: # ignore placeholder
                broken_links.append(f"{relative_path} -> [[{link}]]")

    # 3. Index Consitency
    index_path = WIKI_DIR / "index.md"
    index_missing = []
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        indexed_links = re.findall(r'\[\[(.*?)\]\]', index_content)
        for link in indexed_links:
            if link not in valid_slugs and link != "slug":
                index_missing.append(link)

    # 5. Near-duplicate names
    duplicates = []
    for i in range(len(all_slugs)):
        for j in range(i + 1, len(all_slugs)):
            sim = get_jaccard_similarity(all_slugs[i], all_slugs[j])
            if sim > 0.7:
                duplicates.append(f"{all_slugs[i]} <-> {all_slugs[j]} (Sim: {sim:.2f})")

    # 6. SHA-256 Integrity
    sha_mismatches = []
    for file_path in WIKI_DIR.rglob("sources/*.md"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1])
                if fm and 'raw_file' in fm and 'raw_sha256' in fm:
                    raw_p = Path(fm['raw_file'])
                    if raw_p.exists():
                        current_sha = get_sha256(raw_p)
                        if current_sha.lower() != str(fm['raw_sha256']).lower():
                            sha_mismatches.append(f"{file_path.name}: Expected {fm['raw_sha256']}, got {current_sha}")
        except: pass

    # 8. Cross-language / URL similarity (Heuristic)
    url_similarity = []
    sources = []
    for f in WIKI_DIR.rglob("sources/*.md"):
        try:
            with open(f, 'r', encoding='utf-8') as src:
                fm = yaml.safe_load(src.read().split('---')[1])
                if fm and 'source_url' in fm:
                    sources.append({'slug': f.stem, 'url': fm['source_url']})
        except: pass
    
    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            if sources[i]['url'] and sources[j]['url'] and sources[i]['url'] == sources[j]['url']:
                url_similarity.append(f"{sources[i]['slug']} <-> {sources[j]['slug']} (Same URL: {sources[i]['url']})")

    # Writing Report
    report.append("\n## 1. YAML frontmatter 合法性")
    report.extend([f"- [ ] {p}" for p in invalid_yaml] or ["- [x] 無異常"])
    
    report.append("\n## 2. Broken Wikilinks")
    report.extend([f"- [ ] {p}" for p in broken_links] or ["- [x] 無異常"])
    
    report.append("\n## 3. Index 一致性")
    report.extend([f"- [ ] 索引中引用的 [[{l}]] 不存在" for l in index_missing] or ["- [x] 無異常"])
    
    report.append("\n## 4. Stub 頁面")
    report.extend([f"- [ ] {p}" for p in stubs] or ["- [x] 無異常"])
    
    report.append("\n## 5. 近似重複概念名稱")
    report.extend([f"- [ ] {p}" for p in duplicates] or ["- [x] 無異常"])
    
    report.append("\n## 6. SHA-256 完整性")
    report.extend([f"- [ ] {p}" for p in sha_mismatches] or ["- [x] 無異常"])
    
    report.append("\n## 7. Stale 頁面")
    report.extend([f"- [ ] {p}" for p in stale_pages] or ["- [x] 無異常"])
    
    report.append("\n## 8. 跨語言重複 / URL 相似")
    report.extend([f"- [ ] {p}" for p in url_similarity] or ["- [x] 無異常"])
    
    report.append("\n## 9. Wikilink 格式規範")
    report.extend([f"- [ ] {p}" for p in wikilink_format_errors] or ["- [x] 無異常"])

    report_file = OUTPUT_DIR / f"lint-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"Lint report generated at {report_file}")

if __name__ == "__main__":
    lint()
