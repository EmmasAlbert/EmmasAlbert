"""
模型验证和测试脚本
用于评估训练好的YOLOv8模型性能

使用方法:
    # 验证模型
    python validate_model.py --model runs/train/basketball/weights/best.pt \
                            --data configs/basketball_dataset.yaml
    
    # 测试单张图像
    python validate_model.py --model best.pt --source test.jpg
    
    # 测试视频
    python validate_model.py --model best.pt --source video.mp4
"""

import argparse
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np


class ModelValidator:
    """模型验证器"""
    
    def __init__(self, model_path: str):
        """
        初始化验证器
        
        Args:
            model_path: 模型路径
        """
        self.model = YOLO(model_path)
        print(f"✓ 模型加载成功: {model_path}")
    
    def validate_on_dataset(self, data_config: str, split: str = 'val'):
        """
        在数据集上验证模型
        
        Args:
            data_config: 数据配置文件路径
            split: 数据集分割 (val/test)
        """
        print("\n" + "=" * 60)
        print(f"在 {split.upper()} 集上验证模型")
        print("=" * 60)
        
        # 运行验证
        results = self.model.val(
            data=data_config,
            split=split,
            plots=True,
            save_json=True
        )
        
        # 打印结果
        print("\n验证结果:")
        print("=" * 60)
        
        # 主要指标
        metrics = results.box
        print(f"\n整体性能:")
        print(f"  mAP50:     {metrics.map50:.4f}")
        print(f"  mAP50-95:  {metrics.map:.4f}")
        print(f"  Precision: {metrics.mp:.4f}")
        print(f"  Recall:    {metrics.mr:.4f}")
        
        # 各类别性能
        if hasattr(metrics, 'maps'):
            print(f"\n各类别性能:")
            class_names = self.model.names
            for i, (ap50, ap) in enumerate(zip(metrics.ap50, metrics.ap)):
                class_name = class_names[i] if isinstance(class_names, list) else class_names.get(i, f'class_{i}')
                print(f"  {class_name}:")
                print(f"    mAP50:    {ap50:.4f}")
                print(f"    mAP50-95: {ap:.4f}")
        
        return results
    
    def test_image(self, image_path: str, conf: float = 0.25, save: bool = True):
        """
        测试单张图像
        
        Args:
            image_path: 图像路径
            conf: 置信度阈值
            save: 是否保存结果
        """
        print(f"\n测试图像: {image_path}")
        
        # 预测
        results = self.model(
            image_path,
            conf=conf,
            save=save,
            show_labels=True,
            show_conf=True
        )
        
        # 打印检测结果
        result = results[0]
        
        if len(result.boxes) == 0:
            print("  未检测到任何目标")
        else:
            print(f"  检测到 {len(result.boxes)} 个目标:")
            
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                
                print(f"    - {class_name}: {conf:.2f} @ [{bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f}]")
        
        return results
    
    def test_video(self, video_path: str, conf: float = 0.25, save: bool = True):
        """
        测试视频
        
        Args:
            video_path: 视频路径
            conf: 置信度阈值
            save: 是否保存结果
        """
        print(f"\n测试视频: {video_path}")
        
        # 处理视频
        results = self.model(
            video_path,
            conf=conf,
            save=save,
            stream=True
        )
        
        # 统计信息
        total_frames = 0
        total_detections = 0
        
        for result in results:
            total_frames += 1
            total_detections += len(result.boxes)
            
            if total_frames % 30 == 0:  # 每30帧打印一次
                print(f"  已处理 {total_frames} 帧, 平均每帧检测 {total_detections/total_frames:.1f} 个目标")
        
        print(f"\n视频处理完成:")
        print(f"  总帧数: {total_frames}")
        print(f"  总检测数: {total_detections}")
        print(f"  平均每帧: {total_detections/total_frames:.2f} 个目标")
        
        return results
    
    def test_directory(self, dir_path: str, conf: float = 0.25, save: bool = True):
        """
        测试目录中的所有图像
        
        Args:
            dir_path: 目录路径
            conf: 置信度阈值
            save: 是否保存结果
        """
        dir_path = Path(dir_path)
        image_files = list(dir_path.glob('*.jpg')) + \
                     list(dir_path.glob('*.jpeg')) + \
                     list(dir_path.glob('*.png'))
        
        print(f"\n测试目录: {dir_path}")
        print(f"找到 {len(image_files)} 个图像文件")
        
        # 批量预测
        results = self.model(
            [str(f) for f in image_files],
            conf=conf,
            save=save
        )
        
        # 统计
        total_detections = sum(len(r.boxes) for r in results)
        images_with_detections = sum(1 for r in results if len(r.boxes) > 0)
        
        print(f"\n测试结果:")
        print(f"  有检测结果的图像: {images_with_detections}/{len(image_files)}")
        print(f"  总检测数: {total_detections}")
        print(f"  平均每图: {total_detections/len(image_files):.2f} 个目标")
        
        return results
    
    def benchmark_speed(self, img_size: int = 640, num_iterations: int = 100):
        """
        性能基准测试
        
        Args:
            img_size: 图像大小
            num_iterations: 迭代次数
        """
        import time
        
        print(f"\n性能基准测试:")
        print(f"  图像大小: {img_size}x{img_size}")
        print(f"  迭代次数: {num_iterations}")
        
        # 创建随机图像
        dummy_img = np.random.randint(0, 255, (img_size, img_size, 3), dtype=np.uint8)
        
        # 预热
        for _ in range(10):
            _ = self.model(dummy_img, verbose=False)
        
        # 计时
        start_time = time.time()
        for _ in range(num_iterations):
            _ = self.model(dummy_img, verbose=False)
        end_time = time.time()
        
        # 计算统计
        total_time = end_time - start_time
        avg_time = total_time / num_iterations
        fps = 1.0 / avg_time
        
        print(f"\n结果:")
        print(f"  总时间: {total_time:.2f} 秒")
        print(f"  平均延迟: {avg_time*1000:.2f} 毫秒")
        print(f"  FPS: {fps:.2f}")


