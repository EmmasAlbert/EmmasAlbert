# YOLOv8训练快速入门示例

本文档提供一个简单的端到端示例，帮助您快速上手YOLOv8模型训练。

## 📋 前置条件

- Python 3.10+
- 已安装项目依赖（`pip install -r backend/requirements.txt`）
- 准备好的标注数据集

## 🎯 完整训练示例

### 步骤1: 准备数据集

假设您已经标注好了数据，组织成以下结构：

```
my_basketball_dataset/
├── images/
│   ├── train/          # 1000张训练图像
│   ├── val/            # 200张验证图像
│   └── test/           # 100张测试图像（可选）
└── labels/
    ├── train/          # 训练标注
    ├── val/            # 验证标注
    └── test/           # 测试标注（可选）
```

**标注文件格式示例** (img_001.txt):
```
0 0.5 0.4 0.2 0.6    # player: 中心(0.5,0.4), 大小(0.2x0.6)
1 0.7 0.3 0.05 0.05  # basketball: 中心(0.7,0.3), 大小(0.05x0.05)
2 0.8 0.2 0.15 0.1   # hoop: 中心(0.8,0.2), 大小(0.15x0.1)
```

### 步骤2: 创建数据配置文件

创建 `my_dataset.yaml`:

```yaml
path: /path/to/my_basketball_dataset
train: images/train
val: images/val
test: images/test

nc: 3
names:
  0: player
  1: basketball
  2: hoop
```

### 步骤3: 验证数据集

```bash
cd ai_engine
python validate_dataset.py --data my_dataset.yaml
```

### 步骤4: 开始训练

```bash
# 快速训练（nano模型）
python train_yolov8.py \
    --model n \
    --data my_dataset.yaml \
    --epochs 50 \
    --img 640 \
    --batch 16

# 标准训练（small模型）
python train_yolov8.py \
    --model s \
    --data my_dataset.yaml \
    --epochs 100 \
    --img 640 \
    --batch 16
```

### 步骤5: 验证模型

```bash
python validate_model.py \
    --model runs/train/basketball/weights/best.pt \
    --data my_dataset.yaml
```

### 步骤6: 测试模型

```bash
# 测试图像
python validate_model.py \
    --model runs/train/basketball/weights/best.pt \
    --source test_image.jpg

# 测试视频
python validate_model.py \
    --model runs/train/basketball/weights/best.pt \
    --source basketball_game.mp4
```

## 📚 更多信息

查看完整文档：
- [YOLOv8训练完整指南](YOLOV8_TRAINING_GUIDE.md)
- [AI引擎说明](../ai_engine/README.md)

---

**作者**: EmmasAlbert  
**版本**: 1.0
