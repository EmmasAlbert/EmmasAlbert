# 🚀 快速开始指南

## 5分钟快速体验

### 第一步: 安装依赖

```bash
cd basketball_training_system
pip install -r requirements.txt
```

### 第二步: 启动系统

```bash
python run.py
```

### 第三步: 访问系统

打开浏览器访问: http://localhost:5000

## 💡 首次使用

### 1. 注册账号
- 点击"注册"标签
- 输入用户名和密码
- 点击"注册"按钮

### 2. 登录系统
- 使用注册的账号登录
- 进入主界面

### 3. 开始使用

#### 方式一: 实时摄像头检测
1. 点击"📷 实时摄像头"标签
2. 点击"开启摄像头"按钮
3. 允许浏览器访问摄像头
4. 系统开始实时检测和分析

#### 方式二: 视频上传分析
1. 点击"📹 视频上传"标签
2. 点击"选择视频文件"
3. 选择篮球训练视频（支持MP4, AVI, MOV, MKV）
4. 点击"上传并分析"
5. 等待系统处理
6. 查看详细分析报告

#### 方式三: 查看历史记录
1. 点击"📊 训练历史"标签
2. 查看所有训练记录
3. 点击记录查看详情

## 🎯 最佳实践

### 获得更好的检测效果

1. **光线条件**
   - 确保场地光线充足
   - 避免强烈的逆光或阴影

2. **摄像头位置**
   - 保持摄像头稳定
   - 尽量拍摄全身动作
   - 距离适中（3-5米）

3. **背景环境**
   - 选择简洁的背景
   - 避免过多干扰物体

4. **拍摄角度**
   - 侧面45度角效果最佳
   - 能清晰看到投篮动作

## 🔧 常见问题解决

### 问题1: 模型下载缓慢
**解决方案**: 
- 首次运行会自动下载YOLOv8模型（约6MB）
- 如果下载失败，可以手动下载：
  ```bash
  # 下载模型
  wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -P models/
  wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt -P models/
  ```

### 问题2: 摄像头无法打开
**解决方案**:
- 确保浏览器有摄像头权限
- 使用 https:// 或 localhost 访问
- 检查是否有其他程序占用摄像头

### 问题3: 检测不够准确
**解决方案**:
- 调整 `configs/config.yaml` 中的 `conf_threshold` 参数
- 改善光线条件
- 调整摄像头角度和距离

### 问题4: 依赖安装失败
**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 分别安装主要依赖
pip install torch torchvision
pip install ultralytics
pip install opencv-python
pip install flask flask-cors
```

## 📊 系统配置优化

### GPU加速（可选）

如果你有NVIDIA GPU，可以启用GPU加速：

1. 安装CUDA版本的PyTorch:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. 修改 `configs/config.yaml`:
```yaml
model:
  yolo:
    device: "cuda"  # 改为cuda
  pose:
    device: "cuda"  # 改为cuda
```

### 调整检测精度

编辑 `configs/config.yaml`:

```yaml
model:
  yolo:
    conf_threshold: 0.25  # 增加数值提高精度，减少误检
  pose:
    conf_threshold: 0.3   # 调整姿态估计阈值
```

## 🎓 使用示例代码

查看 `example_usage.py` 了解如何使用各个模块：

```bash
python example_usage.py
```

## 📝 下一步

- 📖 阅读完整 [README.md](README.md)
- 💻 查看 [example_usage.py](example_usage.py) 了解API使用
- 🔧 自定义 [configs/config.yaml](configs/config.yaml)
- 📊 在 [训练历史] 中查看进步曲线

## 🆘 获取帮助

如果遇到问题:
1. 查看 `logs/system.log` 日志文件
2. 阅读 [README.md](README.md) 常见问题部分
3. 联系作者: 2057680774@qq.com

---

祝你使用愉快！🏀🎯
