"""
配置加载器测试 | Config Loader Tests
"""

import os

import pytest

from arxiv_zotero.utils import ConfigLoader
from arxiv_zotero.utils.config_loader import ConfigError


class TestConfigLoader:
    """配置加载器测试"""

    def test_load_zotero_config_success(self, monkeypatch):
        """测试成功加载配置"""
        # 设置环境变量
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_library_id")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_api_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection_key")

        # 加载配置
        config = ConfigLoader.load_zotero_config()

        # 验证
        assert config["library_id"] == "test_library_id"
        assert config["api_key"] == "test_api_key"
        assert config["collection_key"] == "test_collection_key"
        assert config["enable_chinaxiv"] is False

    def test_load_zotero_config_with_chinaxiv(self, monkeypatch):
        """测试加载配置（启用 ChinaXiv）"""
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_library_id")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_api_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection_key")
        monkeypatch.setenv("ENABLE_CHINAXIV", "true")

        config = ConfigLoader.load_zotero_config()

        assert config["enable_chinaxiv"] is True

    def test_load_zotero_config_missing_library_id(self, monkeypatch):
        """测试缺少 LIBRARY_ID"""
        # 使用 mock 直接控制 os.getenv
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "ZOTERO_LIBRARY_ID":
                return None  # 模拟缺失
            elif key == "ZOTERO_API_KEY":
                return "test_api_key"
            elif key == "TEMP_COLLECTION_KEY":
                return "test_collection_key"
            return original_getenv(key, default)

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # 验证抛出 ConfigError
        with pytest.raises(ConfigError):
            ConfigLoader.load_zotero_config()

    def test_load_zotero_config_missing_api_key(self, monkeypatch):
        """测试缺少 API_KEY"""
        # 使用 mock 直接控制 os.getenv
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "ZOTERO_LIBRARY_ID":
                return "test_library_id"
            elif key == "ZOTERO_API_KEY":
                return None  # 模拟缺失
            elif key == "TEMP_COLLECTION_KEY":
                return "test_collection_key"
            return original_getenv(key, default)

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # 验证抛出 ConfigError
        with pytest.raises(ConfigError):
            ConfigLoader.load_zotero_config()

    def test_load_zotero_config_with_optional_collection_key(self, monkeypatch):
        """测试 TEMP_COLLECTION_KEY 为可选（不提供也能成功）"""
        # 使用 mock 直接控制 os.getenv
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "ZOTERO_LIBRARY_ID":
                return "test_library_id"
            elif key == "ZOTERO_API_KEY":
                return "test_api_key"
            elif key == "TEMP_COLLECTION_KEY":
                return None  # 模拟缺失
            return original_getenv(key, default)

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # 验证可以成功加载（不抛出 ConfigError）
        config = ConfigLoader.load_zotero_config()

        assert config["library_id"] == "test_library_id"
        assert config["api_key"] == "test_api_key"
        assert config["collection_key"] is None  # 可选，允许为 None
        assert config["enable_chinaxiv"] is False

    def test_load_zotero_config_missing_all_required(self, monkeypatch):
        """测试缺少所有必需配置"""
        # 使用 mock 直接控制 os.getenv
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key in ["ZOTERO_LIBRARY_ID", "ZOTERO_API_KEY", "TEMP_COLLECTION_KEY"]:
                return None  # 模拟全部缺失
            return original_getenv(key, default)

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # 验证抛出 ConfigError
        with pytest.raises(ConfigError):
            ConfigLoader.load_zotero_config()

    def test_validate_env_file_exists(self, tmp_path, monkeypatch):
        """测试 .env 文件存在"""
        # 创建临时 .env 文件
        env_file = tmp_path / ".env"
        env_file.write_text("TEST=value")

        monkeypatch.chdir(tmp_path)

        assert ConfigLoader.validate_env_file() is True

    def test_validate_env_file_not_exists(self, tmp_path, monkeypatch):
        """测试 .env 文件不存在"""
        monkeypatch.chdir(tmp_path)

        assert ConfigLoader.validate_env_file() is False

    def test_check_env_setup_complete(self, monkeypatch):
        """测试环境配置完整"""
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_id")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection")

        is_complete, missing = ConfigLoader.check_env_setup()

        assert is_complete is True
        assert len(missing) == 0

    def test_check_env_setup_incomplete(self, monkeypatch):
        """测试环境配置不完整"""
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_id")
        # 缺少其他必需变量

        is_complete, missing = ConfigLoader.check_env_setup()

        assert is_complete is False
        assert "ZOTERO_API_KEY" in missing
        # TEMP_COLLECTION_KEY 不再是必需的，所以不应该在缺失列表中
        assert "TEMP_COLLECTION_KEY" not in missing