def main():
    parser = argparse.ArgumentParser(description='YOLOv8模型验证和测试工具')
    
    # 必需参数
    parser.add_argument('--model', type=str, required=True,
                        help='模型路径')
    
    # 验证选项
    parser.add_argument('--data', type=str,
                        help='数据配置文件（用于验证）')
    parser.add_argument('--split', type=str, default='val',
                        choices=['val', 'test'],
                        help='数据集分割')
    
    # 测试选项
    parser.add_argument('--source', type=str,
                        help='测试源（图像/视频/目录）')
    parser.add_argument('--conf', type=float, default=0.25,
                        help='置信度阈值')
    parser.add_argument('--save', action='store_true', default=True,
                        help='保存结果')
    
    # 性能测试
    parser.add_argument('--benchmark', action='store_true',
                        help='运行性能基准测试')
    parser.add_argument('--img-size', type=int, default=640,
                        help='基准测试图像大小')
    
    args = parser.parse_args()
    
    # 创建验证器
    validator = ModelValidator(args.model)
    
    # 数据集验证
    if args.data:
        validator.validate_on_dataset(args.data, args.split)
    
    # 测试源
    if args.source:
        source_path = Path(args.source)
        
        if source_path.is_file():
            # 检查是图像还是视频
            if source_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                validator.test_image(args.source, args.conf, args.save)
            elif source_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                validator.test_video(args.source, args.conf, args.save)
            else:
                print(f"不支持的文件格式: {source_path.suffix}")
        elif source_path.is_dir():
            validator.test_directory(args.source, args.conf, args.save)
        else:
            print(f"源不存在: {args.source}")
    
    # 性能基准测试
    if args.benchmark:
        validator.benchmark_speed(args.img_size)
    
    # 如果没有指定任何操作，显示帮助
    if not args.data and not args.source and not args.benchmark:
        parser.print_help()


if __name__ == '__main__':
    main()
