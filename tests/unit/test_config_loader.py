"""
配置加载器测试 | Config Loader Tests
"""

import os
import pytest
from arxiv_zotero.utils import ConfigLoader, ConfigError


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
        # 首先删除所有可能存在的环境变量
        monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
        monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
        monkeypatch.delenv("TEMP_COLLECTION_KEY", raising=False)

        # 然后只设置部分变量
        monkeypatch.setenv("ZOTERO_API_KEY", "test_api_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection_key")

        with pytest.raises(ConfigError) as exc_info:
            ConfigLoader.load_zotero_config()

        assert "ZOTERO_LIBRARY_ID" in str(exc_info.value)

    def test_load_zotero_config_missing_api_key(self, monkeypatch):
        """测试缺少 API_KEY"""
        # 首先删除所有可能存在的环境变量
        monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
        monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
        monkeypatch.delenv("TEMP_COLLECTION_KEY", raising=False)

        # 然后只设置部分变量
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_library_id")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection_key")

        with pytest.raises(ConfigError) as exc_info:
            ConfigLoader.load_zotero_config()

        assert "ZOTERO_API_KEY" in str(exc_info.value)

    def test_load_zotero_config_missing_collection_key(self, monkeypatch):
        """测试缺少 COLLECTION_KEY"""
        # 首先删除所有可能存在的环境变量
        monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
        monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
        monkeypatch.delenv("TEMP_COLLECTION_KEY", raising=False)

        # 然后只设置部分变量
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_library_id")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_api_key")

        with pytest.raises(ConfigError) as exc_info:
            ConfigLoader.load_zotero_config()

        assert "TEMP_COLLECTION_KEY" in str(exc_info.value)

    def test_load_zotero_config_missing_all_required(self, monkeypatch):
        """测试缺少所有必需配置"""
        # 清空所有环境变量
        for key in ["ZOTERO_LIBRARY_ID", "ZOTERO_API_KEY", "TEMP_COLLECTION_KEY"]:
            monkeypatch.delenv(key, raising=False)

        with pytest.raises(ConfigError) as exc_info:
            ConfigLoader.load_zotero_config()

        error_msg = str(exc_info.value)
        assert "ZOTERO_LIBRARY_ID" in error_msg
        assert "ZOTERO_API_KEY" in error_msg

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
        assert "TEMP_COLLECTION_KEY" in missing
