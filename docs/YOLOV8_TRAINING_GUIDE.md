# YOLOv8 自定义模型训练完整指南

## 目录
- [简介](#简介)
- [环境准备](#环境准备)
- [数据集准备](#数据集准备)
- [训练流程](#训练流程)
- [模型评估](#模型评估)
- [模型导出](#模型导出)
- [常见问题](#常见问题)

---

## 简介

本指南将帮助您使用YOLOv8训练自定义的篮球检测模型，用于检测：
- 🏃 **球员** (Player)
- 🏀 **篮球** (Basketball)  
- 🎯 **球筐** (Hoop)

### 为什么选择YOLOv8？

- **速度快**：实时检测性能优异
- **精度高**：最新的目标检测算法
- **易用性**：简单的API和训练流程
- **可扩展**：支持从nano到xlarge多种模型大小

---

## 环境准备

### 1. 安装依赖

```bash
# 进入项目目录
cd /path/to/EmmasAlbert

# 安装Python依赖（如果还没有安装）
cd backend
pip install -r requirements.txt

# 验证安装
python -c "from ultralytics import YOLO; print('YOLOv8 安装成功!')"
```

### 2. 检查GPU（推荐）

```bash
# 检查CUDA是否可用
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA版本: {torch.version.cuda}')"
python -c "import torch; print(f'GPU数量: {torch.cuda.device_count()}')"
```

### 3. 系统要求

**最低配置：**
- CPU: 4核以上
- 内存: 8GB RAM
- 存储: 20GB可用空间

**推荐配置：**
- GPU: NVIDIA GPU (6GB+ 显存)
- CPU: 8核以上
- 内存: 16GB+ RAM
- 存储: 50GB+ SSD

---

## 数据集准备

### 1. 数据集格式

YOLOv8使用YOLO格式的数据集，目录结构如下：

```
basketball/                    # 数据集根目录
├── images/                    # 图像目录
│   ├── train/                # 训练集图像
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   ├── val/                  # 验证集图像
│   │   ├── img101.jpg
│   │   └── ...
│   └── test/                 # 测试集图像（可选）
│       └── ...
└── labels/                    # 标注目录
    ├── train/                # 训练集标注
    │   ├── img001.txt
    │   ├── img002.txt
    │   └── ...
    ├── val/                  # 验证集标注
    │   ├── img101.txt
    │   └── ...
    └── test/                 # 测试集标注（可选）
        └── ...
```

### 2. 标注文件格式

每个图像对应一个同名的txt标注文件，格式为：

```
class_id x_center y_center width height
```

**说明：**
- `class_id`: 类别ID (0=player, 1=basketball, 2=hoop)
- `x_center, y_center`: 边界框中心点坐标（归一化到0-1）
- `width, height`: 边界框宽高（归一化到0-1）

**示例（img001.txt）：**
```
0 0.5 0.4 0.2 0.6    # 球员
1 0.7 0.3 0.05 0.05  # 篮球
2 0.8 0.2 0.15 0.1   # 球筐
```

### 3. 标注工具推荐

**图形化标注工具：**
1. **LabelImg** - 简单易用
   ```bash
   pip install labelImg
   labelImg
   ```

2. **Roboflow** - 在线标注，自动转换格式
   - 网址: https://roboflow.com
   - 支持团队协作
   - 自动数据增强

3. **CVAT** - 专业标注工具
   - 网址: https://cvat.org
   - 支持视频标注
   - 多用户协作

### 4. 创建数据配置文件

编辑 `ai_engine/configs/basketball_dataset.yaml`:

```yaml
# 数据集根目录
path: /path/to/basketball  # 修改为你的数据集路径

# 训练集、验证集路径
train: images/train
val: images/val
test: images/test  # 可选

# 类别数量和名称
nc: 3
names:
  0: player
  1: basketball
  2: hoop
```

### 5. 数据集划分建议

- **训练集**: 70-80% 的数据
- **验证集**: 15-20% 的数据
- **测试集**: 5-10% 的数据（可选）

**推荐数量：**
- 最少：每个类别 100+ 张图像
- 推荐：每个类别 1000+ 张图像
- 理想：每个类别 5000+ 张图像

### 6. 数据集质量检查

```bash
# 使用我们的验证脚本检查数据集
cd ai_engine
python validate_dataset.py --data configs/basketball_dataset.yaml
```

---

## 训练流程

### 1. 快速开始训练

**基础训练命令：**
```bash
cd ai_engine

# 使用默认参数训练
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --epochs 100 \
    --img 640 \
    --batch 16 \
    --model n

# 查看帮助
python train_yolov8.py --help
```

### 2. 选择合适的模型大小

| 模型 | 参数量 | 速度 | 精度 | 推荐场景 |
|------|--------|------|------|----------|
| YOLOv8n (nano) | 3.2M | 最快 | 中等 | 实时应用、移动端 |
| YOLOv8s (small) | 11.2M | 快 | 好 | 实时应用、边缘设备 |
| YOLOv8m (medium) | 25.9M | 中等 | 很好 | 平衡场景 |
| YOLOv8l (large) | 43.7M | 慢 | 优秀 | 高精度要求 |
| YOLOv8x (xlarge) | 68.2M | 最慢 | 最好 | 最高精度要求 |

**选择建议：**
- **实时检测**: 使用 YOLOv8n 或 YOLOv8s
- **平衡性能**: 使用 YOLOv8m
- **高精度**: 使用 YOLOv8l 或 YOLOv8x

### 3. 训练参数详解

**基础参数：**
```bash
python train_yolov8.py \
    --model s \              # 模型大小: n/s/m/l/x
    --data configs/basketball_dataset.yaml \
    --epochs 100 \           # 训练轮数
    --img 640 \              # 图像大小: 320/416/640/1280
    --batch 16 \             # 批次大小: 8/16/32/64
    --device 0 \             # GPU ID: 0/1/2... 或 cpu
    --project runs/train \   # 保存路径
    --name basketball_v1     # 实验名称
```

**优化器参数：**
```bash
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --optimizer SGD \        # 优化器: SGD/Adam/AdamW
    --lr0 0.01 \            # 初始学习率
    --momentum 0.937 \      # SGD动量
    --weight-decay 0.0005   # 权重衰减
```

**数据增强参数：**
```bash
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --hsv-h 0.015 \         # HSV色调增强
    --hsv-s 0.7 \           # HSV饱和度增强
    --hsv-v 0.4 \           # HSV明度增强
    --degrees 10.0 \        # 旋转角度
    --translate 0.1 \       # 平移
    --scale 0.5 \           # 缩放
    --fliplr 0.5 \          # 左右翻转概率
    --mosaic 1.0 \          # 马赛克增强
    --mixup 0.0             # Mixup增强
```

### 4. 完整训练示例

**场景1: 快速验证（小数据集）**
```bash
python train_yolov8.py \
    --model n \
    --data configs/basketball_dataset.yaml \
    --epochs 50 \
    --img 640 \
    --batch 16 \
    --patience 20 \
    --name quick_test
```

**场景2: 标准训练（中等数据集）**
```bash
python train_yolov8.py \
    --model s \
    --data configs/basketball_dataset.yaml \
    --epochs 100 \
    --img 640 \
    --batch 16 \
    --optimizer SGD \
    --lr0 0.01 \
    --patience 50 \
    --name standard_v1
```

**场景3: 高精度训练（大数据集）**
```bash
python train_yolov8.py \
    --model m \
    --data configs/basketball_dataset.yaml \
    --epochs 200 \
    --img 1280 \
    --batch 8 \
    --optimizer AdamW \
    --lr0 0.001 \
    --patience 100 \
    --mosaic 1.0 \
    --mixup 0.15 \
    --name high_accuracy_v1
```

### 5. 多GPU训练

```bash
# 使用所有可用GPU
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --device 0,1,2,3 \
    --batch 64

# 注意：批次大小会自动分配到各GPU
```

### 6. 从检查点恢复训练

```bash
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --resume runs/train/basketball_v1/weights/last.pt
```

### 7. 训练监控

训练期间，可以实时查看：

**终端输出：**
```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
  1/100      2.1G      1.234      0.567      0.890        156        640
  2/100      2.1G      1.123      0.512      0.845        148        640
```

**TensorBoard可视化（如果安装）：**
```bash
# 启动TensorBoard
tensorboard --logdir runs/train

# 浏览器访问: http://localhost:6006
```

**训练结果文件：**
- `runs/train/basketball_v1/weights/best.pt` - 最佳模型
- `runs/train/basketball_v1/weights/last.pt` - 最后模型
- `runs/train/basketball_v1/results.png` - 训练曲线
- `runs/train/basketball_v1/confusion_matrix.png` - 混淆矩阵

---

## 模型评估

### 1. 验证模型性能

```bash
# 验证最佳模型
python validate_model.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --data configs/basketball_dataset.yaml

# 在测试集上评估
python validate_model.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --data configs/basketball_dataset.yaml \
    --split test
```

### 2. 性能指标解读

**主要指标：**
- **mAP50**: IoU阈值0.5时的平均精度（主要指标）
- **mAP50-95**: IoU阈值0.5-0.95的平均精度
- **Precision**: 精确率（检测正确的比例）
- **Recall**: 召回率（找到目标的比例）

**好的性能标准：**
- mAP50 > 0.8: 优秀
- mAP50 > 0.7: 良好
- mAP50 > 0.6: 可接受
- mAP50 < 0.6: 需要改进

### 3. 测试单张图像

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('runs/train/basketball_v1/weights/best.pt')

# 预测
results = model('test_image.jpg')

# 显示结果
results[0].show()

# 保存结果
results[0].save('result.jpg')
```

### 4. 测试视频

```python
from ultralytics import YOLO

model = YOLO('runs/train/basketball_v1/weights/best.pt')

# 处理视频
results = model('basketball_game.mp4', save=True)
```

---

## 模型导出

### 1. 导出为ONNX格式（推荐）

```bash
# 导出ONNX格式（跨平台）
python train_yolov8.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --export onnx \
    --img 640

# 简化ONNX模型
from ultralytics import YOLO
model = YOLO('runs/train/basketball_v1/weights/best.pt')
model.export(format='onnx', simplify=True)
```

### 2. 导出其他格式

```bash
# TorchScript格式（PyTorch环境）
python -c "from ultralytics import YOLO; YOLO('best.pt').export(format='torchscript')"

# TensorFlow格式
python -c "from ultralytics import YOLO; YOLO('best.pt').export(format='tflite')"

# CoreML格式（iOS/macOS）
python -c "from ultralytics import YOLO; YOLO('best.pt').export(format='coreml')"
```

### 3. 使用导出的模型

```python
# 使用ONNX模型
from ultralytics import YOLO

model = YOLO('best.onnx')
results = model('image.jpg')
```

---

## 常见问题

### 1. 训练问题

**Q: 训练时显存不足怎么办？**
A: 减小批次大小或图像大小
```bash
--batch 8 --img 416  # 减小批次和图像大小
```

**Q: 训练速度太慢？**
A: 
- 检查是否使用GPU
- 减小模型大小（使用yolov8n）
- 减小图像大小
- 使用更少的workers

**Q: 模型不收敛？**
A:
- 检查数据集标注是否正确
- 调整学习率（尝试 --lr0 0.001）
- 增加训练轮数
- 使用预训练权重

### 2. 数据问题

**Q: 数据集太小怎么办？**
A:
- 使用数据增强
- 收集更多数据
- 使用预训练模型
- 尝试迁移学习

**Q: 类别不平衡？**
A:
- 对少数类别进行过采样
- 使用加权损失函数
- 收集更多少数类别数据

### 3. 性能问题

**Q: 某个类别检测效果差？**
A:
- 检查该类别的标注质量
- 增加该类别的样本数
- 调整类别权重
- 增加训练轮数

**Q: 误检太多？**
A:
- 提高置信度阈值
- 增加训练数据
- 使用更大的模型
- 改进数据质量

---

## 进阶技巧

### 1. 学习率调优

```bash
# 找到最优学习率
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --lr0 0.001 \
    --lrf 0.01 \
    --cos-lr  # 使用余弦学习率衰减
```

### 2. 数据增强策略

```bash
# 强数据增强（防止过拟合）
python train_yolov8.py \
    --data configs/basketball_dataset.yaml \
    --mosaic 1.0 \
    --mixup 0.15 \
    --copy-paste 0.3 \
    --degrees 10.0 \
    --perspective 0.001
```

### 3. 模型集成

```python
from ultralytics import YOLO

# 加载多个模型
models = [
    YOLO('model1.pt'),
    YOLO('model2.pt'),
    YOLO('model3.pt')
]

# 集成预测（投票或平均）
results = [m('image.jpg') for m in models]
```

---

## 总结

训练自定义YOLOv8模型的关键步骤：

1. ✅ 准备高质量的标注数据
2. ✅ 选择合适的模型大小
3. ✅ 设置合理的训练参数
4. ✅ 监控训练过程
5. ✅ 评估和优化模型
6. ✅ 导出部署模型

**记住：好的数据比复杂的模型更重要！**

---

## 相关资源

- [YOLOv8官方文档](https://docs.ultralytics.com/)
- [训练脚本源码](train_yolov8.py)
- [配置文件示例](configs/)
- [问题反馈](https://github.com/EmmasAlbert/EmmasAlbert/issues)

---

**作者**: EmmasAlbert  
**更新日期**: 2024-01-31  
**版本**: 1.0
