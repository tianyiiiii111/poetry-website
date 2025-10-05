# 诗词雅集 - 古诗词网站

一个优雅的中国古诗词网站，使用 Python Flask + SQLite 构建，数据来源于 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 项目。

## ✨ 功能特性

- 📖 **诗词浏览** - 按朝代、作者分类浏览
- 🔍 **全文搜索** - 快速搜索诗词、作者、内容
- 📱 **响应式设计** - 完美适配手机、平板、电脑
- 🎨 **中国风 UI** - 优雅的视觉设计
- 🚀 **高性能** - SQLite 全文搜索，快速响应
- 📊 **统计信息** - 诗词、作者、朝代统计
- 🔌 **RESTful API** - 提供 JSON API 接口

## 📊 数据规模

- **诗词总数**: 30万+ 首
- **作者数量**: 数千位
- **朝代范围**: 先秦至清代
- **数据来源**: [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)

## 🛠️ 技术栈

- **后端**: Python 3.8+ / Flask 3.0
- **数据库**: SQLite 3 (FTS5 全文搜索)
- **前端**: HTML5 / CSS3 / JavaScript
- **部署**: Gunicorn / Nginx (可选)

## 📦 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/tianyiiiii111/poetry-website.git
cd poetry-website
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 下载诗词数据

```bash
cd data
git clone https://github.com/chinese-poetry/chinese-poetry.git raw/chinese-poetry
cd ..
```

### 5. 导入数据

```bash
python data/scripts/import_data.py
```

这一步会创建 SQLite 数据库并导入所有诗词数据，需要几分钟时间。

### 6. 启动应用

```bash
python app.py
```

访问 http://localhost:5000 即可查看网站。

## 📁 项目结构

```
poetry-website/
├── app.py                  # Flask 主应用
├── config.py               # 配置文件
├── database.py             # 数据库连接
├── models.py               # 数据模型
├── requirements.txt        # Python 依赖
├── data/                   # 数据目录
│   ├── poetry.db          # SQLite 数据库
│   └── scripts/
│       └── import_data.py # 数据导入脚本
├── templates/              # HTML 模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── poem_detail.html   # 诗词详情
│   ├── search.html        # 搜索页
│   ├── author.html        # 作者页
│   ├── authors.html       # 作者列表
│   ├── dynasty.html       # 朝代页
│   └── dynasties.html     # 朝代列表
├── static/                 # 静态文件
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── main.js        # JavaScript
└── docs/                   # 文档
    └── deployment.md      # 部署文档
```

## 🌐 API 接口

### 随机诗词

```bash
GET /api/poems/random?count=1
```

### 搜索诗词

```bash
GET /api/poems/search?q=关键词&limit=20
```

### 统计信息

```bash
GET /api/stats
```

## 🚀 部署

### 本地部署

直接运行 `python app.py` 即可。

### 生产环境部署

详见 [部署文档](docs/deployment.md)，支持：

- Linux 服务器 + Nginx + Gunicorn
- Docker 容器化部署
- Railway / Heroku 云平台

## 🎨 界面预览

- **首页**: 随机诗词展示、统计信息、朝代导航
- **搜索页**: 全文搜索、结果列表
- **诗词详情**: 完整内容、作者信息、相关推荐
- **作者页**: 作者作品列表、分页浏览
- **朝代页**: 朝代诗词列表、分页浏览

## 📝 开发说明

### 数据库结构

```sql
-- 诗词表
CREATE TABLE poems (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    dynasty TEXT,
    content TEXT,
    paragraphs TEXT,  -- JSON 格式
    tags TEXT         -- JSON 格式
);

-- 全文搜索表
CREATE VIRTUAL TABLE poems_fts USING fts5(
    title, author, content
);
```

### 添加新功能

1. 在 `models.py` 中添加数据查询方法
2. 在 `app.py` 中添加路由
3. 在 `templates/` 中创建模板
4. 在 `static/css/style.css` 中添加样式

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 数据来源: [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)
- Flask 框架: [Flask](https://flask.palletsprojects.com/)

## 📧 联系方式

- GitHub: [@tianyiiiii111](https://github.com/tianyiiiii111)
- 项目地址: https://github.com/tianyiiiii111/poetry-website

---

**传承中华文化，品味诗词之美** 🌸
