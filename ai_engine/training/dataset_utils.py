"""
数据集准备和验证工具
"""
import os
import shutil
from pathlib import Path
from typing import Tuple, List
import random
import cv2
import yaml


class DatasetValidator:
    """数据集验证工具"""
    
    def __init__(self, dataset_path: str):
        """
        初始化验证器
        
        Args:
            dataset_path: 数据集根目录
        """
        self.dataset_path = Path(dataset_path)
        self.issues = []
        
    def validate(self) -> bool:
        """
        验证数据集
        
        Returns:
            是否通过验证
        """
        print("=" * 60)
        print("开始验证数据集...")
        print("=" * 60)
        
        # 检查目录结构
        self._check_structure()
        
        # 检查图片和标注配对
        self._check_image_label_pairs()
        
        # 检查标注格式
        self._check_label_format()
        
        # 检查类别分布
        self._check_class_distribution()
        
        # 显示结果
        self._show_results()
        
        return len(self.issues) == 0
    
    def _check_structure(self):
        """检查目录结构"""
        print("\n1. 检查目录结构...")
        
        required_dirs = [
            'images/train',
            'images/val',
            'labels/train',
            'labels/val'
        ]
        
        for dir_path in required_dirs:
            full_path = self.dataset_path / dir_path
            if not full_path.exists():
                self.issues.append(f"缺少目录: {dir_path}")
                print(f"  ✗ 缺少目录: {dir_path}")
            else:
                print(f"  ✓ 目录存在: {dir_path}")
    
    def _check_image_label_pairs(self):
        """检查图片和标注文件配对"""
        print("\n2. 检查图片和标注配对...")
        
        for split in ['train', 'val']:
            img_dir = self.dataset_path / 'images' / split
            label_dir = self.dataset_path / 'labels' / split
            
            if not img_dir.exists() or not label_dir.exists():
                continue
            
            # 获取所有图片
            images = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
            
            missing_labels = []
            for img_path in images:
                label_path = label_dir / f"{img_path.stem}.txt"
                if not label_path.exists():
                    missing_labels.append(img_path.name)
            
            if missing_labels:
                msg = f"{split}集中有{len(missing_labels)}张图片缺少标注文件"
                self.issues.append(msg)
                print(f"  ✗ {msg}")
                if len(missing_labels) <= 5:
                    for name in missing_labels:
                        print(f"    - {name}")
            else:
                print(f"  ✓ {split}集所有图片都有对应标注")
    
    def _check_label_format(self):
        """检查标注格式"""
        print("\n3. 检查标注格式...")
        
        invalid_labels = []
        
        for split in ['train', 'val']:
            label_dir = self.dataset_path / 'labels' / split
            
            if not label_dir.exists():
                continue
            
            label_files = list(label_dir.glob('*.txt'))
            
            for label_file in label_files:
                try:
                    with open(label_file, 'r') as f:
                        lines = f.readlines()
                        
                    for line_num, line in enumerate(lines, 1):
                        parts = line.strip().split()
                        if len(parts) != 5:
                            invalid_labels.append(
                                f"{label_file.name}:{line_num} - 格式错误（应为5个值）"
                            )
                            continue
                        
                        # 检查类别ID
                        class_id = int(parts[0])
                        if class_id < 0:
                            invalid_labels.append(
                                f"{label_file.name}:{line_num} - 类别ID为负数"
                            )
                        
                        # 检查坐标范围
                        for i, val in enumerate(parts[1:], 1):
                            coord = float(val)
                            if not (0 <= coord <= 1):
                                invalid_labels.append(
                                    f"{label_file.name}:{line_num} - 坐标超出范围[0,1]"
                                )
                                
                except Exception as e:
                    invalid_labels.append(f"{label_file.name} - 读取错误: {str(e)}")
        
        if invalid_labels:
            msg = f"发现{len(invalid_labels)}个标注格式问题"
            self.issues.append(msg)
            print(f"  ✗ {msg}")
            for issue in invalid_labels[:10]:  # 只显示前10个
                print(f"    - {issue}")
            if len(invalid_labels) > 10:
                print(f"    ... 还有{len(invalid_labels) - 10}个问题")
        else:
            print(f"  ✓ 所有标注格式正确")
    
    def _check_class_distribution(self):
        """检查类别分布"""
        print("\n4. 检查类别分布...")
        
        class_counts = {}
        
        for split in ['train', 'val']:
            label_dir = self.dataset_path / 'labels' / split
            
            if not label_dir.exists():
                continue
            
            print(f"\n  {split}集:")
            split_counts = {}
            
            for label_file in label_dir.glob('*.txt'):
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            split_counts[class_id] = split_counts.get(class_id, 0) + 1
            
            for class_id in sorted(split_counts.keys()):
                count = split_counts[class_id]
                print(f"    类别 {class_id}: {count} 个实例")
            
            class_counts[split] = split_counts
    
    def _show_results(self):
        """显示验证结果"""
        print("\n" + "=" * 60)
        if self.issues:
            print(f"验证失败！发现 {len(self.issues)} 个问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("✓ 数据集验证通过！")
        print("=" * 60)


class DatasetSplitter:
    """数据集划分工具"""
    
    @staticmethod
    def split_dataset(
        source_dir: str,
        output_dir: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.2,
        test_ratio: float = 0.0,
        seed: int = 42
    ):
        """
        将数据集划分为训练集、验证集和测试集
        
        Args:
            source_dir: 源数据目录（包含images和labels子目录）
            output_dir: 输出目录
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            test_ratio: 测试集比例
            seed: 随机种子
        """
        print("=" * 60)
        print("划分数据集...")
        print("=" * 60)
        
        source_path = Path(source_dir)
        output_path = Path(output_dir)
        
        # 检查比例和
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.01:
            raise ValueError("训练集、验证集和测试集比例之和必须为1.0")
        
        # 创建输出目录
        for split in ['train', 'val', 'test']:
            (output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
            (output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
        # 获取所有图片
        images = list(source_path.glob('images/**/*.jpg')) + \
                list(source_path.glob('images/**/*.png'))
        
        print(f"找到 {len(images)} 张图片")
        
        # 随机打乱
        random.seed(seed)
        random.shuffle(images)
        
        # 计算划分点
        n_total = len(images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        # 划分数据
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:] if test_ratio > 0 else []
        
        print(f"训练集: {len(train_images)} 张")
        print(f"验证集: {len(val_images)} 张")
        print(f"测试集: {len(test_images)} 张")
        
        # 复制文件
        splits = {
            'train': train_images,
            'val': val_images,
            'test': test_images
        }
        
        for split_name, split_images in splits.items():
            if not split_images:
                continue
            
            print(f"\n复制{split_name}集...")
            for img_path in split_images:
                # 复制图片
                dst_img = output_path / 'images' / split_name / img_path.name
                shutil.copy2(img_path, dst_img)
                
                # 复制标注
                label_path = source_path / 'labels' / f"{img_path.stem}.txt"
                if label_path.exists():
                    dst_label = output_path / 'labels' / split_name / f"{img_path.stem}.txt"
                    shutil.copy2(label_path, dst_label)
        
        print("\n" + "=" * 60)
        print("✓ 数据集划分完成！")
        print("=" * 60)


def visualize_annotations(
    image_path: str,
    label_path: str,
    class_names: List[str] = None,
    output_path: str = None
):
    """
    可视化标注
    
    Args:
        image_path: 图片路径
        label_path: 标注文件路径
        class_names: 类别名称列表
        output_path: 输出路径（如果为None则显示）
    """
    if class_names is None:
        class_names = ['player', 'basketball', 'hoop']
    
    # 读取图片
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    # 读取标注
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            
            class_id = int(parts[0])
            x_center, y_center, width, height = map(float, parts[1:])
            
            # 转换为像素坐标
            x1 = int((x_center - width / 2) * w)
            y1 = int((y_center - height / 2) * h)
            x2 = int((x_center + width / 2) * w)
            y2 = int((y_center + height / 2) * h)
            
            # 绘制边界框
            color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)][class_id % 3]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            label = class_names[class_id] if class_id < len(class_names) else f"Class {class_id}"
            cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # 保存或显示
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"可视化结果保存至: {output_path}")
    else:
        cv2.imshow('Annotations', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据集准备工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证数据集')
    validate_parser.add_argument('dataset_path', help='数据集路径')
    
    # 划分命令
    split_parser = subparsers.add_parser('split', help='划分数据集')
    split_parser.add_argument('source_dir', help='源数据目录')
    split_parser.add_argument('output_dir', help='输出目录')
    split_parser.add_argument('--train', type=float, default=0.8, help='训练集比例')
    split_parser.add_argument('--val', type=float, default=0.2, help='验证集比例')
    split_parser.add_argument('--test', type=float, default=0.0, help='测试集比例')
    
    # 可视化命令
    viz_parser = subparsers.add_parser('visualize', help='可视化标注')
    viz_parser.add_argument('image_path', help='图片路径')
    viz_parser.add_argument('label_path', help='标注文件路径')
    viz_parser.add_argument('--output', help='输出路径')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        validator = DatasetValidator(args.dataset_path)
        validator.validate()
        
    elif args.command == 'split':
        DatasetSplitter.split_dataset(
            args.source_dir,
            args.output_dir,
            args.train,
            args.val,
            args.test
        )
        
    elif args.command == 'visualize':
        visualize_annotations(args.image_path, args.label_path, output_path=args.output)
        
    else:
        parser.print_help()
