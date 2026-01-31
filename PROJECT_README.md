# 基于YOLOv8的中小学生篮球训练辅助系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-blue.svg)](https://react.dev/)

一个基于人工智能的篮球训练辅助平台，专为中小学生设计。系统利用YOLOv8深度学习模型进行实时视频分析，提供投篮检测、姿态分析、动作评估等功能，帮助学生科学提高篮球技能。

## ✨ 核心特性

### 🎯 AI智能分析
- **投篮检测**: YOLOv8实时检测篮球和篮筐，自动判断投篮结果
- **姿态分析**: MediaPipe人体姿态估计，分析投篮动作关键点
- **动作对比**: 与标准动作或NBA球星动作进行对比学习
- **轨迹追踪**: 3D篮球飞行轨迹分析和可视化

### 📊 数据分析
- **个人统计**: 命中率、姿态得分、训练时长等全方位统计
- **进步追踪**: 可视化展示训练进步曲线
- **对比分析**: 与同龄人、班级平均水平对比
- **智能建议**: AI生成个性化训练改进建议

### 🎓 教学系统
- **分级课程**: 初级、中级、高级篮球教学课程
- **视频教学**: 专业教学视频库
- **作业系统**: 教练布置任务，学生完成练习
- **进度追踪**: 实时查看学习进度

### 🏆 激励系统
- **成就徽章**: 解锁各种训练成就
- **排行榜**: 班级和全站排行榜
- **挑战任务**: 每日/每周挑战任务
- **虚拟奖励**: 勋章、称号、虚拟装备

### 👥 社交互动
- **训练动态**: 分享训练成果
- **师生互动**: 教练点评指导
- **好友系统**: 与好友一起进步
- **消息通知**: 及时接收各类通知

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端展示层 (React)                         │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │ 用户管理   │ │ 实时训练   │ │ 数据分析   │ │ 课程管理   │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└────────────────────────┬────────────────────────────────────────┘
                         │ RESTful API / WebSocket
┌────────────────────────▼────────────────────────────────────────┐
│                     应用服务层 (FastAPI)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │用户认证   │ │视频处理   │ │训练管理   │ │报告生成   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      AI推理层 (YOLOv8/MediaPipe)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │目标检测   │ │姿态估计   │ │动作识别   │ │轨迹追踪   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    数据存储层 (MySQL/Redis/MinIO)                │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (推荐)

### 使用Docker部署（推荐）

1. 克隆仓库
```bash
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert
```

2. 启动所有服务
```bash
docker-compose up -d
```

3. 访问服务
- 前端: http://localhost:3000
- 后端API文档: http://localhost:8000/api/docs
- MinIO控制台: http://localhost:9001

### 手动部署

#### 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库等信息

# 初始化数据库
python -c "from app.models.database import init_db; init_db()"

# 启动服务
uvicorn main:app --reload
```

#### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📖 使用说明

### 学生用户

1. **注册登录**: 使用邮箱或手机号注册账号
2. **完善资料**: 填写身高、体重等身体数据
3. **开始训练**: 
   - 实时训练模式：打开摄像头进行实时分析
   - 视频上传模式：上传训练视频进行分析
4. **查看分析**: 查看投篮命中率、姿态评分等数据
5. **学习课程**: 观看教学视频，完成训练任务
6. **解锁成就**: 完成各种挑战，获得徽章奖励

### 教练用户

1. **创建班级**: 创建班级并生成邀请码
2. **管理学生**: 邀请学生加入班级
3. **制定计划**: 为学生制定个性化训练计划
4. **点评指导**: 查看学生训练数据，给予专业指导
5. **布置作业**: 发布训练任务，追踪完成情况

## 📚 API文档

启动后端服务后，访问以下地址查看完整API文档：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 主要API端点

```
认证相关:
POST   /api/auth/register          # 用户注册
POST   /api/auth/login            # 用户登录
POST   /api/auth/logout           # 用户登出

训练管理:
POST   /api/training/upload       # 上传视频
GET    /api/training/videos/{id}  # 获取视频信息
GET    /api/training/records      # 获取训练记录

AI分析:
POST   /api/analysis/shot-detection  # 投篮检测
POST   /api/analysis/pose-analysis   # 姿态分析
GET    /api/analysis/trajectory/{id} # 轨迹分析

课程管理:
GET    /api/courses               # 获取课程列表
POST   /api/courses/{id}/enroll   # 报名课程

成就系统:
GET    /api/achievements          # 获取成就列表
GET    /api/achievements/leaderboard  # 排行榜
```

## 🛠️ 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **UI库**: Ant Design
- **状态管理**: Zustand
- **图表**: ECharts
- **视频**: Video.js
- **实时通信**: Socket.IO

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **认证**: JWT
- **任务队列**: Celery
- **API文档**: OpenAPI

### AI引擎
- **目标检测**: YOLOv8 (Ultralytics)
- **姿态估计**: MediaPipe
- **视频处理**: OpenCV
- **深度学习**: PyTorch

### 数据存储
- **数据库**: MySQL
- **缓存**: Redis
- **对象存储**: MinIO

## 📊 数据库设计

详细的数据库表结构见 `database/schemas/schema.sql`

主要数据表：
- `users`: 用户表
- `user_profiles`: 用户资料
- `training_videos`: 训练视频
- `training_records`: 训练记录
- `video_analysis`: 分析结果
- `courses`: 课程信息
- `achievements`: 成就系统
- `posts`: 训练动态

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**EmmasAlbert**

- Email: 2057680774@qq.com
- QQ/微信: 2057680774
- GitHub: [@EmmasAlbert](https://github.com/EmmasAlbert)

## 🙏 致谢

- [YOLOv8](https://github.com/ultralytics/ultralytics) - 目标检测模型
- [MediaPipe](https://google.github.io/mediapipe/) - 姿态估计
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [React](https://react.dev/) - 前端框架
- [Ant Design](https://ant.design/) - UI组件库

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/EmmasAlbert/EmmasAlbert/issues)
- 发送邮件至 2057680774@qq.com

---

⭐️ 如果这个项目对你有帮助，请给个Star支持一下！
