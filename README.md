# 基于YOLOv8的中小学生篮球训练辅助系统 🏀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-blue.svg)](https://react.dev/)

<p align="center">
  <img src="./416.png" width="150" />
</p>

一个基于人工智能的篮球训练辅助平台，专为中小学生设计。系统利用YOLOv8深度学习模型进行实时视频分析，提供投篮检测、姿态分析、动作评估等功能，帮助学生科学提高篮球技能。

## ✨ 核心特性

### 🎯 AI智能分析
- **投篮检测**: YOLOv8实时检测篮球和篮筐，自动判断投篮结果
- **姿态分析**: MediaPipe人体姿态估计，分析投篮动作关键点
- **动作对比**: 与标准动作或NBA球星动作进行对比学习
- **轨迹追踪**: 3D篮球飞行轨迹分析和可视化

### 📊 数据分析
- 个人统计报告、命中率趋势、姿态得分分析
- 可视化数据展示（图表、热力图）
- AI生成个性化训练建议

### 🎓 教学系统
- 分级课程（初级/中级/高级）
- 教学视频库、作业系统
- 学习进度追踪

### 🏆 激励系统
- 成就徽章、排行榜
- 每日/每周挑战任务
- 虚拟奖励系统

## 📁 项目结构

```
EmmasAlbert/
├── backend/              # 后端服务（FastAPI）
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   └── middleware/  # 中间件
│   ├── config/          # 配置文件
│   └── requirements.txt # Python依赖
├── frontend/            # 前端应用（React + TypeScript）
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   └── services/    # API服务
│   └── package.json     # Node依赖
├── ai_engine/           # AI引擎
│   ├── detection/       # 目标检测
│   ├── pose_estimation/ # 姿态估计
│   ├── action_recognition/  # 动作识别
│   └── trajectory/      # 轨迹追踪
├── database/            # 数据库
│   └── schemas/         # 数据库结构
├── docs/                # 文档
│   ├── SYSTEM_ARCHITECTURE.md  # 系统架构
│   ├── MODULE_DESIGN.md        # 模块设计
│   ├── INSTALLATION.md         # 安装指南
│   └── API_GUIDE.md            # API文档
└── docker-compose.yml   # Docker编排
```

## 🚀 快速开始

### 使用Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert

# 启动所有服务
docker-compose up -d

# 访问服务
# 前端: http://localhost:3000
# 后端API: http://localhost:8000/api/docs
```

### 手动部署

详细安装步骤请查看 [安装指南](docs/INSTALLATION.md)

## 🎓 训练自定义YOLOv8模型

本项目支持训练自己的YOLOv8模型来检测篮球场景中的球员、篮球和球筐。

### 快速训练指南

1. **准备标注数据集**（YOLO格式）
2. **配置数据集路径** (`ai_engine/training/dataset_config.yaml`)
3. **开始训练**：

```bash
cd ai_engine/training

# 基础训练
python train_yolov8.py --config dataset_config.yaml --model n --epochs 100

# GPU训练（推荐）
python train_yolov8.py --config dataset_config.yaml --model s --epochs 100 --device 0
```

4. **评估模型**：

```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --mode eval \
    --weights runs/basketball_detection/basketball_yolov8s/weights/best.pt
```

### 详细教程

完整的训练教程（包括数据准备、标注工具、训练技巧等）请查看：
- 📚 [YOLOv8训练完整指南（中文）](docs/YOLOV8_TRAINING_GUIDE_CN.md)
- 📁 [训练模块说明](ai_engine/training/README.md)

### 数据集格式

```
datasets/basketball/
├── images/
│   ├── train/   # 训练集图片
│   └── val/     # 验证集图片
└── labels/
    ├── train/   # 训练集标注（YOLO格式 .txt）
    └── val/     # 验证集标注
```

## 📖 文档

- [系统架构文档](docs/SYSTEM_ARCHITECTURE.md) - 完整的系统架构说明
- [功能模块设计](docs/MODULE_DESIGN.md) - 详细的功能设计文档
- [安装部署指南](docs/INSTALLATION.md) - 完整的安装部署步骤
- [API使用指南](docs/API_GUIDE.md) - API接口文档和示例
- [项目详细说明](PROJECT_README.md) - 更详细的项目介绍

## 🛠️ 技术栈

**前端**: React 18, TypeScript, Ant Design, ECharts, Socket.IO

**后端**: FastAPI, SQLAlchemy, Celery, Redis, JWT

**AI引擎**: YOLOv8, MediaPipe, OpenCV, PyTorch

**数据库**: MySQL, Redis, MinIO

**部署**: Docker, Docker Compose, Nginx

## 🎯 主要功能模块

### 1. 用户管理 ⭐⭐⭐
- 多角色系统（学生、教练、管理员）
- 用户注册登录、个人资料管理
- 班级和小组管理

### 2. 训练管理 ⭐⭐⭐
- 实时视频分析
- 视频上传和异步分析
- 训练记录管理

### 3. AI分析 ⭐⭐⭐
- 投篮检测和命中判断
- 姿态分析和评分
- 动作对比和轨迹分析

### 4. 数据分析 ⭐⭐⭐
- 个人统计报告
- 数据可视化
- AI训练建议

### 5. 课程管理 ⭐⭐
- 教学视频库
- 分级训练课程
- 作业和进度追踪

### 6. 激励系统 ⭐⭐
- 成就徽章
- 排行榜和挑战任务

### 7. 社交互动 ⭐
- 训练动态分享
- 师生互动
- 消息通知

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

**EmmasAlbert** - 一个正在学习编程的新人，请多多指教！

- 邮箱: 2057680774@qq.com
- QQ/微信: 2057680774
- GitHub: [@EmmasAlbert](https://github.com/EmmasAlbert)

## 🙏 致谢

- [YOLOv8](https://github.com/ultralytics/ultralytics) - 目标检测模型
- [MediaPipe](https://google.github.io/mediapipe/) - 姿态估计
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [React](https://react.dev/) - 前端框架

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/EmmasAlbert/EmmasAlbert/issues)
- 发送邮件至 2057680774@qq.com

---

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=EmmasAlbert&show_icons=true&theme=default" width="400" />
</p>

⭐️ 如果这个项目对你有帮助，请给个Star支持一下！
