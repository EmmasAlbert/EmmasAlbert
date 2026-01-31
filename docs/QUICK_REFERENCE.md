# 📋 快速参考手册

> 常用操作速查表

## 🚀 快速启动

### Docker 方式（推荐）
```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]
```

### 手动方式
```bash
# 后端
cd backend && uvicorn main:app --reload

# 前端
cd frontend && npm run dev

# MySQL
mysql -u root -p

# Redis
redis-server
```

---

## 🎯 常用命令

### 训练相关

#### 上传视频分析
```bash
curl -X POST http://localhost:8000/api/training/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@video.mp4" \
  -F "training_type=shooting"
```

#### 查看训练记录
```bash
curl http://localhost:8000/api/training/records \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 开始实时训练
```javascript
// WebSocket连接
const ws = new WebSocket('ws://localhost:8000/ws/training/realtime/USER_ID');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('实时分析:', data);
};
```

### 用户相关

#### 注册
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student01",
    "email": "student@example.com",
    "password": "password123",
    "role": "student"
  }'
```

#### 登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student01&password=password123"
```

#### 获取个人信息
```bash
curl http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 数据分析

#### 获取统计数据
```bash
curl http://localhost:8000/api/analysis/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 导出报告
```bash
curl http://localhost:8000/api/analysis/export?format=pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o report.pdf
```

### YOLOv8 训练

#### 验证数据集
```bash
cd ai_engine/training
python validate_dataset.py --data configs/basketball_dataset.yaml
```

#### 训练模型
```bash
python train_yolov8.py \
  --model s \
  --data configs/basketball_dataset.yaml \
  --epochs 100 \
  --device 0
```

#### 评估模型
```bash
python validate_model.py \
  --model runs/train/exp/weights/best.pt \
  --data configs/basketball_dataset.yaml
```

---

## 🔧 配置文件

### 后端配置 (backend/.env)
```env
# 数据库
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/basketball_training

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=basketball-videos

# AI模型路径
YOLOV8_MODEL_PATH=models/basketball_yolov8s.pt
MEDIAPIPE_MODEL_PATH=models/pose_landmarker.task
```

### 前端配置 (frontend/.env)
```env
# API地址
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws

# 其他配置
VITE_APP_NAME=篮球训练辅助系统
VITE_APP_VERSION=2.0.0
```

### Docker配置 (docker-compose.yml)
```yaml
# 修改端口
services:
  frontend:
    ports:
      - "3001:3000"  # 外部端口:容器端口
  
  backend:
    ports:
      - "8001:8000"
```

---

## 📊 API端点速查

### 认证 API
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `POST /api/auth/refresh` - 刷新token

### 用户 API
- `GET /api/users/profile` - 获取个人信息
- `PUT /api/users/profile` - 更新个人信息
- `POST /api/users/avatar` - 上传头像
- `GET /api/users/{id}` - 获取用户信息

### 训练 API
- `POST /api/training/upload` - 上传视频
- `GET /api/training/videos` - 获取视频列表
- `GET /api/training/videos/{id}` - 获取视频详情
- `GET /api/training/videos/{id}/analysis` - 获取分析结果
- `GET /api/training/records` - 获取训练记录
- `POST /api/training/plans` - 创建训练计划
- `WS /ws/training/realtime/{user_id}` - 实时训练WebSocket

### 分析 API
- `GET /api/analysis/statistics` - 获取统计数据
- `GET /api/analysis/progress` - 获取进步数据
- `GET /api/analysis/comparison` - 获取对比数据
- `GET /api/analysis/recommendations` - 获取AI建议
- `GET /api/analysis/export` - 导出报告

### 课程 API
- `GET /api/courses` - 获取课程列表
- `GET /api/courses/{id}` - 获取课程详情
- `POST /api/courses/{id}/enroll` - 报名课程
- `GET /api/courses/my-courses` - 我的课程
- `POST /api/courses/{id}/progress` - 更新学习进度

### 成就 API
- `GET /api/achievements` - 获取成就列表
- `GET /api/achievements/my-achievements` - 我的成就
- `GET /api/leaderboard` - 排行榜

### 社交 API
- `GET /api/social/posts` - 获取动态
- `POST /api/social/posts` - 发布动态
- `POST /api/social/posts/{id}/like` - 点赞
- `POST /api/social/posts/{id}/comment` - 评论
- `GET /api/social/friends` - 好友列表
- `POST /api/social/friends/add` - 添加好友

---

## 🐛 故障排查

### 服务无法启动

#### 检查端口占用
```bash
# Linux/Mac
lsof -i :3000
lsof -i :8000

# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

#### 检查Docker状态
```bash
docker ps -a
docker-compose logs [service_name]
```

#### 重启服务
```bash
docker-compose restart [service_name]
```

### 数据库问题

#### 连接测试
```bash
# 测试MySQL连接
mysql -h localhost -u root -p -e "SELECT 1"

# 测试Redis连接
redis-cli ping
```

