"""
数据集验证脚本
用于检查YOLOv8数据集的完整性和正确性

使用方法:
    python validate_dataset.py --data configs/basketball_dataset.yaml
"""

import os
import yaml
from pathlib import Path
import argparse
from collections import defaultdict
import cv2


def validate_dataset(data_yaml_path):
    """
    验证YOLO格式数据集
    
    Args:
        data_yaml_path: 数据配置YAML文件路径
    """
    print("=" * 60)
    print("YOLOv8 数据集验证工具")
    print("=" * 60)
    
    # 读取配置文件
    if not os.path.exists(data_yaml_path):
        print(f"❌ 错误: 配置文件不存在: {data_yaml_path}")
        return False
    
    with open(data_yaml_path, 'r', encoding='utf-8') as f:
        data_config = yaml.safe_load(f)
    
    print(f"\n✓ 配置文件读取成功: {data_yaml_path}")
    
    # 检查必要字段
    required_fields = ['path', 'train', 'val', 'nc', 'names']
    for field in required_fields:
        if field not in data_config:
            print(f"❌ 错误: 配置文件缺少必要字段: {field}")
            return False
    
    print("✓ 配置文件字段完整")
    
    # 获取路径
    dataset_root = Path(data_config['path'])
    if not dataset_root.is_absolute():
        # 相对路径，转换为相对于YAML文件的路径
        yaml_dir = Path(data_yaml_path).parent
        dataset_root = (yaml_dir / dataset_root).resolve()
    
    print(f"\n数据集根目录: {dataset_root}")
    
    if not dataset_root.exists():
        print(f"❌ 错误: 数据集根目录不存在: {dataset_root}")
        return False
    
    print("✓ 数据集根目录存在")
    
    # 检查类别配置
    nc = data_config['nc']
    names = data_config['names']
    
    print(f"\n类别配置:")
    print(f"  类别数量: {nc}")
    print(f"  类别名称: {names}")
    
    if len(names) != nc:
        print(f"❌ 错误: 类别数量({nc})与类别名称数量({len(names)})不匹配")
        return False
    
    print("✓ 类别配置正确")
    
    # 检查数据集分割
    splits = {
        'train': data_config.get('train'),
        'val': data_config.get('val'),
        'test': data_config.get('test')
    }
    
    print(f"\n数据集分割:")
    stats = {}
    
    for split_name, split_path in splits.items():
        if split_path is None:
            continue
        
        print(f"\n  {split_name.upper()} 集:")
        
        # 图像和标签路径
        images_dir = dataset_root / split_path
        labels_dir = dataset_root / split_path.replace('images', 'labels')
        
        print(f"    图像目录: {images_dir}")
        print(f"    标签目录: {labels_dir}")
        
        if not images_dir.exists():
            print(f"    ❌ 图像目录不存在")
            continue
        
        if not labels_dir.exists():
            print(f"    ❌ 标签目录不存在")
            continue
        
        # 统计图像和标签
        image_files = list(images_dir.glob('*.jpg')) + \
                     list(images_dir.glob('*.jpeg')) + \
                     list(images_dir.glob('*.png'))
        
        label_files = list(labels_dir.glob('*.txt'))
        
        print(f"    图像数量: {len(image_files)}")
        print(f"    标签数量: {len(label_files)}")
        
        # 检查图像标签对应关系
        missing_labels = []
        missing_images = []
        
        for img_file in image_files:
            label_file = labels_dir / (img_file.stem + '.txt')
            if not label_file.exists():
                missing_labels.append(img_file.name)
        
        for label_file in label_files:
            img_found = False
            for ext in ['.jpg', '.jpeg', '.png']:
                img_file = images_dir / (label_file.stem + ext)
                if img_file.exists():
                    img_found = True
                    break
            if not img_found:
                missing_images.append(label_file.name)
        
        if missing_labels:
            print(f"    ⚠️  缺少标签文件: {len(missing_labels)} 个")
            if len(missing_labels) <= 5:
                for f in missing_labels:
                    print(f"       - {f}")
        
        if missing_images:
            print(f"    ⚠️  缺少图像文件: {len(missing_images)} 个")
            if len(missing_images) <= 5:
                for f in missing_images:
                    print(f"       - {f}")
        
        if not missing_labels and not missing_images:
            print("    ✓ 所有图像都有对应的标签")
        
        # 验证标签格式
        class_counts = defaultdict(int)
        invalid_labels = []
        
        for label_file in label_files[:100]:  # 抽样检查前100个
            try:
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) != 5:
                            invalid_labels.append(label_file.name)
                            break
                        
                        class_id = int(parts[0])
                        if class_id < 0 or class_id >= nc:
                            invalid_labels.append(label_file.name)
                            break
                        
                        class_counts[class_id] += 1
                        
                        # 检查坐标范围
                        coords = [float(x) for x in parts[1:]]
                        if any(c < 0 or c > 1 for c in coords):
                            invalid_labels.append(label_file.name)
                            break
            except Exception as e:
                invalid_labels.append(label_file.name)
        
        if invalid_labels:
            print(f"    ⚠️  无效标签文件: {len(invalid_labels)} 个")
            for f in invalid_labels[:5]:
                print(f"       - {f}")
        else:
            print("    ✓ 标签格式正确")
        
        # 统计类别分布
        if class_counts:
            print(f"    类别分布 (抽样):")
            for class_id, count in sorted(class_counts.items()):
                class_name = names[class_id] if isinstance(names, list) else names.get(class_id, f"class_{class_id}")
                print(f"       {class_name}: {count} 个目标")
        
        # 保存统计信息
        stats[split_name] = {
            'images': len(image_files),
            'labels': len(label_files),
            'missing_labels': len(missing_labels),
            'missing_images': len(missing_images),
            'invalid_labels': len(invalid_labels),
            'class_counts': dict(class_counts)
        }
    
    # 输出总结
    print("\n" + "=" * 60)
    print("验证总结:")
    print("=" * 60)
    
    total_images = sum(s['images'] for s in stats.values())
    total_labels = sum(s['labels'] for s in stats.values())
    total_issues = sum(s['missing_labels'] + s['missing_images'] + s['invalid_labels'] 
                       for s in stats.values())
    
    print(f"\n总图像数量: {total_images}")
    print(f"总标签数量: {total_labels}")
    print(f"总问题数量: {total_issues}")
    
    if total_issues == 0:
        print("\n✅ 数据集验证通过！可以开始训练。")
        return True
    else:
        print(f"\n⚠️  数据集存在 {total_issues} 个问题，建议修复后再训练。")
        return False


