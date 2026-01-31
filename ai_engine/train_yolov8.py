"""
YOLOv8 自定义模型训练脚本
用于训练篮球、球员、球筐检测模型

使用方法:
    python train_yolov8.py --data basketball.yaml --epochs 100 --img 640

作者: EmmasAlbert
"""

import os
import argparse
from pathlib import Path
from ultralytics import YOLO
import yaml
import torch


class YOLOv8Trainer:
    """YOLOv8训练器"""
    
    def __init__(self, 
                 model_size: str = 'n',
                 pretrained: bool = True,
                 device: str = None):
        """
        初始化训练器
        
        Args:
            model_size: 模型大小 (n/s/m/l/x)
            pretrained: 是否使用预训练权重
            device: 训练设备 (cpu/cuda/mps)
        """
        self.model_size = model_size
        self.pretrained = pretrained
        
        # 自动检测设备
        if device is None:
            if torch.cuda.is_available():
                self.device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = 'mps'
            else:
                self.device = 'cpu'
        else:
            self.device = device
        
        print(f"使用设备: {self.device}")
        
        # 加载模型
        model_name = f'yolov8{model_size}.pt' if pretrained else f'yolov8{model_size}.yaml'
        self.model = YOLO(model_name)
        print(f"加载模型: {model_name}")
    
    def train(self,
              data_config: str,
              epochs: int = 100,
              img_size: int = 640,
              batch_size: int = 16,
              project: str = 'runs/train',
              name: str = 'basketball_detector',
              patience: int = 50,
              save_period: int = 10,
              **kwargs):
        """
        训练模型
        
        Args:
            data_config: 数据配置文件路径 (YAML)
            epochs: 训练轮数
            img_size: 图像大小
            batch_size: 批次大小
            project: 项目保存路径
            name: 实验名称
            patience: 早停耐心值
            save_period: 模型保存周期
            **kwargs: 其他训练参数
        """
        print(f"\n{'='*60}")
        print(f"开始训练 YOLOv8{self.model_size} 模型")
        print(f"{'='*60}\n")
        
        # 训练参数
        train_args = {
            'data': data_config,
            'epochs': epochs,
            'imgsz': img_size,
            'batch': batch_size,
            'device': self.device,
            'project': project,
            'name': name,
            'patience': patience,
            'save_period': save_period,
            'plots': True,
            'verbose': True,
            **kwargs
        }
        
        # 显示训练配置
        print("训练配置:")
        for key, value in train_args.items():
            print(f"  {key}: {value}")
        print()
        
        # 开始训练
        results = self.model.train(**train_args)
        
        print(f"\n{'='*60}")
        print("训练完成!")
        print(f"{'='*60}\n")
        
        # 显示结果
        best_model_path = Path(project) / name / 'weights' / 'best.pt'
        last_model_path = Path(project) / name / 'weights' / 'last.pt'
        
        print(f"最佳模型保存在: {best_model_path}")
        print(f"最后模型保存在: {last_model_path}")
        
        return results
    
    def validate(self, data_config: str, model_path: str = None):
        """
        验证模型
        
        Args:
            data_config: 数据配置文件路径
            model_path: 模型路径（如果不提供，使用当前模型）
        """
        if model_path:
            model = YOLO(model_path)
        else:
            model = self.model
        
        print(f"\n{'='*60}")
        print("验证模型")
        print(f"{'='*60}\n")
        
        results = model.val(data=data_config, device=self.device)
        
        return results
    
    def export_model(self, 
                     model_path: str,
                     format: str = 'onnx',
                     img_size: int = 640,
                     simplify: bool = True):
        """
        导出模型
        
        Args:
            model_path: 模型路径
            format: 导出格式 (onnx/torchscript/coreml/etc)
            img_size: 图像大小
            simplify: 是否简化ONNX模型
        """
        model = YOLO(model_path)
        
        print(f"\n{'='*60}")
        print(f"导出模型为 {format.upper()} 格式")
        print(f"{'='*60}\n")
        
        export_path = model.export(
            format=format,
            imgsz=img_size,
            simplify=simplify
        )
        
        print(f"模型导出到: {export_path}")
        
        return export_path


def create_data_yaml(output_path: str,
                     train_path: str,
                     val_path: str,
                     test_path: str = None,
                     class_names: list = None):
    """
    创建数据配置YAML文件
    
    Args:
        output_path: 输出YAML文件路径
        train_path: 训练集路径
        val_path: 验证集路径
        test_path: 测试集路径（可选）
        class_names: 类别名称列表
    """
    if class_names is None:
        class_names = ['player', 'basketball', 'hoop']
    
    data_dict = {
        'path': str(Path(train_path).parent.parent),  # 数据集根目录
        'train': train_path,
        'val': val_path,
        'nc': len(class_names),  # 类别数量
        'names': class_names  # 类别名称
    }
    
    if test_path:
        data_dict['test'] = test_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_dict, f, allow_unicode=True, default_flow_style=False)
    
    print(f"数据配置文件已创建: {output_path}")
    print(f"类别数量: {len(class_names)}")
    print(f"类别名称: {class_names}")


