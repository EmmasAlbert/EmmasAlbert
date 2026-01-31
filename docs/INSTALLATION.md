# 系统安装部署指南

## 目录
- [环境准备](#环境准备)
- [Docker部署（推荐）](#docker部署推荐)
- [手动部署](#手动部署)
- [常见问题](#常见问题)

## 环境准备

### 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS / Windows 10+
- **CPU**: 4核及以上
- **内存**: 8GB及以上
- **GPU**: NVIDIA GPU（可选，用于加速AI推理）
- **存储**: 50GB可用空间

### 软件依赖

#### Docker方式（推荐）
- Docker 20.10+
- Docker Compose 2.0+

#### 手动部署方式
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+
- CUDA 11.8+（如果使用GPU）

---

## Docker部署（推荐）

### 1. 安装Docker和Docker Compose

#### Ubuntu/Debian
```bash
# 更新包索引
sudo apt-get update

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### macOS
```bash
# 使用Homebrew安装
brew install docker docker-compose

# 或直接下载Docker Desktop
# https://www.docker.com/products/docker-desktop
```

#### Windows
下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### 2. 克隆项目

```bash
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert
```

### 3. 配置环境变量

```bash
# 后端配置
cp backend/.env.example backend/.env
# 编辑backend/.env，根据需要修改配置

# 前端配置
cp frontend/.env.example frontend/.env
# 编辑frontend/.env，根据需要修改配置
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 初始化数据库

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库初始化脚本
python -c "from app.models.database import init_db; init_db()"

# 退出容器
exit
```

### 6. 访问服务

- **前端界面**: http://localhost:3000
- **后端API文档**: http://localhost:8000/api/docs
- **MinIO控制台**: http://localhost:9001 (账号: minioadmin / minioadmin)

### 7. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除所有数据
docker-compose down -v
```

---

## 手动部署

### 1. 安装系统依赖

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    mysql-server redis-server \
    nodejs npm \
    git curl wget \
    build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev
```

#### macOS
```bash
brew install python@3.10 mysql redis node git
```

### 2. 克隆项目

```bash
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert
```

### 3. 部署后端

```bash
cd backend

# 创建虚拟环境
python3.10 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库等信息

# 下载YOLOv8模型（首次运行会自动下载）
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# 初始化数据库
python -c "from app.models.database import init_db; init_db()"

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 部署前端

打开新终端：

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

### 5. 配置MySQL数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE basketball_training CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户
CREATE USER 'basketball_user'@'localhost' IDENTIFIED BY 'basketball_pass';

# 授权
GRANT ALL PRIVILEGES ON basketball_training.* TO 'basketball_user'@'localhost';
FLUSH PRIVILEGES;

# 导入数据库结构
USE basketball_training;
SOURCE /path/to/EmmasAlbert/database/schemas/schema.sql;

# 退出
EXIT;
```

### 6. 启动Redis

```bash
# Ubuntu/Debian
sudo systemctl start redis-server
sudo systemctl enable redis-server

# macOS
brew services start redis
```

### 7. 安装MinIO（可选）

```bash
# 下载MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# 创建数据目录
mkdir -p ~/minio/data

# 启动MinIO
export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin
minio server ~/minio/data --console-address ":9001"
```

### 8. 启动Celery Worker（异步任务）

打开新终端：

```bash
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

---

## 生产环境部署

### 使用Nginx反向代理

```bash
# 安装Nginx
sudo apt-get install nginx

# 配置文件示例
sudo nano /etc/nginx/sites-available/basketball
```

Nginx配置内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/basketball /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 使用Systemd管理服务

创建后端服务：

```bash
sudo nano /etc/systemd/system/basketball-backend.service
```

```ini
[Unit]
Description=Basketball Training Backend
After=network.target mysql.service redis.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/EmmasAlbert/backend
Environment="PATH=/path/to/EmmasAlbert/backend/venv/bin"
ExecStart=/path/to/EmmasAlbert/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start basketball-backend
sudo systemctl enable basketball-backend

# 查看状态
sudo systemctl status basketball-backend
```

---

## 常见问题

### 1. 端口被占用

```bash
# 查看占用端口的进程
sudo lsof -i :8000  # 后端端口
sudo lsof -i :3000  # 前端端口

# 杀死进程
kill -9 <PID>
```

### 2. MySQL连接失败

- 检查MySQL服务是否启动
- 检查数据库配置（用户名、密码、数据库名）
- 检查防火墙设置

### 3. Redis连接失败

```bash
# 测试Redis连接
redis-cli ping
# 应返回 PONG

# 检查Redis服务状态
sudo systemctl status redis-server
```

### 4. Python依赖安装失败

```bash
# 使用国内镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. GPU不可用

```bash
# 检查CUDA是否安装
nvidia-smi

# 安装GPU版本的PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 6. 前端依赖安装慢

```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

### 7. 视频分析速度慢

- 使用GPU加速（安装CUDA版本的PyTorch）
- 降低视频分辨率
- 调整帧率采样频率

---

## 性能优化建议

1. **使用GPU加速AI推理**
   - 安装NVIDIA驱动和CUDA
   - 安装GPU版本的PyTorch

2. **启用Redis缓存**
   - 缓存热点数据
   - 缓存API响应

3. **使用CDN**
   - 加速静态资源加载
   - 视频文件使用CDN分发

4. **数据库优化**
   - 添加适当的索引
   - 使用连接池
   - 定期清理旧数据

5. **负载均衡**
   - 使用多个后端实例
   - Nginx负载均衡

---

## 安全建议

1. **修改默认密码**
   - 修改数据库密码
   - 修改Redis密码
   - 修改MinIO密码
   - 修改JWT密钥

2. **启用HTTPS**
   - 使用Let's Encrypt免费证书
   - 配置SSL/TLS

3. **设置防火墙**
   - 只开放必要端口
   - 限制数据库访问

4. **定期备份**
   - 数据库定期备份
   - 媒体文件定期备份

---

## 技术支持

如有问题，请：
1. 查看项目文档
2. 提交 [Issue](https://github.com/EmmasAlbert/EmmasAlbert/issues)
3. 联系作者：2057680774@qq.com
