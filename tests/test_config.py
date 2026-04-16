"""配置模块测试"""
import json
import tempfile
from pathlib import Path
import pytest
from config import load_config, get_output_dir, get_data_dir, CONFIG_FILE


def test_load_config_missing_file():
    """测试配置文件不存在时抛出异常"""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.json")


def test_load_config_missing_required_field():
    """测试缺少必要字段时抛出异常"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"reddit": {"client_id": "test"}}, f)
        f.flush()
        with pytest.raises(ValueError, match="缺少必要字段"):
            load_config(f.name)
    Path(f.name).unlink()


def test_load_config_placeholder_value():
    """测试占位符值时抛出异常"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({
            "reddit": {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "test",
                "user_agent": "test"
            },
            "claude": {
                "api_key": "test",
                "model": "test"
            }
        }, f)
        f.flush()
        with pytest.raises(ValueError, match="需要填写真实值"):
            load_config(f.name)
    Path(f.name).unlink()


def test_load_config_valid():
    """测试有效配置加载"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({
            "reddit": {
                "client_id": "valid_id",
                "client_secret": "valid_secret",
                "user_agent": "valid_agent"
            },
            "claude": {
                "api_key": "valid_key",
                "model": "claude-sonnet-4-6"
            }
        }, f)
        f.flush()
        config = load_config(f.name)
        assert config["reddit"]["client_id"] == "valid_id"
        assert config["claude"]["model"] == "claude-sonnet-4-6"
        assert config["default_subreddits"] == ["SomebodyMakeThis", "AppIdeas", "Startup_Ideas"]
    Path(f.name).unlink()


def test_get_output_dir_creates_directory():
    """测试输出目录创建"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"output_dir": f"{tmpdir}/new_output"}
        output_dir = get_output_dir(config)
        assert output_dir.exists()
        assert output_dir.name == "new_output"


def test_get_data_dir_creates_directory():
    """测试数据目录创建"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"data_dir": f"{tmpdir}/new_data"}
        data_dir = get_data_dir(config)
        assert data_dir.exists()
        assert data_dir.name == "new_data"