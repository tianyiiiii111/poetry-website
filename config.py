import os

class Config:
    """应用配置"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'poetry.db')
    
    # 分页配置
    POEMS_PER_PAGE = 20
    AUTHORS_PER_PAGE = 50
    
    # 搜索配置
    SEARCH_RESULTS_LIMIT = 50

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