def main():
    parser = argparse.ArgumentParser(description='YOLOv8 自定义模型训练')
    
    # 模型参数
    parser.add_argument('--model', type=str, default='n',
                        choices=['n', 's', 'm', 'l', 'x'],
                        help='模型大小 (n=nano, s=small, m=medium, l=large, x=xlarge)')
    parser.add_argument('--pretrained', action='store_true', default=True,
                        help='使用预训练权重')
    
    # 数据参数
    parser.add_argument('--data', type=str, required=True,
                        help='数据配置文件路径 (YAML)')
    
    # 训练参数
    parser.add_argument('--epochs', type=int, default=100,
                        help='训练轮数')
    parser.add_argument('--img', '--img-size', type=int, default=640,
                        help='图像大小')
    parser.add_argument('--batch', type=int, default=16,
                        help='批次大小')
    parser.add_argument('--device', type=str, default=None,
                        help='训练设备 (cpu/cuda/mps)')
    
    # 保存参数
    parser.add_argument('--project', type=str, default='runs/train',
                        help='项目保存路径')
    parser.add_argument('--name', type=str, default='basketball_detector',
                        help='实验名称')
    parser.add_argument('--patience', type=int, default=50,
                        help='早停耐心值')
    parser.add_argument('--save-period', type=int, default=10,
                        help='模型保存周期')
    
    # 优化参数
    parser.add_argument('--optimizer', type=str, default='SGD',
                        choices=['SGD', 'Adam', 'AdamW'],
                        help='优化器')
    parser.add_argument('--lr0', type=float, default=0.01,
                        help='初始学习率')
    parser.add_argument('--lrf', type=float, default=0.01,
                        help='最终学习率 (lr0 * lrf)')
    parser.add_argument('--momentum', type=float, default=0.937,
                        help='SGD动量/Adam beta1')
    parser.add_argument('--weight-decay', type=float, default=0.0005,
                        help='权重衰减')
    
    # 数据增强参数
    parser.add_argument('--hsv-h', type=float, default=0.015,
                        help='HSV色调增强')
    parser.add_argument('--hsv-s', type=float, default=0.7,
                        help='HSV饱和度增强')
    parser.add_argument('--hsv-v', type=float, default=0.4,
                        help='HSV明度增强')
    parser.add_argument('--degrees', type=float, default=0.0,
                        help='旋转角度')
    parser.add_argument('--translate', type=float, default=0.1,
                        help='平移')
    parser.add_argument('--scale', type=float, default=0.5,
                        help='缩放')
    parser.add_argument('--shear', type=float, default=0.0,
                        help='剪切')
    parser.add_argument('--perspective', type=float, default=0.0,
                        help='透视变换')
    parser.add_argument('--flipud', type=float, default=0.0,
                        help='上下翻转概率')
    parser.add_argument('--fliplr', type=float, default=0.5,
                        help='左右翻转概率')
    parser.add_argument('--mosaic', type=float, default=1.0,
                        help='马赛克增强概率')
    parser.add_argument('--mixup', type=float, default=0.0,
                        help='Mixup增强概率')
    
    # 其他选项
    parser.add_argument('--resume', type=str, default=None,
                        help='从检查点恢复训练')
    parser.add_argument('--validate', action='store_true',
                        help='训练后验证模型')
    parser.add_argument('--export', type=str, default=None,
                        choices=['onnx', 'torchscript', 'coreml', 'tflite'],
                        help='训练后导出模型格式')
    
    args = parser.parse_args()
    
    # 检查数据配置文件
    if not os.path.exists(args.data):
        print(f"错误: 数据配置文件不存在: {args.data}")
        print("\n请使用以下命令创建数据配置文件:")
        print("python train_yolov8.py --create-yaml")
        return
    
    # 创建训练器
    trainer = YOLOv8Trainer(
        model_size=args.model,
        pretrained=args.pretrained,
        device=args.device
    )
    
    # 准备训练参数
    train_kwargs = {
        'optimizer': args.optimizer,
        'lr0': args.lr0,
        'lrf': args.lrf,
        'momentum': args.momentum,
        'weight_decay': args.weight_decay,
        'hsv_h': args.hsv_h,
        'hsv_s': args.hsv_s,
        'hsv_v': args.hsv_v,
        'degrees': args.degrees,
        'translate': args.translate,
        'scale': args.scale,
        'shear': args.shear,
        'perspective': args.perspective,
        'flipud': args.flipud,
        'fliplr': args.fliplr,
        'mosaic': args.mosaic,
        'mixup': args.mixup,
    }
    
    if args.resume:
        train_kwargs['resume'] = args.resume
    
    # 训练模型
    results = trainer.train(
        data_config=args.data,
        epochs=args.epochs,
        img_size=args.img,
        batch_size=args.batch,
        project=args.project,
        name=args.name,
        patience=args.patience,
        save_period=args.save_period,
        **train_kwargs
    )
    
    # 训练后验证
    if args.validate:
        best_model = Path(args.project) / args.name / 'weights' / 'best.pt'
        if best_model.exists():
            trainer.validate(args.data, str(best_model))
    
    # 导出模型
    if args.export:
        best_model = Path(args.project) / args.name / 'weights' / 'best.pt'
        if best_model.exists():
            trainer.export_model(
                str(best_model),
                format=args.export,
                img_size=args.img
            )


if __name__ == '__main__':
    main()
