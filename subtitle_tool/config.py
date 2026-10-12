"""配置加载模块"""

import yaml
from pathlib import Path


def load_config(path="config.yaml"):
    """加在配置文件"""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
