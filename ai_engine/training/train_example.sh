#!/bin/bash
# YOLOv8训练快速启动脚本示例

echo "========================================="
echo "YOLOv8篮球场景检测模型训练"
echo "========================================="
echo ""

# 检查参数
if [ "$#" -lt 1 ]; then
    echo "用法: ./train_example.sh <config_file> [model_size] [epochs]"
    echo ""
    echo "示例:"
    echo "  ./train_example.sh dataset_config.yaml"
    echo "  ./train_example.sh dataset_config.yaml s 100"
    echo ""
    exit 1
fi

CONFIG_FILE=$1
MODEL_SIZE=${2:-n}
EPOCHS=${3:-100}

echo "配置文件: $CONFIG_FILE"
echo "模型大小: yolov8$MODEL_SIZE"
echo "训练轮数: $EPOCHS"
echo ""

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python"
    exit 1
fi

# 检查ultralytics是否安装
python -c "import ultralytics" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "错误: 未安装ultralytics库"
    echo "请运行: pip install ultralytics"
    exit 1
fi

echo "开始训练..."
echo ""

# 执行训练
python train_yolov8.py \
    --config "$CONFIG_FILE" \
    --model "$MODEL_SIZE" \
    --epochs "$EPOCHS" \
    --batch 16 \
    --device 0

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ 训练完成！"
    echo "========================================="
    echo ""
    echo "模型保存位置: runs/basketball_detection/basketball_yolov8$MODEL_SIZE/weights/best.pt"
    echo ""
    echo "下一步:"
    echo "  1. 评估模型: python train_yolov8.py --config $CONFIG_FILE --mode eval --weights runs/basketball_detection/basketball_yolov8$MODEL_SIZE/weights/best.pt"
    echo "  2. 导出模型: python train_yolov8.py --config $CONFIG_FILE --mode export --weights runs/basketball_detection/basketball_yolov8$MODEL_SIZE/weights/best.pt"
else
    echo ""
    echo "========================================="
    echo "✗ 训练失败"
    echo "========================================="
    exit 1
fi
