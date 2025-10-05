import sqlite3
from contextlib import contextmanager
from config import Config

@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """初始化数据库表结构"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 创建诗词表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS poems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                dynasty TEXT NOT NULL,
                content TEXT NOT NULL,
                paragraphs TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_author ON poems(author)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dynasty ON poems(dynasty)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON poems(title)')
        
        # 创建全文搜索表
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS poems_fts 
            USING fts5(title, author, content, content='poems', content_rowid='id')
        ''')
        
        conn.commit()
        print('数据库初始化完成')
