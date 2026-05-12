import os
import sqlite3
import re
import yaml

# 設定路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WIKI_DIR = os.path.join(BASE_DIR, 'wiki')
DB_PATH = os.path.join(BASE_DIR, 'knowledge_index.db')

def cjk_seg(text):
    # 在中文字元之間插入空格，確保 FTS5 能索引每個字
    if not text: return ""
    # 匹配中文字元範圍
    return re.sub(r'([\u4e00-\u9fa5])', r' \1 ', text)

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 建立 FTS5 虛擬表
    cursor.execute("DROP TABLE IF EXISTS wiki_index")
    cursor.execute("""
        CREATE VIRTUAL TABLE wiki_index USING fts5(
            title,
            path,
            content,
            tags,
            tokenize='unicode61'
        )
    """)
    conn.commit()
    return conn

def index_files(conn, target_dir, recursive=True):
    cursor = conn.cursor()
    print(f"Indexing Directory: {target_dir}")
    
    # 遍歷目錄
    search_scope = os.walk(target_dir) if recursive else [(target_dir, [], os.listdir(target_dir))]
    
    for root, dirs, files in search_scope:
        # 跳過一些不需要索引的目錄
        if 'outputs' in root or '.agent' in root or 'raw' in root:
            continue
            
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # 解析 Front-matter
                title = file
                tags = ""
                content = text
                if text.startswith('---'):
                    parts = text.split('---', 2)
                    if len(parts) >= 3:
                        try:
                            meta = yaml.safe_load(parts[1])
                            title = meta.get('title', title)
                            tags = ",".join(meta.get('tags', [])) if isinstance(meta.get('tags'), list) else str(meta.get('tags', ""))
                            content = parts[2]
                        except:
                            pass
                
                rel_path = os.path.relpath(path, BASE_DIR)
                cursor.execute("INSERT INTO wiki_index (title, path, content, tags) VALUES (?, ?, ?, ?)",
                               (str(title), rel_path, cjk_seg(content.strip()), cjk_seg(tags)))
    conn.commit()

if __name__ == "__main__":
    conn = setup_db()
    # 索引 wiki 目錄 (遞迴)
    index_files(conn, WIKI_DIR, recursive=True)
    # 索引根目錄 (非遞迴，只取 .md)
    index_files(conn, BASE_DIR, recursive=False)
    
    print("Indexing complete!")
    conn.close()
