"""
集中配置管理 | Centralized Configuration Management

定义应用的所有配置项，提供类型安全的配置访问
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ZoteroConfig:
    """Zotero API 相关配置"""

    library_id: str
    api_key: str
    collection_key: Optional[str] = None
    min_request_interval: float = 6.0  # Zotero API 限制：每 10 分钟 100 次

    def __post_init__(self):
        if not self.library_id or self.library_id in ["your_library_id", "", "None"]:
            raise ValueError(f"Invalid library_id: '{self.library_id}'")
        if not self.api_key or len(self.api_key) < 10:
            raise ValueError(f"Invalid api_key: must be at least 10 characters")


@dataclass
class CollectionConfig:
    """论文采集相关配置"""

    max_results_per_category: int = 10
    time_filter_hours: int = 25
    download_pdfs: bool = True
    enable_chinaxiv: bool = False
    enable_openalex_ranking: bool = False


@dataclass
class CacheConfig:
    """缓存配置"""

    # arXiv ID 缓存
    arxiv_id_cache_ttl: int = 300  # 5 分钟

    # 通用查重缓存
    lookup_cache_max_size: int = 1000
    lookup_cache_evict_size: int = 200  # 缓存满时删除 20%

    # OpenAlex 缓存目录
    openalex_cache_dir: str = "config"
    openalex_cache_file: str = "journal_metrics_cache.json"


@dataclass
class ConcurrencyConfig:
    """并发控制配置"""

    max_concurrent_papers: int = 5  # 同时处理的论文数量


@dataclass
class LoggingConfig:
    """日志配置"""

    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_dir: str = "logs"
    log_file: str = "arxiv_zotero.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class AppConfig:
    """应用主配置 - 聚合所有配置"""

    zotero: ZoteroConfig = field(default_factory=lambda: ZoteroConfig(library_id="", api_key=""))
    collection: CollectionConfig = field(default_factory=CollectionConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    concurrency: ConcurrencyConfig = field(default_factory=ConcurrencyConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """从环境变量创建配置"""
        import os

        zotero_config = ZoteroConfig(
            library_id=os.getenv("ZOTERO_LIBRARY_ID", ""),
            api_key=os.getenv("ZOTERO_API_KEY", ""),
            collection_key=os.getenv("TEMP_COLLECTION_KEY"),
        )

        return cls(zotero=zotero_config)

    def validate(self) -> bool:
        """验证配置是否有效"""
        try:
            # 验证 Zotero 配置
            if not self.zotero.library_id:
                raise ValueError("ZOTERO_LIBRARY_ID is required")
            if not self.zotero.api_key:
                raise ValueError("ZOTERO_API_KEY is required")

            # 验证并发配置
            if self.concurrency.max_concurrent_papers < 1:
                raise ValueError("max_concurrent_papers must be at least 1")
            if self.concurrency.max_concurrent_papers > 20:
                raise ValueError("max_concurrent_papers should not exceed 20")

            # 验证缓存配置
            if self.cache.arxiv_id_cache_ttl < 0:
                raise ValueError("arxiv_id_cache_ttl must be positive")

            return True

        except ValueError as e:
            logger.error(f"配置验证失败: {e}")
            return False
