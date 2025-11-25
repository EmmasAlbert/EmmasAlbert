# 🏀 YOLOv8篮球训练辅助系统

基于YOLOv8的中小学篮球训练辅助系统，提供实时视频分析、投篮姿态评估和训练建议。

## 📋 项目简介

本系统采用先进的深度学习技术YOLOv8，实现了：
- 🎯 **实时检测**：准确识别篮球、篮筐和运动员
- 🤸 **姿态分析**：分析投篮姿势，提供专业建议
- 📹 **多种模式**：支持实时摄像头和视频上传两种检测方式
- 👤 **用户管理**：完整的注册登录系统
- 📊 **数据可视化**：训练历史记录和进度追踪
- 💡 **智能反馈**：根据投篮姿态给出优化建议

## 🎓 研究背景

本项目为**本科生毕业设计**，研究课题为"基于YOLOv8的中小学篮球训练辅助系统设计与实现"。

**作者**: 赖炳灿  
**学号**: 2201133075  
**学院**: 计算与信息科学学院  
**专业**: 智能科学与技术  
**年级**: 2022级  
**时间**: 2025年10月12日

## 🚀 功能特性

### 1. 实时摄像头检测
- 📷 开启电脑摄像头进行实时检测
- 🎯 实时识别篮球、篮筐、人员
- 💬 即时反馈投篮姿态建议

### 2. 视频上传分析
- 📹 支持多种视频格式（MP4, AVI, MOV, MKV）
- 📊 完整的训练分析报告
- 📈 投篮动作质量评分

### 3. 投篮姿态分析
- 🔍 肘部角度检测
- 📏 出手高度分析
- ⚖️ 身体对齐度评估
- ✋ 投篮手识别

### 4. 用户系统
- 👤 用户注册与登录
- 📚 个人训练历史记录
- 📊 训练数据统计分析

## 🛠️ 技术栈

### 后端
- **Python 3.8+**
- **Flask**: Web框架
- **YOLOv8**: 目标检测和姿态估计
- **OpenCV**: 图像处理
- **SQLite**: 数据库

### 前端
- **HTML5/CSS3**
- **JavaScript (ES6+)**
- **Canvas API**: 视频处理

### AI模型
- **YOLOv8n**: 目标检测（篮球、人员）
- **YOLOv8n-pose**: 姿态估计
- **自定义算法**: 篮筐检测

## 📦 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert/basketball_training_system
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置设置
编辑 `configs/config.yaml` 文件，根据需要调整配置：
- 模型路径
- 置信度阈值
- 服务器端口等

## 🎮 使用方法

### 启动服务器
```bash
cd basketball_training_system
python run.py
```

服务器默认运行在: `http://localhost:5000`

### 访问系统
1. 打开浏览器访问 `http://localhost:5000`
2. 注册新账号或使用现有账号登录
3. 选择功能：
   - **实时摄像头**: 点击"开启摄像头"进行实时检测
   - **视频上传**: 上传训练视频进行分析
   - **训练历史**: 查看历史训练记录

## 📂 项目结构

```
basketball_training_system/
├── backend/                 # 后端代码
│   ├── app.py              # Flask主应用
│   └── database.py         # 数据库管理
├── configs/                # 配置文件
│   └── config.yaml         # 主配置文件
├── data/                   # 数据目录
│   ├── raw/               # 原始视频
│   ├── processed/         # 处理后数据
│   └── annotations/       # 标注数据
├── frontend/              # 前端代码
│   ├── static/           # 静态资源
│   │   ├── css/         # 样式文件
│   │   └── js/          # JavaScript
│   └── templates/        # HTML模板
├── models/                # 模型代码
│   ├── basketball_detector.py  # 篮球检测
│   ├── pose_estimator.py       # 姿态估计
│   ├── shot_analyzer.py        # 投篮分析
│   └── hoop_detector.py        # 篮筐检测
├── utils/                 # 工具函数
│   ├── config_loader.py  # 配置加载
│   ├── logger.py         # 日志管理
│   └── video_utils.py    # 视频处理
├── logs/                  # 日志文件
├── outputs/              # 输出文件
│   ├── videos/          # 处理后视频
│   └── reports/         # 分析报告
├── requirements.txt      # 依赖项
└── README.md            # 说明文档
```

## 🎯 核心算法

### 1. 篮球检测
使用YOLOv8检测篮球和运动员：
- 目标类别：person (人), sports ball (篮球)
- 实时跟踪篮球轨迹
- 多目标追踪

### 2. 篮筐检测
基于颜色和轮廓的篮筐检测：
- HSV颜色空间转换
- 橙色/红色区域检测
- 形态学处理和轮廓识别

### 3. 姿态估计
使用YOLOv8-Pose进行人体关键点检测：
- 17个关键点检测（COCO格式）
- 骨架可视化
- 关键角度计算

### 4. 投篮分析
多维度投篮姿态评估：
- **肘部角度**: 检测投篮手臂弯曲度（建议60-110°）
- **出手高度**: 评估出手点是否足够高
- **身体对齐**: 检查肩膀是否水平
- **投篮时机**: 自动识别投篮瞬间

### 评分系统
- 满分100分
- 三个评估维度各占33.3分
- 实时反馈优化建议

## 📊 数据库设计

