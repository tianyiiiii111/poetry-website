import json
from database import get_db
from config import Config

class PoemModel:
    """诗词数据模型"""
    
    @staticmethod
    def search(keyword, limit=None):
        """全文搜索诗词"""
        if limit is None:
            limit = Config.SEARCH_RESULTS_LIMIT
            
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 尝试 FTS5 全文搜索
            try:
                cursor.execute('''
                    SELECT p.* FROM poems p
                    JOIN poems_fts ON poems_fts.rowid = p.id
                    WHERE poems_fts MATCH ?
                    LIMIT ?
                ''', (keyword, limit))
                rows = cursor.fetchall()
                
                # 如果 FTS5 搜索有结果，直接返回
                if rows:
                    return [PoemModel._row_to_dict(row) for row in rows]
            except:
                pass
            
            # 如果 FTS5 搜索失败或无结果，使用 LIKE 模糊搜索
            search_pattern = f'%{keyword}%'
            cursor.execute('''
                SELECT * FROM poems 
                WHERE title LIKE ? OR author LIKE ? OR content LIKE ?
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit))
            
            rows = cursor.fetchall()
            return [PoemModel._row_to_dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(poem_id):
        """根据 ID 获取诗词"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM poems WHERE id = ?', (poem_id,))
            row = cursor.fetchone()
            
            if row:
                return PoemModel._row_to_dict(row)
            return None
    
    @staticmethod
    def get_by_author(author, page=1, page_size=None):
        """根据作者获取诗词列表"""
        if page_size is None:
            page_size = Config.POEMS_PER_PAGE
            
        offset = (page - 1) * page_size
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute('SELECT COUNT(*) as total FROM poems WHERE author = ?', (author,))
            total = cursor.fetchone()['total']
            
            # 获取分页数据（有标题的诗歌优先）
            cursor.execute('''
                SELECT * FROM poems 
                WHERE author = ?
                ORDER BY 
                    CASE WHEN title = '无题' THEN 1 ELSE 0 END,
                    id
                LIMIT ? OFFSET ?
            ''', (author, page_size, offset))
            
            rows = cursor.fetchall()
            poems = [PoemModel._row_to_dict(row) for row in rows]
            
            return {
                'poems': poems,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
    
    @staticmethod
    def get_by_dynasty(dynasty, page=1, page_size=None):
        """根据朝代获取诗词列表"""
        if page_size is None:
            page_size = Config.POEMS_PER_PAGE
            
        offset = (page - 1) * page_size
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute('SELECT COUNT(*) as total FROM poems WHERE dynasty = ?', (dynasty,))
            total = cursor.fetchone()['total']
            
            # 获取分页数据（有标题的诗歌优先）
            cursor.execute('''
                SELECT * FROM poems 
                WHERE dynasty = ?
                ORDER BY 
                    CASE WHEN title = '无题' THEN 1 ELSE 0 END,
                    id
                LIMIT ? OFFSET ?
            ''', (dynasty, page_size, offset))
            
            rows = cursor.fetchall()
            poems = [PoemModel._row_to_dict(row) for row in rows]
            
            return {
                'poems': poems,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
    
    @staticmethod
    def get_random(count=1):
        """获取随机诗词"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM poems ORDER BY RANDOM() LIMIT ?', (count,))
            
            if count == 1:
                row = cursor.fetchone()
                return PoemModel._row_to_dict(row) if row else None
            else:
                rows = cursor.fetchall()
                return [PoemModel._row_to_dict(row) for row in rows]
    
    @staticmethod
    def get_all_authors(page=1, page_size=None):
        """获取所有作者列表"""
        if page_size is None:
            page_size = Config.AUTHORS_PER_PAGE
            
        offset = (page - 1) * page_size
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute('SELECT COUNT(DISTINCT author) as total FROM poems')
            total = cursor.fetchone()['total']
            
            # 获取分页数据
            cursor.execute('''
                SELECT author, dynasty, COUNT(*) as poem_count
                FROM poems
                GROUP BY author, dynasty
                ORDER BY poem_count DESC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            
            rows = cursor.fetchall()
            authors = [dict(row) for row in rows]
            
            return {
                'authors': authors,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
    
    @staticmethod
    def get_dynasties():
        """获取所有朝代及诗词数量"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT dynasty, COUNT(*) as poem_count
                FROM poems
                GROUP BY dynasty
                ORDER BY 
                    CASE dynasty
                        WHEN '先秦' THEN 1
                        WHEN '汉' THEN 2
                        WHEN '魏晋' THEN 3
                        WHEN '南北朝' THEN 4
                        WHEN '隋' THEN 5
                        WHEN '唐' THEN 6
                        WHEN '宋' THEN 7
                        WHEN '元' THEN 8
                        WHEN '明' THEN 9
                        WHEN '清' THEN 10
                        ELSE 11
                    END
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def get_stats():
        """获取统计信息"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 总诗词数
            cursor.execute('SELECT COUNT(*) as total_poems FROM poems')
            total_poems = cursor.fetchone()['total_poems']
            
            # 总作者数
            cursor.execute('SELECT COUNT(DISTINCT author) as total_authors FROM poems')
            total_authors = cursor.fetchone()['total_authors']
            
            # 朝代数
            cursor.execute('SELECT COUNT(DISTINCT dynasty) as total_dynasties FROM poems')
            total_dynasties = cursor.fetchone()['total_dynasties']
            
            return {
                'total_poems': total_poems,
                'total_authors': total_authors,
                'total_dynasties': total_dynasties
            }
    
    @staticmethod
    def _row_to_dict(row):
        """将数据库行转换为字典，解析 JSON 字段"""
        if not row:
            return None
            
        poem = dict(row)
        
        # 解析 JSON 字段
        if 'paragraphs' in poem and poem['paragraphs']:
            try:
                poem['paragraphs'] = json.loads(poem['paragraphs'])
            except:
                poem['paragraphs'] = []
        
        if 'tags' in poem and poem['tags']:
            try:
                poem['tags'] = json.loads(poem['tags'])
            except:
                poem['tags'] = []
        
        if 'pinyin' in poem and poem['pinyin']:
            try:
                poem['pinyin'] = json.loads(poem['pinyin'])
            except:
                poem['pinyin'] = []
        
        return poem
