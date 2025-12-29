# 🏀 基于YOLOv8的篮球训练辅助系统

<p align="center">
  <img src="./416.png" width="150" />
</p>

<p align="center">
  <strong>Basketball Training Assistance System based on YOLOv8</strong>
</p>

<p align="center">
  智能分析投篮姿势，提升训练效果
</p>

---

## 📋 项目简介

本系统是基于YOLOv8深度学习模型的篮球训练辅助系统，通过计算机视觉技术实现：

- 🎯 **目标检测**：实时检测篮球和运动员位置
- 🏃 **姿态估计**：精确识别人体17个关键点
- 📊 **动作分析**：分析投篮姿势，计算肘部角度、膝盖弯曲等关键指标
- 📈 **进度追踪**：记录训练数据，可视化展示训练进步趋势

## 🚀 快速开始

### 环境要求

- Python 3.8+
- CUDA 11.0+ (GPU加速，可选)

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

### 访问系统

启动后访问 http://localhost:5000 即可使用Web界面。

## 📁 项目结构

```
EmmasAlbert/
├── app.py                      # 主应用入口
├── requirements.txt            # 项目依赖
├── basketball_training_system/ # 核心模块
│   ├── __init__.py
│   ├── backend/               # 后端模块
│   │   ├── models/           # 检测与分析模型
│   │   │   ├── detector.py       # YOLOv8目标检测
│   │   │   ├── pose_estimator.py # 姿态估计
│   │   │   └── action_analyzer.py # 动作分析
│   │   ├── utils/            # 工具模块
│   │   │   ├── video_processor.py # 视频处理
│   │   │   ├── data_analyzer.py   # 数据分析
│   │   │   └── visualizer.py      # 可视化
│   │   └── api/              # REST API
│   │       ├── routes.py         # API路由
│   │       └── service.py        # 分析服务
│   ├── frontend/             # 前端模块
│   │   ├── templates/        # HTML模板
│   │   └── static/           # 静态资源 (CSS/JS)
│   └── tests/                # 单元测试
└── data/                     # 数据目录
    ├── videos/              # 训练视频
    ├── annotations/         # 标注数据
    └── models/              # 模型文件
```

## 🔧 系统功能

### 1. 视频分析

上传篮球训练视频，系统自动：
- 检测视频中的篮球和运动员
- 识别投篮动作及其阶段（准备、蓄力、出手、跟随）
- 计算关键角度指标
- 生成姿势质量评分和改进建议

### 2. 实时反馈

- 肘部角度分析：理想范围 85°-105°
- 肩部角度分析：理想范围 80°-120°
- 膝盖弯曲分析：理想范围 140°-170°
- 中文反馈建议

### 3. 训练记录

- 保存每次训练分析结果
- 查看历史训练数据
- 追踪进步趋势
- 导出数据（JSON/CSV）

## 🖥️ API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/analyze/video` | POST | 分析训练视频 |
| `/api/analyze/frame` | POST | 分析单帧图像 |
| `/api/sessions` | GET | 获取训练记录列表 |
| `/api/sessions/<id>` | GET | 获取指定训练详情 |
| `/api/progress` | GET | 获取训练进度 |
| `/api/export` | GET | 导出训练数据 |

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest basketball_training_system/tests/

# 运行测试并生成覆盖率报告
pytest basketball_training_system/tests/ --cov=basketball_training_system --cov-report=html
```

## 📚 技术栈

- **深度学习**: YOLOv8, PyTorch
- **计算机视觉**: OpenCV
- **后端框架**: Flask
- **数据处理**: NumPy
- **可视化**: Matplotlib

## 🎯 研究目标

1. ✅ 完成篮球关键动作数据集的采集与标注
2. ✅ 基于YOLOv8训练高精度动作检测模型
3. ✅ 实现功能完善的篮球训练辅助系统
4. ⏳ 通过实际应用测试验证系统效果

## 📖 参考文献

1. YOLO系列目标检测算法
2. Ultralytics YOLOv8框架
3. OpenPose人体姿态估计
4. MMPose开源姿态估计工具
5. 篮球运动训练智能化研究

## 📫 联系方式

- 邮箱: 2057680774@qq.com
- QQ/微信: 2057680774

## 📄 许可证

本项目仅供学术研究使用。

---

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=EmmasAlbert&show_icons=true&theme=default" width="400" />
</p>