#### 重置数据库
```bash
# 谨慎操作！会清除所有数据
docker-compose down -v
docker-compose up -d
```

#### 导入数据库结构
```bash
docker-compose exec mysql mysql -u root -p basketball_training < database/schemas/schema.sql
```

### 前端问题

#### 清除缓存
```bash
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
```

#### 重新构建
```bash
npm run build
```

### 后端问题

#### 查看日志
```bash
docker-compose logs -f backend
```

#### 重装依赖
```bash
cd backend
pip install -r requirements.txt --force-reinstall
```

#### 重启服务
```bash
docker-compose restart backend
```

### AI模型问题

#### 下载模型
```bash
# YOLOv8
cd ai_engine
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# MediaPipe
# 从官网下载 pose_landmarker.task
```

#### 检查GPU
```bash
# NVIDIA GPU
nvidia-smi

# 检查PyTorch GPU支持
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 💾 数据备份

### 备份数据库
```bash
# MySQL备份
docker-compose exec mysql mysqldump -u root -p basketball_training > backup.sql

# 恢复
docker-compose exec -T mysql mysql -u root -p basketball_training < backup.sql
```

### 备份文件
```bash
# 备份视频和图片
tar -czf videos_backup.tar.gz data/videos/
tar -czf images_backup.tar.gz data/images/

# 恢复
tar -xzf videos_backup.tar.gz
tar -xzf images_backup.tar.gz
```

### 完整备份
```bash
# 备份所有数据
docker-compose down
tar -czf full_backup_$(date +%Y%m%d).tar.gz \
  database/ \
  backend/.env \
  frontend/.env \
  docker-compose.yml
docker-compose up -d
```

---

## 📈 性能优化

### Docker优化
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_user_id ON training_records(user_id);
CREATE INDEX idx_created_at ON training_records(created_at);
CREATE INDEX idx_video_status ON training_videos(status);
```

### Redis缓存
```python
# 使用Redis缓存热点数据
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 缓存用户统计
r.setex(f'user_stats_{user_id}', 3600, json.dumps(stats))

# 获取缓存
cached = r.get(f'user_stats_{user_id}')
```

---

## 🔐 安全相关

### 修改默认密码
```bash
# MySQL
docker-compose exec mysql mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';

# MinIO
# 在 docker-compose.yml 中修改
MINIO_ROOT_USER=new_admin
MINIO_ROOT_PASSWORD=new_password
```

### 生成密钥
```bash
# 生成JWT密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### HTTPS配置
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
}
```

---

## 📝 日志管理

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f frontend

# 最近100行
docker-compose logs --tail=100 backend
```

### 日志文件位置
```
logs/
├── backend/
│   ├── app.log
│   └── error.log
├── nginx/
│   ├── access.log
│   └── error.log
└── mysql/
    └── error.log
```

### 清理日志
```bash
# 清理Docker日志
docker-compose down
docker system prune -a --volumes

# 清理应用日志
rm -rf logs/*.log
```

---

## 🎯 常用场景

### 场景1: 新用户首次使用
```bash
1. docker-compose up -d
2. 访问 http://localhost:3000
3. 点击"注册"
4. 填写信息并选择"学生"角色
5. 登录系统
6. 上传第一个训练视频
```

### 场景2: 教练管理班级
```bash
1. 登录（教练账号）
2. 进入"班级管理"
3. 点击"创建班级"
4. 填写班级信息
5. 复制邀请码发给学生
6. 学生加入后即可管理
```

### 场景3: 训练自定义模型
```bash
1. 准备YOLO格式数据集
2. 配置 basketball_dataset.yaml
3. 验证数据集: python validate_dataset.py
4. 训练模型: python train_yolov8.py
5. 评估性能: python validate_model.py
6. 导出模型: 设置export参数
```

### 场景4: 数据分析和导出
```bash
1. 登录系统
2. 进入"数据分析"
3. 选择时间范围
4. 查看各项统计
5. 点击"导出"
6. 选择格式（PDF/Excel）
7. 下载报告
```

---

## 🔗 快速链接

### 文档
- [完整用户指南](USER_GUIDE_CN.md)
- [系统架构](SYSTEM_ARCHITECTURE.md)
- [API文档](API_GUIDE.md)
- [安装指南](INSTALLATION.md)
- [训练指南](YOLOV8_TRAINING_GUIDE_CN.md)

### 在线资源
- [GitHub仓库](https://github.com/EmmasAlbert/EmmasAlbert)
- [问题反馈](https://github.com/EmmasAlbert/EmmasAlbert/issues)
- [YOLOv8文档](https://docs.ultralytics.com/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [React文档](https://react.dev/)

### 技术支持
- 📧 邮箱: 2057680774@qq.com
- 💬 QQ/微信: 2057680774

---

<p align="center">
  <strong>保存此页面以便快速查阅！</strong>
</p>
