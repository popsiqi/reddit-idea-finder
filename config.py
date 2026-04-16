"""配置加载模块"""
import json
import os
from pathlib import Path
from typing import Any


CONFIG_FILE = "config.json"


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """加载配置文件

    Args:
        config_path: 配置文件路径，默认为当前目录的 config.json

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件格式错误或缺少必要字段
    """
    if config_path is None:
        config_path = CONFIG_FILE

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 验证必要字段
    required_fields = ["reddit", "claude"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"配置缺少必要字段: {field}")

    reddit_required = ["client_id", "client_secret", "user_agent"]
    for field in reddit_required:
        if field not in config["reddit"]:
            raise ValueError(f"Reddit 配置缺少必要字段: {field}")
        if config["reddit"][field].startswith("YOUR_"):
            raise ValueError(f"Reddit 配置字段 {field} 需要填写真实值")

    claude_required = ["api_key", "model"]
    for field in claude_required:
        if field not in config["claude"]:
            raise ValueError(f"Claude 配置缺少必要字段: {field}")
        if config["claude"]["api_key"].startswith("YOUR_"):
            raise ValueError(f"Claude API Key 需要填写真实值")

    # 设置默认值
    if "default_subreddits" not in config:
        config["default_subreddits"] = ["SomebodyMakeThis", "AppIdeas", "Startup_Ideas"]
    if "output_dir" not in config:
        config["output_dir"] = "./reports"
    if "data_dir" not in config:
        config["data_dir"] = "./data"
    if "max_comments_per_post" not in config:
        config["max_comments_per_post"] = 100

    return config


def get_output_dir(config: dict[str, Any]) -> Path:
    """获取输出目录路径，不存在则创建"""
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_data_dir(config: dict[str, Any]) -> Path:
    """获取数据目录路径，不存在则创建"""
    data_dir = Path(config["data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir