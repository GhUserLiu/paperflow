"""Environment-based configuration loader"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Load environment-specific configuration"""

    def __init__(self, env: str = "production"):
        """
        Initialize environment configuration

        Args:
            env: Environment name ('development', 'production', or 'test')
        """
        self.env = env
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.config: Dict[str, Any] = {}

        if env == "development":
            self.config_file = self.config_dir / "development.yaml"
        elif env == "production":
            self.config_file = self.config_dir / "production.yaml"
        elif env == "test":
            self.config_file = self.config_dir / "test.yaml"
        else:
            raise ValueError(f"Unknown environment: {env}")

        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        if not YAML_AVAILABLE:
            logger.warning("PyYAML not installed, using default configuration")
            self.config = self._get_default_config()
            return

        if not self.config_file.exists():
            logger.warning(f"Config file not found: {self.config_file}")
            self.config = self._get_default_config()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}

            logger.info(f"Loaded {self.env} configuration from {self.config_file}")

        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "rate_limiting": {
                "enabled": True,
                "max_requests_per_minute": 10
            },
            "cache": {
                "arxiv_id_cache_ttl": 300,
                "lookup_cache_max_size": 1000
            },
            "collection": {
                "max_results_per_category": 20,
                "download_pdfs": True,
                "concurrent_limit": 5
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key

        Args:
            key: Configuration key (e.g., 'logging.level')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            config = EnvironmentConfig('production')
            log_level = config.get('logging.level', 'INFO')
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value if value is not None else default

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get('logging', {})

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration"""
        return self.get('cache', {})

    def get_collection_config(self) -> Dict[str, Any]:
        """Get paper collection configuration"""
        return self.get('collection', {})

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.env == "development"

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.env == "production"

    def is_test(self) -> bool:
        """Check if running in test mode"""
        return self.env == "test"

    @classmethod
    def from_env(cls) -> "EnvironmentConfig":
        """
        Create EnvironmentConfig from ENVIRONMENT environment variable

        Returns:
            EnvironmentConfig instance

        Example:
            # Set environment variable
            export ENVIRONMENT=development

            # Load config
            config = EnvironmentConfig.from_env()
        """
        env = os.getenv("ENVIRONMENT", "production").lower()
        return cls(env)


def setup_logging_from_config(config: EnvironmentConfig):
    """
    Setup logging based on environment configuration

    Args:
        config: EnvironmentConfig instance

    Example:
        config = EnvironmentConfig('development')
        setup_logging_from_config(config)
    """
    log_config = config.get_logging_config()

    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/arxiv_zotero.log", mode='a', encoding='utf-8')
        ]
    )

    logger.info(f"Logging configured for {config.env} environment (level: {log_config.get('level')})")


# Example usage
if __name__ == "__main__":
    # Load configuration based on environment variable
    config = EnvironmentConfig.from_env()

    print(f"Environment: {config.env}")
    print(f"Logging level: {config.get('logging.level')}")
    print(f"Rate limiting enabled: {config.get('rate_limiting.enabled')}")
    print(f"Max results: {config.get('collection.max_results_per_category')}")
    print(f"Concurrent limit: {config.get('collection.concurrent_limit')}")

    # Setup logging
    setup_logging_from_config(config)

    logger.info("Configuration loaded successfully")
