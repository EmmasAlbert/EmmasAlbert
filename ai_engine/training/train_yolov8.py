"""
YOLOv8 自定义模型训练脚本
用于训练篮球场景检测模型（球员、篮球、球筐）
"""
import os
import yaml
from pathlib import Path
from ultralytics import YOLO
import torch
import argparse


class BasketballYOLOTrainer:
    """篮球场景YOLOv8训练器"""
    
    def __init__(self, config_path: str):
        """
        初始化训练器
        
        Args:
            config_path: 数据集配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    
    def validate_dataset(self):
        """验证数据集结构"""
        print("=" * 60)
        print("验证数据集...")
        print("=" * 60)
        
        # 检查必要的路径
        train_path = Path(self.config['train'])
        val_path = Path(self.config['val'])
        
        if not train_path.exists():
            raise FileNotFoundError(f"训练集路径不存在: {train_path}")
        if not val_path.exists():
            raise FileNotFoundError(f"验证集路径不存在: {val_path}")
        
        # 统计数据集
        train_images = list(train_path.glob('**/*.jpg')) + list(train_path.glob('**/*.png'))
        val_images = list(val_path.glob('**/*.jpg')) + list(val_path.glob('**/*.png'))
        
        print(f"✓ 训练集图片数量: {len(train_images)}")
        print(f"✓ 验证集图片数量: {len(val_images)}")
        print(f"✓ 类别数量: {self.config['nc']}")
        print(f"✓ 类别名称: {self.config['names']}")
        print()
        
        return True
    
    def train(
        self,
        model_size: str = 'n',
        epochs: int = 100,
        imgsz: int = 640,
        batch: int = 16,
        device: str = '0',
        resume: bool = False,
        **kwargs
    ):
        """
        训练YOLOv8模型
        
        Args:
            model_size: 模型大小 (n, s, m, l, x)
            epochs: 训练轮数
            imgsz: 输入图像大小
            batch: 批次大小
            device: 设备 (cpu, 0, 0,1,2,3等)
            resume: 是否继续训练
            **kwargs: 其他训练参数
        """
        print("=" * 60)
        print("开始训练YOLOv8模型")
        print("=" * 60)
        
        # 验证数据集
        self.validate_dataset()
        
        # 选择预训练模型
        model_name = f"yolov8{model_size}.pt"
        print(f"使用预训练模型: {model_name}")
        print(f"训练参数:")
        print(f"  - 轮数: {epochs}")
        print(f"  - 图像大小: {imgsz}")
        print(f"  - 批次大小: {batch}")
        print(f"  - 设备: {device}")
        print()
        
        # 加载模型
        model = YOLO(model_name)
        
        # 设置训练参数
        training_args = {
            'data': self.config_path,
            'epochs': epochs,
            'imgsz': imgsz,
            'batch': batch,
            'device': device,
            'project': 'runs/basketball_detection',
            'name': f'basketball_yolov8{model_size}',
            'exist_ok': True,
            'resume': resume,
            'verbose': True,
            # 数据增强参数
            'hsv_h': 0.015,  # 色调增强
            'hsv_s': 0.7,    # 饱和度增强
            'hsv_v': 0.4,    # 明度增强
            'degrees': 10,   # 旋转角度
            'translate': 0.1,  # 平移
            'scale': 0.5,    # 缩放
            'flipud': 0.0,   # 上下翻转
            'fliplr': 0.5,   # 左右翻转
            'mosaic': 1.0,   # 马赛克增强
            'mixup': 0.1,    # 混合增强
        }
        
        # 合并其他参数
        training_args.update(kwargs)
        
        # 开始训练
        print("=" * 60)
        print("训练中...")
        print("=" * 60)
        
        results = model.train(**training_args)
        
        print()
        print("=" * 60)
        print("训练完成！")
        print("=" * 60)
        
        return results
    
    def evaluate(self, model_path: str):
        """
        评估模型性能
        
        Args:
            model_path: 训练好的模型路径
        """
        print("=" * 60)
        print("评估模型性能")
        print("=" * 60)
        
        model = YOLO(model_path)
        
        # 在验证集上评估
        metrics = model.val(data=self.config_path)
        
        print()
        print("评估结果:")
        print(f"  mAP50: {metrics.box.map50:.4f}")
        print(f"  mAP50-95: {metrics.box.map:.4f}")
        print(f"  Precision: {metrics.box.mp:.4f}")
        print(f"  Recall: {metrics.box.mr:.4f}")
        print()
        
        return metrics
    
    def export_model(self, model_path: str, format: str = 'onnx'):
        """
        导出模型到其他格式
        
        Args:
            model_path: 训练好的模型路径
            format: 导出格式 (onnx, torchscript, tflite等)
        """
        print("=" * 60)
        print(f"导出模型为 {format.upper()} 格式")
        print("=" * 60)
        
        model = YOLO(model_path)
        export_path = model.export(format=format)
        
        print(f"✓ 模型已导出至: {export_path}")
        print()
        
        return export_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='YOLOv8 篮球场景训练脚本')
    
    # 必需参数
    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help='数据集配置文件路径 (YAML格式)'
    )
    
    # 训练参数
    parser.add_argument(
        '--model',
        type=str,
        default='n',
        choices=['n', 's', 'm', 'l', 'x'],
        help='模型大小: n(nano), s(small), m(medium), l(large), x(xlarge)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=100,
        help='训练轮数'
    )
    parser.add_argument(
        '--imgsz',
        type=int,
        default=640,
        help='输入图像大小'
    )
    parser.add_argument(
        '--batch',
        type=int,
        default=16,
        help='批次大小'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='0' if torch.cuda.is_available() else 'cpu',
        help='训练设备 (cpu, 0, 0,1,2,3等)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='继续之前的训练'
    )
    
    # 模式选择
    parser.add_argument(
        '--mode',
        type=str,
        default='train',
        choices=['train', 'eval', 'export'],
        help='运行模式: train(训练), eval(评估), export(导出)'
    )
    parser.add_argument(
        '--weights',
        type=str,
        help='模型权重路径 (用于评估或导出)'
    )
    parser.add_argument(
        '--export-format',
        type=str,
        default='onnx',
        help='导出格式 (onnx, torchscript, tflite等)'
    )
    
    args = parser.parse_args()
    
    # 创建训练器
    trainer = BasketballYOLOTrainer(args.config)
    
    # 根据模式执行不同操作
    if args.mode == 'train':
        # 训练模型
        results = trainer.train(
            model_size=args.model,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            resume=args.resume
        )
        
        print("\n训练完成！模型保存在: runs/basketball_detection/")
        print("可以使用以下命令评估模型:")
        print(f"python train_yolov8.py --config {args.config} --mode eval --weights runs/basketball_detection/basketball_yolov8{args.model}/weights/best.pt")
        
    elif args.mode == 'eval':
        # 评估模型
        if not args.weights:
            raise ValueError("评估模式需要指定 --weights 参数")
        
        trainer.evaluate(args.weights)
        
    elif args.mode == 'export':
        # 导出模型
        if not args.weights:
            raise ValueError("导出模式需要指定 --weights 参数")
        
        trainer.export_model(args.weights, args.export_format)


if __name__ == '__main__':
    main()