### users 表 - 用户信息
- id: 用户ID
- username: 用户名
- password_hash: 密码哈希
- email: 邮箱
- full_name: 姓名
- created_at: 创建时间
- last_login: 最后登录时间

### training_sessions 表 - 训练记录
- id: 记录ID
- user_id: 用户ID
- session_date: 训练时间
- video_path: 视频路径
- total_shots: 总投篮次数
- average_score: 平均得分
- notes: 备注

### shot_analysis 表 - 投篮分析
- id: 分析ID
- session_id: 训练记录ID
- timestamp: 时间戳
- elbow_angle: 肘部角度
- release_height: 出手高度
- body_alignment: 身体对齐度
- form_score: 姿势得分
- feedback: 反馈建议

## 🔧 配置说明

### 模型配置
```yaml
model:
  yolo:
    model_path: "models/yolov8n.pt"  # 模型路径
    conf_threshold: 0.25              # 置信度阈值
    device: "cuda"                    # 使用GPU (cuda) 或 CPU (cpu)
```

### 投篮分析阈值
```yaml
shot_analysis:
  shooting_thresholds:
    elbow_angle_min: 60      # 肘部最小角度
    elbow_angle_max: 110     # 肘部最大角度
    release_height_ratio: 1.3 # 出手高度比例
```

## 🎨 界面预览

### 登录界面
- 简洁的用户认证界面
- 注册/登录切换
- 表单验证

### 实时检测界面
- 摄像头视频流
- 实时检测信息显示
- 动态反馈面板

### 视频分析界面
- 拖拽上传视频
- 进度条显示
- 详细分析报告

### 训练历史界面
- 卡片式历史记录
- 得分可视化
- 点击查看详情

## ⚙️ 系统要求

### 硬件要求
- **CPU**: Intel i5 或更高
- **内存**: 8GB RAM 或更高
- **GPU**: NVIDIA GPU（可选，用于加速）
- **摄像头**: 支持720p或更高分辨率

### 软件要求
- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.8 或更高版本
- **浏览器**: Chrome, Firefox, Edge（最新版本）

## 📝 使用示例

### Python API使用
```python
from models.basketball_detector import BasketballDetector
from models.pose_estimator import PoseEstimator
from models.shot_analyzer import ShotAnalyzer

# 初始化检测器
detector = BasketballDetector()
pose_estimator = PoseEstimator()
analyzer = ShotAnalyzer(pose_estimator)

# 检测图像
import cv2
frame = cv2.imread('basketball_shot.jpg')

# 检测篮球和人
ball_dets, player_dets = detector.detect_basketball_and_players(frame)

# 姿态估计
poses = pose_estimator.estimate(frame)

# 分析投篮姿势
if poses:
    analysis = analyzer.analyze_shooting_form(poses[0]['keypoints'])
    print(f"投篮得分: {analysis['form_score']}")
    print("反馈建议:")
    for feedback in analysis['feedback']:
        print(f"  - {feedback}")
```

## 🐛 常见问题

### Q1: 注册/登录时报错 "table users has no column named age"？
A: 这是因为数据库结构需要更新。请执行以下步骤：

**方法1：运行修复脚本（推荐）**
```bash
python fix_database.py
```

**方法2：删除旧数据库重新开始**
```bash
# Windows
del data\basketball_training.db

# Linux/Mac
rm data/basketball_training.db
```

然后重新运行 `python run.py`

### Q2: 模型下载失败？
A: 首次运行时，系统会自动从Ultralytics下载YOLOv8模型。如果下载失败，可以手动下载模型文件放到 `models/` 目录。

### Q3: 静态文件404错误（CSS/JS加载失败）？
A: 请确保使用最新代码。如果问题仍然存在，请检查：
1. 确保从正确的目录启动：`cd basketball_training_system && python run.py`
2. 检查 `frontend/static/` 目录是否存在

### Q4: 摄像头无法打开？
A: 请检查：
1. 浏览器是否有摄像头权限
2. 是否有其他应用占用摄像头
3. 使用HTTPS或localhost访问

### Q5: 检测效果不佳？
A: 可以调整以下参数：
- 增加 `conf_threshold` 以提高检测精度
- 调整光线条件，确保场景明亮
- 使用更高分辨率的摄像头

### Q6: GPU加速如何设置？
A: 在 `config.yaml` 中设置 `device: "cuda"`，需要安装CUDA和cuDNN。

## 🔐 安全说明

- 用户密码使用SHA256哈希存储
- Session管理确保用户认证安全
- 上传文件大小限制（500MB）
- 文件名安全处理

## 📈 未来改进

- [ ] 添加更多投篮动作识别（三分球、罚球等）
- [ ] 支持多人同时分析
- [ ] 添加训练计划推荐
- [ ] 移动端APP开发
- [ ] 云端部署支持
- [ ] 3D姿态可视化
- [ ] 数据导出功能

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目为学术研究项目，仅供学习交流使用。

## 📧 联系方式

- **作者**: 赖炳灿
- **邮箱**: 2057680774@qq.com
- **QQ/微信**: 2057680774

## 🙏 致谢

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Flask](https://flask.palletsprojects.com/)
- [OpenCV](https://opencv.org/)

---

**注意**: 首次运行时，系统会自动下载YOLOv8模型文件（约6MB），请确保网络连接正常。

如有问题，请查看 `logs/` 目录中的日志文件进行调试。
