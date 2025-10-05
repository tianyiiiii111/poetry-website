from flask import Flask, render_template, request, jsonify
from config import config
from database import init_db
from models import PoemModel
import os

# 创建 Flask 应用
app = Flask(__name__)

# 加载配置
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# 初始化数据库
init_db()

@app.route('/')
def index():
    """首页 - 显示随机诗词和统计信息"""
    poem = PoemModel.get_random()
    stats = PoemModel.get_stats()
    dynasties = PoemModel.get_dynasties()
    return render_template('index.html', poem=poem, stats=stats, dynasties=dynasties)

@app.route('/poem/<int:poem_id>')
def poem_detail(poem_id):
    """诗词详情页"""
    poem = PoemModel.get_by_id(poem_id)
    if not poem:
        return render_template('404.html', message='诗词不存在'), 404
    
    # 获取同作者的其他诗词（随机3首）
    author_poems = PoemModel.get_by_author(poem['author'], page=1, page_size=4)
    other_poems = [p for p in author_poems['poems'] if p['id'] != poem_id][:3]
    
    return render_template('poem_detail.html', poem=poem, other_poems=other_poems)

@app.route('/search')
def search():
    """搜索页面"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return render_template('search.html', poems=[], keyword='', message='请输入搜索关键词')
    
    poems = PoemModel.search(keyword)
    
    message = None
    if not poems:
        message = f'未找到包含 "{keyword}" 的诗词'
    
    return render_template('search.html', poems=poems, keyword=keyword, message=message)

@app.route('/author/<author>')
def author_poems(author):
    """作者诗词列表"""
    page = request.args.get('page', 1, type=int)
    result = PoemModel.get_by_author(author, page=page)
    
    if not result['poems']:
        return render_template('404.html', message=f'作者 "{author}" 不存在'), 404
    
    return render_template('author.html', 
                         author=author, 
                         poems=result['poems'],
                         pagination=result)

@app.route('/dynasty/<dynasty>')
def dynasty_poems(dynasty):
    """朝代诗词列表"""
    page = request.args.get('page', 1, type=int)
    result = PoemModel.get_by_dynasty(dynasty, page=page)
    
    if not result['poems']:
        return render_template('404.html', message=f'朝代 "{dynasty}" 不存在'), 404
    
    return render_template('dynasty.html', 
                         dynasty=dynasty, 
                         poems=result['poems'],
                         pagination=result)

@app.route('/authors')
def authors():
    """作者列表"""
    page = request.args.get('page', 1, type=int)
    result = PoemModel.get_all_authors(page=page)
    
    return render_template('authors.html', 
                         authors=result['authors'],
                         pagination=result)

@app.route('/dynasties')
def dynasties():
    """朝代列表"""
    dynasties_list = PoemModel.get_dynasties()
    return render_template('dynasties.html', dynasties=dynasties_list)

# API 接口
@app.route('/api/poems/random')
def api_random_poem():
    """API: 随机诗词"""
    count = request.args.get('count', 1, type=int)
    count = min(count, 10)  # 最多10首
    
    poems = PoemModel.get_random(count=count)
    return jsonify({'success': True, 'data': poems})

@app.route('/api/poems/search')
def api_search():
    """API: 搜索诗词"""
    keyword = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)
    
    if not keyword:
        return jsonify({'success': False, 'error': '缺少搜索关键词'}), 400
    
    poems = PoemModel.search(keyword, limit=limit)
    return jsonify({'success': True, 'data': poems, 'count': len(poems)})

@app.route('/api/stats')
def api_stats():
    """API: 统计信息"""
    stats = PoemModel.get_stats()
    return jsonify({'success': True, 'data': stats})

@app.errorhandler(404)
def page_not_found(e):
    """404 错误处理"""
    return render_template('404.html', message='页面不存在'), 404

@app.errorhandler(500)
def internal_error(e):
    """500 错误处理"""
    return render_template('500.html', message='服务器内部错误'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
