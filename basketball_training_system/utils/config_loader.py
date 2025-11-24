"""
配置文件加载器
"""
import yaml
import os
from pathlib import Path


def load_config(config_path=None):
    """
    加载YAML配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
    
    Returns:
        dict: 配置字典
    """
    if config_path is None:
        # 获取项目根目录
        root_dir = Path(__file__).parent.parent
        config_path = root_dir / "configs" / "config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_config_value(config, *keys, default=None):
    """
    从嵌套配置字典中获取值
    
    Args:
        config: 配置字典
        *keys: 键的路径
        default: 默认值
    
    Returns:
        配置值或默认值
    """
    value = config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    return value if value is not None else default
