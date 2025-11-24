#!/usr/bin/env python
"""
启动脚本 - YOLOv8篮球训练辅助系统
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import app
from utils.config_loader import load_config
from utils.logger import setup_logger

def main():
    """主函数"""
    # 设置日志
    logger = setup_logger('main', log_file='logs/system.log')
    logger.info("="*60)
    logger.info("🏀 YOLOv8篮球训练辅助系统启动")
    logger.info("="*60)
    
    # 加载配置
    config = load_config()
    
    # 创建必要的目录
    directories = [
        'data/raw',
        'data/processed',
        'data/annotations',
        'models',
        'logs',
        'outputs/videos',
        'outputs/reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✓ 创建目录: {directory}")
    
    # 显示配置信息
    logger.info(f"系统名称: {config['system']['name']}")
    logger.info(f"版本: {config['system']['version']}")
    logger.info(f"作者: {config['system']['author']}")
    logger.info(f"服务器地址: {config['server']['host']}:{config['server']['port']}")
    
    # 启动Flask应用
    logger.info("-"*60)
    logger.info("🚀 启动Web服务器...")
    logger.info(f"📱 请在浏览器中访问: http://localhost:{config['server']['port']}")
    logger.info("-"*60)
    
    try:
        app.run(
            host=config['server']['host'],
            port=config['server']['port'],
            debug=config['server']['debug']
        )
    except KeyboardInterrupt:
        logger.info("\n系统已关闭")
    except Exception as e:
        logger.error(f"启动错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
