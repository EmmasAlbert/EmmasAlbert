# YOLOv8训练快速入门 🚀

## 你有标注好的数据集了吗？

如果你已经有了标注好的数据集（包含球员、篮球、球筐），按照以下步骤就可以训练自己的YOLOv8模型了！

---

## 📋 前提条件

✅ 已标注的数据集（YOLO格式）
✅ Python 3.10+
✅ 已安装ultralytics库：`pip install ultralytics`

---

## 🎯 三步开始训练

### 第一步：组织数据集

将你的数据集按照以下结构组织：

```
datasets/basketball/
├── images/
│   ├── train/          # 训练集图片（.jpg或.png）
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── val/            # 验证集图片
│       ├── img101.jpg
│       └── ...
└── labels/
    ├── train/          # 训练集标注（.txt，YOLO格式）
    │   ├── img001.txt
    │   ├── img002.txt
    │   └── ...
    └── val/            # 验证集标注
        ├── img101.txt
        └── ...
```

**标注文件格式**（每行一个目标）：
```
<class_id> <x_center> <y_center> <width> <height>
```

示例（img001.txt）：
```
0 0.512 0.345 0.156 0.423    # 球员
1 0.678 0.234 0.045 0.067    # 篮球
2 0.823 0.123 0.089 0.156    # 球筐
```

其中：
- `0` = player（球员）
- `1` = basketball（篮球）
- `2` = hoop（球筐）
- 所有坐标值都归一化到0-1之间

---

### 第二步：配置训练参数

编辑 `ai_engine/training/dataset_config.yaml`：

```yaml
# 修改为你的数据集路径
path: /path/to/your/datasets/basketball
train: images/train
val: images/val

nc: 3
names:
  0: player
  1: basketball
  2: hoop
```

---

### 第三步：开始训练

```bash
cd ai_engine/training

# 快速训练（测试用）
python train_yolov8.py \
    --config dataset_config.yaml \
    --model n \
    --epochs 50

# 推荐训练（GPU）
python train_yolov8.py \
    --config dataset_config.yaml \
    --model s \
    --epochs 100 \
    --device 0

# 高精度训练
python train_yolov8.py \
    --config dataset_config.yaml \
    --model m \
    --epochs 200 \
    --batch 8
```

**参数说明**：
- `--model n` : 使用nano模型（最快）
- `--model s` : 使用small模型（推荐）
- `--model m` : 使用medium模型（更高精度）
- `--epochs 100` : 训练100轮
- `--device 0` : 使用第一个GPU（使用CPU改为 `--device cpu`）

---

## 📊 训练过程

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
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss
  1/100    3.24G      1.234      2.345      1.123
  2/100    3.24G      1.123      2.123      1.045
  ...
```

**关键指标**：
- `box_loss`：边界框损失（越小越好）
- `cls_loss`：分类损失（越小越好）
- 这些值会随训练逐渐下降

---

## 🎉 训练完成

训练完成后，模型保存在：

```
runs/basketball_detection/basketball_yolov8s/
├── weights/
│   ├── best.pt          ← 这是你要的模型！
│   └── last.pt
├── results.png          ← 训练曲线图
├── confusion_matrix.png ← 混淆矩阵
└── val_batch*.jpg       ← 验证集预测示例
```

---

## 🧪 评估模型

```bash
python train_yolov8.py \
    --config dataset_config.yaml \
    --mode eval \
    --weights runs/basketball_detection/basketball_yolov8s/weights/best.pt
```

你会看到：

```
评估结果:
  mAP50: 0.8523        # 在IoU=0.5时的平均精度
  mAP50-95: 0.6234     # 在IoU=0.5-0.95的平均精度
  Precision: 0.8123    # 精确率
  Recall: 0.7856       # 召回率
```

**好的结果**：
- mAP50 > 0.80 ✅
- mAP50-95 > 0.60 ✅
- Precision和Recall都 > 0.75 ✅

---

## 💻 使用训练好的模型

### Python代码

```python
from ultralytics import YOLO

# 加载你训练的模型
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')

# 对图片进行检测
results = model('basketball_game.jpg')

# 显示结果
results[0].show()

# 或者获取检测详情
for result in results:
    boxes = result.boxes
    for box in boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        print(f"检测到 {class_name}，置信度: {confidence:.2f}")
```

### 视频检测

```python
# 对视频进行检测
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')
results = model('basketball_video.mp4', save=True)
```

### 实时摄像头检测

```python
# 使用摄像头实时检测
model = YOLO('runs/basketball_detection/basketball_yolov8s/weights/best.pt')
results = model(source=0, show=True)  # 0 = 默认摄像头
```

---

## 🔧 常见问题快速解决

### ❌ 错误："CUDA out of memory"

**解决**：减小批次大小
```bash
python train_yolov8.py ... --batch 8   # 或 4
```

### ❌ 训练很慢

**解决**：
1. 使用GPU：`--device 0`
2. 使用更小的模型：`--model n`
3. 减小图像大小：`--imgsz 416`

### ❌ mAP很低（<0.5）

**解决**：
1. 检查标注质量
2. 增加训练数据
3. 增加训练轮数：`--epochs 200`

---

## 📚 需要更多帮助？

查看完整文档：

- **[完整训练指南](docs/YOLOV8_TRAINING_GUIDE_CN.md)** - 10000字详细教程
- **[训练模块说明](ai_engine/training/README.md)** - 模块文档
- **标注工具推荐**：LabelImg、CVAT、Roboflow

---

## 🎯 快速命令参考

```bash
# 训练
python train_yolov8.py --config dataset_config.yaml --model s --epochs 100 --device 0

# 评估
python train_yolov8.py --config dataset_config.yaml --mode eval --weights runs/.../best.pt

# 导出
python train_yolov8.py --config dataset_config.yaml --mode export --weights runs/.../best.pt

# 验证数据集
python dataset_utils.py validate /path/to/dataset

# 可视化标注
python dataset_utils.py visualize image.jpg label.txt --output result.jpg
```

---

**开始训练你的模型吧！** 🚀🏀

有问题？查看 [完整训练指南](docs/YOLOV8_TRAINING_GUIDE_CN.md) 或提交Issue！
