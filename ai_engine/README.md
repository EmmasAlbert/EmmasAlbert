# YOLOv8 训练模块

本目录包含用于训练自定义YOLOv8篮球检测模型的所有工具和配置。

## 📁 目录结构

```
ai_engine/
├── train_yolov8.py          # 主训练脚本
├── validate_dataset.py      # 数据集验证工具
├── validate_model.py        # 模型验证和测试工具
├── configs/                 # 配置文件目录
│   ├── basketball_dataset.yaml    # 数据集配置示例
│   └── train_config.yaml          # 训练参数配置示例
├── detection/               # 检测模块
│   └── basketball_detector.py
└── pose_estimation/         # 姿态估计模块
    └── pose_estimator.py
```

## 🚀 快速开始

### 1. 准备数据集

按照YOLO格式组织您的数据集:

```
datasets/basketball/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

### 2. 配置数据集

编辑 `configs/basketball_dataset.yaml`:

```yaml
path: /path/to/datasets/basketball
train: images/train
val: images/val
test: images/test

nc: 3
names:
  0: player
  1: basketball
  2: hoop
```

### 3. 验证数据集

```bash
python validate_dataset.py --data configs/basketball_dataset.yaml
```

### 4. 开始训练

```bash
# 快速训练（nano模型）
python train_yolov8.py \
    --model n \
    --data configs/basketball_dataset.yaml \
    --epochs 100 \
    --img 640 \
    --batch 16 \
    --name basketball_v1

# 高精度训练（medium模型）
python train_yolov8.py \
    --model m \
    --data configs/basketball_dataset.yaml \
    --epochs 200 \
    --img 1280 \
    --batch 8 \
    --name basketball_v2
```

### 5. 验证模型

```bash
# 在验证集上评估
python validate_model.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --data configs/basketball_dataset.yaml

# 测试单张图像
python validate_model.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --source test.jpg

# 测试视频
python validate_model.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --source video.mp4

# 性能基准测试
python validate_model.py \
    --model runs/train/basketball_v1/weights/best.pt \
    --benchmark
```

## 📖 详细文档

请查看 [YOLOv8训练完整指南](../docs/YOLOV8_TRAINING_GUIDE.md) 获取详细的训练说明。

## 🔧 主要脚本说明

### train_yolov8.py

YOLOv8模型训练脚本，支持：
- 多种模型大小 (n/s/m/l/x)
- 自定义训练参数
- 数据增强配置
- 多GPU训练
- 训练恢复
- 模型导出

**主要参数：**
```bash
--model: 模型大小 (n/s/m/l/x)
--data: 数据配置文件
--epochs: 训练轮数
--img: 图像大小
--batch: 批次大小
--device: 训练设备
```

### validate_dataset.py

数据集验证工具，检查：
- 数据集结构
- 标注文件格式
- 图像标签对应关系
- 类别分布
- 坐标范围

### validate_model.py

模型验证和测试工具，支持：
- 数据集评估
- 单图测试
- 视频测试
- 批量测试
- 性能基准测试

## 📊 训练监控

训练过程中生成的文件：

```
runs/train/basketball_v1/
├── weights/
│   ├── best.pt          # 最佳模型
│   └── last.pt          # 最后检查点
├── results.png          # 训练曲线
├── confusion_matrix.png # 混淆矩阵
├── F1_curve.png         # F1曲线
├── PR_curve.png         # PR曲线
└── args.yaml            # 训练参数
```

## 🎯 性能指标

主要评估指标：
- **mAP50**: IoU@0.5的平均精度
- **mAP50-95**: IoU@0.5:0.95的平均精度
- **Precision**: 精确率
- **Recall**: 召回率
- **F1-Score**: F1分数

## 💡 最佳实践

1. **数据质量优先**
   - 确保标注准确
   - 数据分布均衡
   - 每类至少1000+样本

2. **合理选择模型**
   - 实时应用: YOLOv8n/s
   - 平衡性能: YOLOv8m
   - 高精度: YOLOv8l/x

3. **训练策略**
   - 使用预训练权重
   - 适当的数据增强
   - 监控验证指标
   - 早停避免过拟合

4. **超参数调优**
   - 学习率: 0.001-0.01
   - 批次大小: 根据GPU调整
   - 图像大小: 640/1280

## 🐛 常见问题

### 显存不足
```bash
# 减小批次大小
--batch 8

# 减小图像大小
--img 416

# 使用更小的模型
--model n
```

### 训练不收敛
```bash
# 降低学习率
--lr0 0.001

# 增加训练轮数
--epochs 200

# 检查数据集质量
python validate_dataset.py --data your_data.yaml
```

### 过拟合
```bash
# 增加数据增强
--mosaic 1.0 --mixup 0.15

# 早停
--patience 50

# 正则化
--weight-decay 0.001
```

## 📞 技术支持

- [完整训练指南](../docs/YOLOV8_TRAINING_GUIDE.md)
- [GitHub Issues](https://github.com/EmmasAlbert/EmmasAlbert/issues)
- [YOLOv8官方文档](https://docs.ultralytics.com/)

## 📝 示例

更多训练示例请参考：
- [快速开始示例](../docs/YOLOV8_TRAINING_GUIDE.md#快速开始训练)
- [高级配置示例](../docs/YOLOV8_TRAINING_GUIDE.md#完整训练示例)

---

**作者**: EmmasAlbert  
**版本**: 1.0  
**更新**: 2024-01-31
