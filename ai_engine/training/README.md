# YOLOv8训练模块

本目录包含训练自定义YOLOv8模型所需的所有脚本和配置文件。

## 📁 文件说明

### 核心文件
- **`train_yolov8.py`** - 主训练脚本
- **`dataset_config.yaml`** - 数据集配置模板
- **`dataset_utils.py`** - 数据集准备和验证工具

### 使用文档
- **`../docs/YOLOV8_TRAINING_GUIDE_CN.md`** - 完整中文训练指南

## 🚀 快速开始

### 1. 准备数据集

按照以下结构组织你的数据：

```
datasets/basketball/
├── images/
│   ├── train/   # 训练集图片
│   └── val/     # 验证集图片
└── labels/
    ├── train/   # 训练集标注（YOLO格式）
    └── val/     # 验证集标注
```

### 2. 验证数据集

```bash
python dataset_utils.py validate datasets/basketball
```

### 3. 配置训练参数

编辑 `dataset_config.yaml`：

```yaml
path: ./datasets/basketball
train: images/train
val: images/val

nc: 3
names:
  0: player
  1: basketball
  2: hoop
```

### 4. 开始训练

```bash
# 基础训练
python train_yolov8.py --config dataset_config.yaml --model n --epochs 100

# 使用GPU训练
python train_yolov8.py --config dataset_config.yaml --model s --epochs 100 --device 0

# 高精度训练
python train_yolov8.py --config dataset_config.yaml --model m --epochs 200 --batch 8
```

### 5. 评估模型

```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --mode eval \
    --weights runs/basketball_detection/basketball_yolov8n/weights/best.pt
```

### 6. 导出模型

```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --mode export \
    --weights runs/basketball_detection/basketball_yolov8n/weights/best.pt \
    --export-format onnx
```

## 📊 训练参数说明

| 参数 | 说明 | 默认值 | 推荐值 |
|------|------|-------|--------|
| `--config` | 数据集配置文件 | 必需 | - |
| `--model` | 模型大小(n/s/m/l/x) | n | n或s |
| `--epochs` | 训练轮数 | 100 | 100-300 |
| `--batch` | 批次大小 | 16 | 8-32 |
| `--imgsz` | 图像大小 | 640 | 640 |
| `--device` | 设备(0/cpu) | 自动 | 0 |

## 🛠️ 数据集工具

### 验证数据集

```bash
python dataset_utils.py validate /path/to/dataset
```

### 划分数据集

```bash
python dataset_utils.py split \
    /path/to/source \
    /path/to/output \
    --train 0.8 \
    --val 0.2
```

### 可视化标注

```bash
python dataset_utils.py visualize \
    image.jpg \
    label.txt \
    --output result.jpg
```

## 📚 详细文档

完整的训练教程请查看：[YOLOv8训练指南](../docs/YOLOV8_TRAINING_GUIDE_CN.md)

内容包括：
- 数据集准备详解
- 标注工具推荐
- 训练步骤详解
- 模型评估方法
- 常见问题解答
- 进阶技巧

## ⚡ 训练示例

### 示例1：快速训练（测试用）
```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --model n \
    --epochs 50 \
    --batch 16
```

### 示例2：标准训练（推荐）
```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --model s \
    --epochs 100 \
    --batch 16 \
    --device 0
```

### 示例3：高精度训练
```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --model m \
    --epochs 200 \
    --batch 8 \
    --imgsz 1280 \
    --device 0
```

## 📈 训练结果

训练完成后，结果保存在：
```
runs/basketball_detection/basketball_yolov8{model}/
├── weights/
│   ├── best.pt          # 最佳模型
│   └── last.pt          # 最后一轮模型
├── results.png          # 训练曲线
├── confusion_matrix.png # 混淆矩阵
└── val_batch*.jpg       # 验证集预测示例
```

## 🎯 使用训练好的模型

### Python代码

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')

# 预测
results = model('basketball_image.jpg')

# 显示结果
results[0].show()
```

### 集成到项目

```python
# 在basketball_detector.py中使用
from ai_engine.detection.basketball_detector import BasketballDetector

detector = BasketballDetector(
    model_path='runs/basketball_detection/basketball_yolov8s/weights/best.pt'
)
```

## ❓ 常见问题

### Q: 训练很慢怎么办？
A: 
1. 使用GPU训练 (`--device 0`)
2. 减小批次大小 (`--batch 8`)
3. 使用更小的模型 (`--model n`)

### Q: 内存不足？
A:
1. 减小批次大小 (`--batch 4`)
2. 减小图像大小 (`--imgsz 416`)
3. 使用更小的模型

### Q: 模型效果不好？
A:
1. 增加训练数据
2. 检查标注质量
3. 增加训练轮数
4. 使用更大的模型

## 📞 获取帮助

- 查看完整训练指南：`docs/YOLOV8_TRAINING_GUIDE_CN.md`
- 查看YOLOv8官方文档：https://docs.ultralytics.com/
- 提交Issue到项目仓库

---

**开始训练你的模型吧！** 🎯🏀
