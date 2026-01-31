# 🏀 篮球训练系统 - 快速开始指南

## 📦 一键启动（推荐）

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+

### 启动步骤

```bash
# 1. 克隆仓库
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert

# 2. 启动所有服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 访问系统

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/api/docs
- **MinIO控制台**: http://localhost:9001 (账号: minioadmin/minioadmin)

### 停止服务

```bash
# 停止服务
docker-compose down

# 停止并清除所有数据
docker-compose down -v
```

## 🔧 手动部署

### 1. 后端服务

```bash
cd backend

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件配置数据库等信息

# 启动服务
uvicorn main:app --reload
```

### 2. 前端服务

```bash
cd frontend

# 安装依赖
npm install

# 配置环境
cp .env.example .env

# 启动服务
npm run dev
```

### 3. 数据库

```bash
# MySQL
mysql -u root -p
CREATE DATABASE basketball_training;
SOURCE database/schemas/schema.sql;

# Redis
redis-server
```

## 📱 功能演示

### 学生用户流程

1. **注册登录**
   ```
   POST /api/auth/register
   {
     "username": "student01",
     "email": "student@example.com",
     "password": "password123"
   }
   ```

2. **上传训练视频**
   ```
   POST /api/training/upload
   Content-Type: multipart/form-data
   ```

3. **查看分析结果**
   ```
   GET /api/training/videos/{id}/analysis
   ```

4. **查看训练记录**
   ```
   GET /api/training/records
   ```

### 教练用户流程

1. **创建班级**
   ```
   POST /api/classes
   {
     "name": "初级篮球班",
     "max_members": 30
   }
   ```

2. **制定训练计划**
   ```
   POST /api/training/plans
   {
     "student_id": 1,
     "title": "投篮提升计划"
   }
   ```

## 🎯 核心功能

### 1. 实时训练模式
- 打开摄像头
- WebSocket连接: `ws://localhost:8000/ws/training/realtime/{user_id}`
- 实时AI分析反馈

### 2. 视频分析
- 上传训练视频（MP4/AVI/MOV）
- 自动AI分析
- 生成详细报告

### 3. 数据统计
- 命中率统计
- 姿态得分
- 进步曲线
- 排行榜

### 4. 课程学习
- 教学视频
- 分级课程
- 进度追踪

## 📖 API示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 登录
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "student01", "password": "password123"}
)
token = response.json()["access_token"]

# 获取个人信息
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
print(response.json())
```

### JavaScript示例

```javascript
const BASE_URL = 'http://localhost:8000/api';

// 登录
const formData = new URLSearchParams();
formData.append('username', 'student01');
formData.append('password', 'password123');

const response = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: formData,
});

const { access_token } = await response.json();
console.log('Token:', access_token);
```

## 🔍 目录结构

```
EmmasAlbert/
├── backend/              # FastAPI后端
│   ├── app/             # 应用代码
│   │   ├── api/        # API路由
│   │   ├── models/     # 数据模型
│   │   └── middleware/ # 中间件
│   ├── config/          # 配置
│   └── main.py          # 入口文件
├── frontend/            # React前端
│   └── src/
│       ├── components/  # 组件
│       └── pages/       # 页面
├── ai_engine/           # AI引擎
│   ├── detection/       # YOLOv8检测
│   └── pose_estimation/ # 姿态估计
├── database/            # 数据库
│   └── schemas/         # SQL结构
├── docs/                # 文档
└── docker-compose.yml   # Docker配置
```

## 📚 文档资源

- [系统架构](docs/SYSTEM_ARCHITECTURE.md) - 完整架构说明
- [模块设计](docs/MODULE_DESIGN.md) - 功能模块详解
- [安装指南](docs/INSTALLATION.md) - 详细部署步骤
- [API文档](docs/API_GUIDE.md) - API使用手册
- [实现总结](docs/IMPLEMENTATION_SUMMARY.md) - 实现说明

## ❓ 常见问题

### 1. 端口冲突
```bash
# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 后端
  - "3001:3000"  # 前端
```

### 2. 数据库连接失败
```bash
# 检查MySQL服务
docker-compose ps mysql

# 查看日志
docker-compose logs mysql
```

### 3. 前端无法访问API
```bash
# 检查 frontend/.env 中的API地址
VITE_API_BASE_URL=http://localhost:8000/api
```

## 💡 技术支持

- **GitHub Issues**: https://github.com/EmmasAlbert/EmmasAlbert/issues
- **Email**: 2057680774@qq.com
- **QQ/微信**: 2057680774

## 🌟 下一步

1. 完善前端页面实现
2. 训练自定义YOLOv8模型
3. 添加更多AI分析功能
4. 开发移动端应用
5. 部署到生产环境

---

⭐️ 喜欢这个项目？给个Star支持一下！
