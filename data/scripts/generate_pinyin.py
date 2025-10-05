#!/usr/bin/env python3
"""
为诗词生成拼音
使用 pypinyin 库自动为所有诗词的每一句生成拼音
"""

import json
import sqlite3
import sys
from pathlib import Path
from pypinyin import pinyin, Style

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config

def generate_pinyin_for_text(text):
    """为文本生成拼音"""
    # 使用带声调的拼音
    result = pinyin(text, style=Style.TONE, heteronym=False)
    # 将结果扁平化为字符串列表
    return [item[0] for item in result]

def generate_pinyin_for_poem(paragraphs):
    """为诗词的每一句生成拼音"""
    if not paragraphs:
        return []
    
    pinyin_list = []
    for line in paragraphs:
        # 为每一句生成拼音
        line_pinyin = generate_pinyin_for_text(line)
        pinyin_list.append(line_pinyin)
    
    return pinyin_list

def add_pinyin_column():
    """添加 pinyin 字段到数据库"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(poems)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'pinyin' not in columns:
            print('添加 pinyin 字段到数据库...')
            cursor.execute('ALTER TABLE poems ADD COLUMN pinyin TEXT')
            conn.commit()
            print('✅ 字段添加成功')
        else:
            print('pinyin 字段已存在')
    except Exception as e:
        print(f'添加字段时出错: {e}')
    finally:
        conn.close()

def generate_all_pinyin():
    """为所有诗词生成拼音"""
    print('=' * 60)
    print('诗词拼音生成工具')
    print('=' * 60)
    
    # 确保 pinyin 字段存在
    add_pinyin_column()
    
    # 连接数据库
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute('SELECT COUNT(*) FROM poems')
    total = cursor.fetchone()[0]
    print(f'\n总共 {total} 首诗词需要生成拼音')
    
    # 检查已有拼音的数量
    cursor.execute('SELECT COUNT(*) FROM poems WHERE pinyin IS NOT NULL AND pinyin != ""')
    existing = cursor.fetchone()[0]
    
    if existing > 0:
        response = input(f'\n已有 {existing} 首诗词包含拼音，是否重新生成？(y/N): ')
        if response.lower() != 'y':
            print('取消生成')
            conn.close()
            return
    
    print('\n开始生成拼音...')
    
    # 获取所有诗词
    cursor.execute('SELECT id, paragraphs FROM poems')
    all_poems = cursor.fetchall()
    
    processed = 0
    
    for row in all_poems:
        poem_id, paragraphs_json = row
        
        try:
            # 解析 paragraphs
            paragraphs = json.loads(paragraphs_json) if paragraphs_json else []
            
            # 生成拼音
            pinyin_data = generate_pinyin_for_poem(paragraphs)
            
            # 保存到数据库
            cursor.execute(
                'UPDATE poems SET pinyin = ? WHERE id = ?',
                (json.dumps(pinyin_data, ensure_ascii=False), poem_id)
            )
            
            processed += 1
            
            # 显示进度
            if processed % 100 == 0:
                progress = (processed / total) * 100
                print(f'  进度: {processed}/{total} ({progress:.1f}%)', end='\r')
            
            # 每1000条提交一次
            if processed % 1000 == 0:
                conn.commit()
        
        except Exception as e:
            print(f'\n  警告: 处理诗词 ID {poem_id} 时出错: {e}')
    
    # 最后提交
    conn.commit()
    
    print(f'\n\n✅ 拼音生成完成！')
    print(f'成功处理: {processed} 首诗词')
    
    conn.close()

if __name__ == '__main__':
    generate_all_pinyin()
