# 部署文档

本文档详细说明如何将古诗词网站部署到不同环境。

## 目录

- [本地部署](#本地部署)
- [Linux 服务器部署](#linux-服务器部署)
- [Docker 部署](#docker-部署)
- [云平台部署](#云平台部署)

---

## 本地部署

### 开发环境

适用于本地开发和测试。

```bash
# 1. 克隆项目
git clone https://github.com/tianyiiiii111/poetry-website.git
cd poetry-website

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载数据
cd data
git clone https://github.com/chinese-poetry/chinese-poetry.git raw/chinese-poetry
cd ..

# 5. 导入数据
python data/scripts/import_data.py

# 6. 启动应用
python app.py
```

访问 http://localhost:5000

### 局域网访问

如果想让局域网内其他设备访问（如手机），确保 `app.py` 中：

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

然后通过 `http://你的电脑IP:5000` 访问。

---

## Linux 服务器部署

### 环境要求

- Ubuntu 20.04+ / Debian 10+ / CentOS 8+
- Python 3.8+
- Nginx
- 域名（可选）

### 步骤 1：安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git

# CentOS
sudo yum install -y python3 python3-pip nginx git
```

### 步骤 2：部署应用

```bash
# 创建应用目录
sudo mkdir -p /var/www/poetry
cd /var/www/poetry

# 克隆项目
sudo git clone https://github.com/tianyiiiii111/poetry-website.git .

# 创建虚拟环境
sudo python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 下载并导入数据
cd data
git clone https://github.com/chinese-poetry/chinese-poetry.git raw/chinese-poetry
cd ..
python data/scripts/import_data.py

# 设置权限
sudo chown -R www-data:www-data /var/www/poetry
```

### 步骤 3：配置 Gunicorn

创建 Gunicorn 配置文件：

```bash
sudo nano /var/www/poetry/gunicorn_config.py
```

内容：

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/www/poetry/logs/access.log"
errorlog = "/var/www/poetry/logs/error.log"
loglevel = "info"
```

创建日志目录：

```bash
sudo mkdir -p /var/www/poetry/logs
sudo chown -R www-data:www-data /var/www/poetry/logs
```

### 步骤 4：创建 Systemd 服务

```bash
sudo nano /etc/systemd/system/poetry.service
```

内容：

```ini
[Unit]
Description=Poetry Website Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/poetry
Environment="PATH=/var/www/poetry/venv/bin"
ExecStart=/var/www/poetry/venv/bin/gunicorn -c gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start poetry
sudo systemctl enable poetry
sudo systemctl status poetry
```

### 步骤 5：配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/poetry
```

内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或服务器 IP

    # 静态文件
    location /static {
        alias /var/www/poetry/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 日志
    access_log /var/log/nginx/poetry_access.log;
    error_log /var/log/nginx/poetry_error.log;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/poetry /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 步骤 6：配置防火墙

```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 步骤 7：配置 HTTPS（推荐）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## Docker 部署

### Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制应用代码
COPY . .

# 下载数据（可选，也可以挂载卷）
RUN cd data && \
    git clone https://github.com/chinese-poetry/chinese-poetry.git raw/chinese-poetry && \
    cd ..

# 导入数据
RUN python data/scripts/import_data.py

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "app:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

---

## 云平台部署

### Railway

1. 访问 [railway.app](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择你的仓库
4. Railway 自动检测 Python 项目并部署
5. 等待部署完成，获得访问链接

### Heroku

```bash
# 安装 Heroku CLI
brew install heroku/brew/heroku

# 登录
heroku login

# 创建应用
heroku create poetry-website

# 添加 Procfile
echo "web: gunicorn app:app" > Procfile

# 部署
git push heroku main

# 打开应用
heroku open
```

---

## 维护操作

### 更新应用

```bash
cd /var/www/poetry
sudo git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart poetry
```

### 查看日志

```bash
# 应用日志
sudo journalctl -u poetry -f

# Gunicorn 日志
tail -f /var/www/poetry/logs/error.log

# Nginx 日志
tail -f /var/log/nginx/poetry_error.log
```

### 备份数据库

```bash
# 手动备份
cp /var/www/poetry/data/poetry.db /backup/poetry_$(date +%Y%m%d).db

# 自动备份（添加到 crontab）
0 2 * * * cp /var/www/poetry/data/poetry.db /backup/poetry_$(date +\%Y\%m\%d).db
```

### 重新导入数据

```bash
cd /var/www/poetry
source venv/bin/activate
python data/scripts/import_data.py
sudo systemctl restart poetry
```

---

## 性能优化

### 1. 启用 Gzip 压缩（Nginx）

在 Nginx 配置中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

### 2. 静态文件缓存

已在 Nginx 配置中设置 30 天缓存。

### 3. 数据库优化

SQLite 已启用 WAL 模式和全文索引，无需额外优化。

### 4. 增加 Gunicorn Workers

根据 CPU 核心数调整：

```python
workers = (CPU核心数 * 2) + 1
```

---

## 故障排查

### 应用无法启动

```bash
# 检查服务状态
sudo systemctl status poetry

# 查看详细日志
sudo journalctl -u poetry -n 50
```

### 502 Bad Gateway

- 检查 Gunicorn 是否运行
- 检查端口 8000 是否被占用
- 查看 Gunicorn 错误日志

### 数据库错误

- 确保 `data/poetry.db` 存在
- 检查文件权限
- 重新运行导入脚本

---

## 安全建议

1. **更改 SECRET_KEY**：在生产环境设置环境变量
2. **使用 HTTPS**：通过 Certbot 配置 SSL
3. **限制访问**：配置防火墙规则
4. **定期更新**：保持系统和依赖最新
5. **备份数据**：定期备份数据库

---

## 联系支持

如有问题，请提交 Issue：https://github.com/tianyiiiii111/poetry-website/issues
