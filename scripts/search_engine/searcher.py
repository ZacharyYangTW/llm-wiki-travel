import sqlite3
import os
import sys
import json
import re

# 設定路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'knowledge_index.db')

def cjk_seg(text):
    if not text: return ""
    return re.sub(r'([\u4e00-\u9fa5])', r' \1 ', text)

def search(query_str):
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Please run indexer.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 使用 FTS5 的 BM25 演算法進行相關性排序
    # snippet 函數會自動擷取包含關鍵字的片段
    sql = """
        SELECT 
            title, 
            path, 
            snippet(wiki_index, 2, '【', '】', '...', 20) as context,
            rank
        FROM wiki_index 
        WHERE wiki_index MATCH ?
        ORDER BY rank
        LIMIT 10
    """
    
    try:
        # 對查詢字串做切分
        processed_query = cjk_seg(query_str)
        
        # 處理連字號問題：將整體包在引號內，使其被視為一個片語 (Phrase)
        # 除非使用者已經用了 OR/AND 指令
        if " OR " not in query_str and " AND " not in query_str:
            processed_query = f'"{processed_query}"'
            
        cursor.execute(sql, (processed_query,))
        results = cursor.fetchall()
        
        output = []
        for row in results:
            output.append({
                "title": row[0],
                "path": row[1],
                "snippet": row[2]
            })
        
        return output
    except Exception as e:
        return f"Search Error: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python searcher.py <query>")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # 修正 Windows 控制台編碼問題
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
    results = search(query)
    
    if isinstance(results, list):
        if not results:
            print(f"No results found for: {query}")
        for r in results:
            print(f"[{r['title']}] ({r['path']})")
            print(f"   ...{r['snippet']}...")
            print("-" * 40)
    else:
        print(results)
