# YOLOv8自定义模型训练完整指南

## 目录
- [概述](#概述)
- [数据集准备](#数据集准备)
- [标注工具](#标注工具)
- [训练步骤](#训练步骤)
- [模型评估](#模型评估)
- [模型使用](#模型使用)
- [常见问题](#常见问题)

---

## 概述

本指南将教你如何使用YOLOv8训练自己的篮球场景检测模型，能够识别：
- **球员** (player)
- **篮球** (basketball)
- **球筐** (hoop)

### 为什么需要训练自定义模型？

YOLOv8的预训练模型（基于COCO数据集）虽然能检测篮球，但无法准确识别：
1. 篮球场上的球员
2. 篮筐/篮框
3. 特定场景下的篮球

因此，需要使用你自己标注的数据集训练专用模型。

---

## 数据集准备

### 1. 数据集目录结构

你的数据集应该按照以下结构组织：

```
datasets/
└── basketball/
    ├── images/
    │   ├── train/          # 训练集图片
    │   │   ├── img_001.jpg
    │   │   ├── img_002.jpg
    │   │   └── ...
    │   ├── val/            # 验证集图片
    │   │   ├── img_101.jpg
    │   │   ├── img_102.jpg
    │   │   └── ...
    │   └── test/           # 测试集图片（可选）
    │       ├── img_201.jpg
    │       └── ...
    └── labels/
        ├── train/          # 训练集标注
        │   ├── img_001.txt
        │   ├── img_002.txt
        │   └── ...
        ├── val/            # 验证集标注
        │   ├── img_101.txt
        │   ├── img_102.txt
        │   └── ...
        └── test/           # 测试集标注（可选）
            ├── img_201.txt
            └── ...
```

**重要说明**：
- 每张图片都需要对应一个同名的`.txt`标注文件
- 标注文件和图片必须在对应的目录中（train/val/test）
- 建议训练集:验证集比例为 8:2 或 7:3

### 2. 标注文件格式（YOLO格式）

每个`.txt`文件包含多行，每行一个目标，格式为：

```
<class_id> <x_center> <y_center> <width> <height>
```

**参数说明**：
- `class_id`: 类别ID（0=player, 1=basketball, 2=hoop）
- `x_center`: 边界框中心点x坐标（归一化到0-1）
- `y_center`: 边界框中心点y坐标（归一化到0-1）
- `width`: 边界框宽度（归一化到0-1）
- `height`: 边界框高度（归一化到0-1）

**示例标注文件** (`img_001.txt`)：
```
0 0.512 0.345 0.156 0.423
1 0.678 0.234 0.045 0.067
2 0.823 0.123 0.089 0.156
```

这表示：
- 第1行：球员，中心点(0.512, 0.345)，宽度0.156，高度0.423
- 第2行：篮球，中心点(0.678, 0.234)，宽度0.045，高度0.067
- 第3行：球筐，中心点(0.823, 0.123)，宽度0.089，高度0.156

### 3. 数据集规模建议

| 类别 | 最少图片数 | 推荐图片数 | 说明 |
|------|-----------|-----------|------|
| 训练集 | 100张 | 500-2000张 | 越多越好 |
| 验证集 | 20张 | 100-400张 | 约为训练集的20% |
| 每类别样本 | 50个 | 200-1000个 | 保证每个类别充足 |

---

## 标注工具

推荐使用以下工具进行数据标注：

### 1. LabelImg（推荐）

**优点**：简单易用，支持YOLO格式

**安装**：
```bash
pip install labelImg
```

**使用**：
```bash
labelImg
```

**操作步骤**：
1. 打开图片目录
2. 选择"YOLO"格式
3. 设置标注保存目录
4. 按`w`键创建边界框
5. 选择类别（player/basketball/hoop）
6. 按`Ctrl+S`保存
7. 按`d`键切换到下一张图片

### 2. CVAT（适合团队协作）

在线标注工具：https://cvat.org

**特点**：
- 支持多人协作
- 云端存储
- 自动标注辅助
- 支持导出YOLO格式

### 3. Roboflow（推荐，功能全面）

网址：https://roboflow.com

**特点**：
- 在线标注
- 数据增强
- 自动划分数据集
- 直接导出YOLOv8格式
- 免费版足够个人使用

---

## 训练步骤

### 第一步：准备配置文件

1. 复制配置模板：
```bash
cd ai_engine/training
cp dataset_config.yaml my_basketball_config.yaml
```

2. 编辑`my_basketball_config.yaml`，修改数据集路径：
```yaml
path: /path/to/your/datasets/basketball
train: images/train
val: images/val
test: images/test  # 可选

nc: 3
names:
  0: player
  1: basketball
  2: hoop
```

### 第二步：开始训练

#### 基础训练命令

```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model n \
    --epochs 100 \
    --batch 16 \
    --imgsz 640
```

#### 参数说明

| 参数 | 说明 | 默认值 | 建议值 |
|------|------|-------|--------|
| `--config` | 数据集配置文件 | 必需 | - |
| `--model` | 模型大小 | n | n/s/m |
| `--epochs` | 训练轮数 | 100 | 100-300 |
| `--batch` | 批次大小 | 16 | 8-32 |
| `--imgsz` | 图像大小 | 640 | 640/1280 |
| `--device` | 设备 | 自动 | 0/cpu |

#### 模型大小选择

| 模型 | 参数量 | 速度 | 精度 | 推荐场景 |
|------|--------|------|------|---------|
| yolov8n | 3.2M | 最快 | 较低 | 实时应用、移动端 |
| yolov8s | 11.2M | 快 | 中等 | 平衡性能和速度 |
| yolov8m | 25.9M | 中等 | 较高 | 需要更高精度 |
| yolov8l | 43.7M | 慢 | 高 | 离线处理 |
| yolov8x | 68.2M | 最慢 | 最高 | 最高精度要求 |

**建议**：初次训练使用`yolov8n`或`yolov8s`

### 第三步：训练示例

#### 示例1：快速训练（适合测试）
```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model n \
    --epochs 50 \
    --batch 16 \
    --device 0
```

#### 示例2：标准训练（推荐）
```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model s \
    --epochs 100 \
    --batch 16 \
    --device 0
```

#### 示例3：高精度训练
```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model m \
    --epochs 200 \
    --batch 8 \
    --imgsz 1280 \
    --device 0
```

#### 示例4：CPU训练（无GPU）
```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model n \
    --epochs 50 \
    --batch 4 \
    --device cpu
```

#### 示例5：继续训练
```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model s \
    --resume
```

### 训练过程监控

训练开始后，你会看到：

```
============================================================
验证数据集...
============================================================
✓ 训练集图片数量: 800
✓ 验证集图片数量: 200
✓ 类别数量: 3
✓ 类别名称: ['player', 'basketball', 'hoop']

============================================================
开始训练YOLOv8模型
============================================================
使用预训练模型: yolov8s.pt
训练参数:
  - 轮数: 100
  - 图像大小: 640
  - 批次大小: 16
  - 设备: 0

============================================================
训练中...
============================================================
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
  1/100      3.24G      1.234      2.345      1.123        156        640
  2/100      3.24G      1.123      2.123      1.045        156        640
  ...
```

**关键指标**：
- `box_loss`: 边界框损失（越小越好）
- `cls_loss`: 分类损失（越小越好）
- `dfl_loss`: 分布焦点损失（越小越好）

### 训练结果

训练完成后，模型保存在：
```
runs/basketball_detection/basketball_yolov8s/
├── weights/
│   ├── best.pt          # 最佳模型（验证集上表现最好）
│   └── last.pt          # 最后一轮模型
├── confusion_matrix.png  # 混淆矩阵
├── results.png           # 训练曲线
└── val_batch0_pred.jpg   # 验证集预测示例
```

---

## 模型评估

### 评估训练好的模型

```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --mode eval \
    --weights runs/basketball_detection/basketball_yolov8s/weights/best.pt
```

### 评估结果

```
============================================================
评估模型性能
============================================================

评估结果:
  mAP50: 0.8523        # 在IoU=0.5时的平均精度
  mAP50-95: 0.6234     # 在IoU=0.5-0.95的平均精度
  Precision: 0.8123    # 精确率
  Recall: 0.7856       # 召回率
```

### 评估指标解释

| 指标 | 说明 | 好的值 |
|------|------|--------|
| **mAP50** | IoU阈值0.5时的平均精度 | >0.80 |
| **mAP50-95** | IoU阈值0.5-0.95的平均精度 | >0.60 |
| **Precision** | 预测为正例中实际为正例的比例 | >0.75 |
| **Recall** | 实际正例中被正确预测的比例 | >0.75 |

**IoU（Intersection over Union）**：预测框和真实框的重叠程度

---

## 模型使用

### 1. 在检测脚本中使用

```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')

# 对图片进行检测
results = model('basketball_game.jpg')

# 显示结果
for result in results:
    boxes = result.boxes  # 边界框
    for box in boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        bbox = box.xyxy[0].cpu().numpy()
        
        # 获取类别名称
        class_name = model.names[class_id]  # player, basketball, 或 hoop
        
        print(f"检测到 {class_name}，置信度: {confidence:.2f}")
```

### 2. 对视频进行检测

```python
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')

# 对视频进行检测
results = model('basketball_video.mp4', save=True)
```

### 3. 实时摄像头检测

```python
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')

# 使用摄像头进行实时检测
results = model(source=0, show=True)  # 0表示默认摄像头
```

### 4. 集成到项目中

将训练好的模型复制到项目的模型目录：

```bash
# 复制最佳模型
cp runs/basketball_detection/basketball_yolov8s/weights/best.pt \
   ai_engine/models/basketball_custom.pt
```

然后在`basketball_detector.py`中使用：

```python
# 修改检测器初始化
detector = BasketballDetector(model_path="ai_engine/models/basketball_custom.pt")
```

---

## 模型导出

### 导出为ONNX格式（推荐）

```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --mode export \
    --weights runs/basketball_detection/basketball_yolov8s/weights/best.pt \
    --export-format onnx
```

### 支持的导出格式

| 格式 | 说明 | 使用场景 |
|------|------|---------|
| `onnx` | ONNX Runtime | 跨平台部署 |
| `torchscript` | PyTorch JIT | PyTorch环境 |
| `tflite` | TensorFlow Lite | 移动端、嵌入式 |
| `coreml` | Core ML | iOS设备 |
| `engine` | TensorRT | NVIDIA GPU加速 |

---

## 训练技巧和最佳实践

### 1. 数据质量比数量更重要

- ✅ 高质量标注（边界框精确）
- ✅ 多样化场景（室内、室外、不同光照）
- ✅ 不同角度和距离
- ❌ 模糊、遮挡严重的图片

### 2. 数据增强策略

训练脚本已内置以下增强：
- 色调、饱和度、明度调整
- 随机旋转（±10度）
- 平移和缩放
- 水平翻转
- 马赛克增强（4张图拼接）
- Mixup增强（图像混合）

### 3. 训练技巧

**初期训练（Epoch 1-30）**：
- 损失快速下降
- 可能出现过拟合迹象

**中期训练（Epoch 30-70）**：
- 损失平稳下降
- 注意观察验证集性能

**后期训练（Epoch 70-100+）**：
- 损失趋于稳定
- 如果验证集loss不再下降，可以提前停止

### 4. 防止过拟合

- 增加数据量
- 使用数据增强
- 适当降低训练轮数
- 使用较小的模型

### 5. 提高精度

- 增加训练轮数（200-300）
- 使用更大的模型（s→m→l）
- 提高图像分辨率（640→1280）
- 收集更多高质量数据
- 仔细检查和改进标注质量

---

## 常见问题

### Q1: 训练时显示"CUDA out of memory"

**解决方法**：
- 减小`--batch`参数（16→8→4）
- 减小`--imgsz`参数（640→416）
- 使用更小的模型（m→s→n）
- 使用`--device cpu`（会很慢）

### Q2: 训练速度很慢

**可能原因**：
1. 使用CPU训练：改用GPU (`--device 0`)
2. 批次太小：增大`--batch`
3. 图片分辨率过高：使用640x640

### Q3: mAP很低（<0.5）

**解决方法**：
1. 检查标注质量（是否准确）
2. 增加训练数据
3. 增加训练轮数
4. 检查类别平衡（每个类别样本是否充足）
5. 调整学习率或使用预训练权重

### Q4: 某个类别检测效果差

**解决方法**：
1. 增加该类别的样本数量
2. 确保该类别标注质量
3. 检查该类别是否有特殊情况（如球筐被遮挡）
4. 可以增加该类别的数据增强

### Q5: 如何判断训练是否成功？

**检查项**：
- ✅ 训练loss持续下降
- ✅ 验证loss稳定或下降
- ✅ mAP50 > 0.7
- ✅ Precision和Recall均衡（差距<0.1）
- ✅ 混淆矩阵对角线值高

### Q6: 能否使用已有的COCO预训练模型？

可以！YOLOv8训练时会自动下载并使用COCO预训练权重，这样可以：
- 加快收敛速度
- 需要更少的训练数据
- 获得更好的初始性能

### Q7: 如何处理类别不平衡？

如果某个类别样本很少：
1. 增加该类别的采集和标注
2. 使用数据增强
3. 调整类别权重（在配置中）
4. 使用focal loss

### Q8: 训练中断了怎么办？

使用`--resume`参数继续训练：
```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model s \
    --resume
```

---

## 进阶内容

### 超参数调优

YOLOv8支持自动超参数调优：

```python
from ultralytics import YOLO

model = YOLO('yolov8s.pt')
model.tune(
    data='my_basketball_config.yaml',
    epochs=30,
    iterations=300,
    optimizer='AdamW',
    plots=True,
    save=True
)
```

### 多GPU训练

```bash
python train_yolov8.py \
    --config my_basketball_config.yaml \
    --model s \
    --epochs 100 \
    --device 0,1,2,3  # 使用4个GPU
```

### 混合精度训练

自动启用，可加速训练：
```bash
# YOLOv8默认使用混合精度训练（FP16）
# 无需额外配置
```

---

## 参考资源

- **YOLOv8官方文档**: https://docs.ultralytics.com/
- **YOLOv8 GitHub**: https://github.com/ultralytics/ultralytics
- **标注工具LabelImg**: https://github.com/tzutalin/labelImg
- **在线标注Roboflow**: https://roboflow.com/

---

## 获取帮助

如果遇到问题：
1. 查看[常见问题](#常见问题)部分
2. 检查数据集格式和配置文件
3. 查看训练日志输出
4. 提交Issue到项目仓库

---

**祝你训练成功！** 🎯🏀
