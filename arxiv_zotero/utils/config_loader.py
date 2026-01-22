"""
配置加载器 | Configuration Loader

统一加载和验证项目配置，确保安全性
"""

import os
from pathlib import Path
from typing import Optional


class ConfigError(Exception):
    """配置错误"""

    pass


class ConfigLoader:
    """统一配置加载器"""

    # 必需的环境变量
    REQUIRED_VARS = ["ZOTERO_LIBRARY_ID", "ZOTERO_API_KEY"]

    # 可选的环境变量及其默认值
    OPTIONAL_VARS = {
        "TEMP_COLLECTION_KEY": None,
        "ENABLE_CHINAXIV": "false"}  # 无默认值，必须提供

    @classmethod
    def load_zotero_config(cls) -> dict:
        """
        加载 Zotero 配置

        Returns:
            dict: 包含 library_id, api_key, collection_key

        Raises:
            ConfigError: 配置缺失或无效时
        """
        # 检查必需的环境变量
        missing_vars = []
        config = {}

        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            config[var] = value

        if missing_vars:
            raise ConfigError(
                f"缺少必需的环境变量: {', '.join(missing_vars)}\n"
                f"请在 .env 文件中设置这些变量，或从环境变量中提供。\n"
                f"获取 Zotero API Key: https://www.zotero.org/settings/keys"
            )

        # 检查可选但重要的环境变量
        collection_key = os.getenv("TEMP_COLLECTION_KEY")
        if not collection_key:
            raise ConfigError(
                "缺少 TEMP_COLLECTION_KEY 环境变量\n"
                "请提供目标 Zotero 集合的 KEY")

        config["TEMP_COLLECTION_KEY"] = collection_key

        # 添加可选配置
        config["ENABLE_CHINAXIV"] = os.getenv(
            "ENABLE_CHINAXIV", "false").lower() == "true"

        return {
            "library_id": config["ZOTERO_LIBRARY_ID"],
            "api_key": config["ZOTERO_API_KEY"],
            "collection_key": config["TEMP_COLLECTION_KEY"],
            "enable_chinaxiv": config["ENABLE_CHINAXIV"],
        }

    @classmethod
    def validate_env_file(cls) -> bool:
        """
        验证 .env 文件是否存在

        Returns:
            bool: .env 文件是否存在
        """
        env_file = Path.cwd() / ".env"
        if not env_file.exists():
            return False

        # 检查是否为空文件
        if env_file.stat().st_size == 0:
            return False

        return True

    @classmethod
    def check_env_setup(cls) -> tuple[bool, list[str]]:
        """
        检查环境配置状态

        Returns:
            tuple[bool, list[str]]: (是否配置完整, 缺失的变量列表)
        """
        missing = []

        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)

        if not os.getenv("TEMP_COLLECTION_KEY"):
            missing.append("TEMP_COLLECTION_KEY")

        return len(missing) == 0, missing


def get_zotero_config() -> dict:
    """
    便捷函数：获取 Zotero 配置

    Returns:
        dict: Zotero 配置

    Raises:
        ConfigError: 配置无效时
    """
    return ConfigLoader.load_zotero_config()


# 模块级别的便捷函数
def require_config(func):
    """
    装饰器：确保配置已加载

    Usage:
        @require_config
        def some_function():
            config = get_zotero_config()
            ...
    """

    def wrapper(*args, **kwargs):
        try:
            config = get_zotero_config()
            return func(config, *args, **kwargs)
        except ConfigError as e:
            print(f"\n❌ 配置错误: {e}")
            print("\n💡 快速配置:")
            print("   1. 复制 .env.example 到 .env")
            print("   2. 在 .env 中填入你的 Zotero 凭证")
            print("   3. 重新运行程序\n")
            raise

    return wrapper
