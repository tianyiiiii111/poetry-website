#!/usr/bin/env python3
"""
古诗词数据导入脚本
从 chinese-poetry 项目导入诗词数据到 SQLite 数据库
"""

import json
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database import init_db
from config import Config

def import_poems():
    """导入诗词数据"""
    
    # 初始化数据库
    print('初始化数据库...')
    init_db()
    
    # 连接数据库
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM poems')
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        response = input(f'数据库中已有 {existing_count} 首诗词，是否清空重新导入？(y/N): ')
        if response.lower() == 'y':
            print('清空现有数据...')
            cursor.execute('DELETE FROM poems')
            cursor.execute('DELETE FROM poems_fts')
            conn.commit()
        else:
            print('取消导入')
            conn.close()
            return
    
    # 数据源目录
    raw_dir = Path(__file__).parent.parent / 'raw' / 'chinese-poetry'
    
    if not raw_dir.exists():
        print(f'错误: 数据源目录不存在: {raw_dir}')
        print('\n请先下载 chinese-poetry 数据:')
        print('  cd data')
        print('  git clone https://github.com/chinese-poetry/chinese-poetry.git raw/chinese-poetry')
        conn.close()
        return
    
    total_count = 0
    
    # 导入唐诗
    tang_dir = raw_dir / '全唐诗'
    if tang_dir.exists():
        print('\n开始导入唐诗...')
        count = import_from_directory(cursor, tang_dir, '唐', 'poet.tang.*.json')
        total_count += count
        print(f'唐诗导入完成: {count} 首')
        conn.commit()
    
    # 导入宋诗
    song_dir = raw_dir / '全宋诗'
    if song_dir.exists():
        print('\n开始导入宋诗...')
        count = import_from_directory(cursor, song_dir, '宋', 'poet.song.*.json')
        total_count += count
        print(f'宋诗导入完成: {count} 首')
        conn.commit()
    
    # 导入宋词
    songci_dir = raw_dir / '宋词'
    if songci_dir.exists():
        print('\n开始导入宋词...')
        count = import_from_directory(cursor, songci_dir, '宋', 'ci.song.*.json')
        total_count += count
        print(f'宋词导入完成: {count} 首')
        conn.commit()
    
    # 导入元曲
    yuanqu_dir = raw_dir / '元曲'
    if yuanqu_dir.exists():
        print('\n开始导入元曲...')
        count = import_from_directory(cursor, yuanqu_dir, '元', '*.json')
        total_count += count
        print(f'元曲导入完成: {count} 首')
        conn.commit()
    
    # 导入诗经
    shijing_file = raw_dir / '诗经' / 'shijing.json'
    if shijing_file.exists():
        print('\n开始导入诗经...')
        count = import_from_file(cursor, shijing_file, '先秦')
        total_count += count
        print(f'诗经导入完成: {count} 首')
        conn.commit()
    
    # 构建全文搜索索引
    print('\n构建全文搜索索引...')
    cursor.execute('''
        INSERT INTO poems_fts(rowid, title, author, content)
        SELECT id, title, author, content FROM poems
    ''')
    conn.commit()
    
    print(f'\n✅ 数据导入完成！')
    print(f'总计导入: {total_count} 首诗词')
    
    # 显示统计信息
    cursor.execute('SELECT COUNT(DISTINCT author) FROM poems')
    author_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT dynasty) FROM poems')
    dynasty_count = cursor.fetchone()[0]
    
    print(f'作者数量: {author_count}')
    print(f'朝代数量: {dynasty_count}')
    
    conn.close()

def import_from_directory(cursor, directory, dynasty, pattern):
    """从目录导入诗词"""
    count = 0
    files = sorted(directory.glob(pattern))
    
    for i, json_file in enumerate(files, 1):
        print(f'  处理文件 [{i}/{len(files)}]: {json_file.name}', end='\r')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                poems = json.load(f)
                
                for poem in poems:
                    if import_poem(cursor, poem, dynasty):
                        count += 1
        except Exception as e:
            print(f'\n  警告: 处理文件 {json_file.name} 时出错: {e}')
    
    print()  # 换行
    return count

def import_from_file(cursor, json_file, dynasty):
    """从单个文件导入诗词"""
    count = 0
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            poems = json.load(f)
            
            for poem in poems:
                if import_poem(cursor, poem, dynasty):
                    count += 1
    except Exception as e:
        print(f'  警告: 处理文件 {json_file.name} 时出错: {e}')
    
    return count

def import_poem(cursor, poem_data, dynasty):
    """导入单首诗词"""
    try:
        # 提取数据
        title = poem_data.get('title', '无题')
        author = poem_data.get('author', '佚名')
        
        # 处理内容
        paragraphs = poem_data.get('paragraphs', [])
        if not paragraphs:
            # 有些数据格式可能不同
            paragraphs = poem_data.get('content', [])
        
        if not paragraphs:
            return False
        
        # 合并为纯文本
        content = ''.join(paragraphs)
        
        if not content.strip():
            return False
        
        # 标签
        tags = poem_data.get('tags', [])
        
        # 插入数据库
        cursor.execute('''
            INSERT INTO poems (title, author, dynasty, content, paragraphs, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            title,
            author,
            dynasty,
            content,
            json.dumps(paragraphs, ensure_ascii=False),
            json.dumps(tags, ensure_ascii=False) if tags else None
        ))
        
        return True
        
    except Exception as e:
        print(f'\n  警告: 导入诗词时出错: {e}')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('古诗词数据导入工具')
    print('=' * 60)
    
    import_poems()
    
    print('\n数据库位置:', Config.DATABASE_PATH)
    print('\n可以运行以下命令启动应用:')
    print('  python app.py')