def check_sample_images(data_yaml_path, num_samples=5):
    """
    检查并显示样本图像
    
    Args:
        data_yaml_path: 数据配置文件路径
        num_samples: 样本数量
    """
    print("\n" + "=" * 60)
    print("样本图像检查")
    print("=" * 60)
    
    with open(data_yaml_path, 'r', encoding='utf-8') as f:
        data_config = yaml.safe_load(f)
    
    dataset_root = Path(data_config['path'])
    train_images = dataset_root / data_config['train']
    
    if not train_images.exists():
        print("训练图像目录不存在")
        return
    
    image_files = list(train_images.glob('*.jpg'))[:num_samples]
    
    print(f"\n检查 {len(image_files)} 个样本图像:")
    
    for img_file in image_files:
        img = cv2.imread(str(img_file))
        if img is not None:
            h, w = img.shape[:2]
            print(f"  {img_file.name}: {w}x{h} 像素")
        else:
            print(f"  {img_file.name}: ❌ 无法读取")


def main():
    parser = argparse.ArgumentParser(description='YOLOv8数据集验证工具')
    parser.add_argument('--data', type=str, required=True,
                        help='数据配置YAML文件路径')
    parser.add_argument('--check-images', action='store_true',
                        help='检查样本图像')
    parser.add_argument('--samples', type=int, default=5,
                        help='检查的样本图像数量')
    
    args = parser.parse_args()
    
    # 验证数据集
    success = validate_dataset(args.data)
    
    # 检查样本图像
    if args.check_images:
        check_sample_images(args.data, args.samples)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
