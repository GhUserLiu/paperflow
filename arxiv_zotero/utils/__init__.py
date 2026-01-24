"""
工具模块 | Utils Module
"""

from .collection_logger import CollectionLogger
from .config_loader import ConfigError as ConfigLoadError
from .config_loader import (
    ConfigLoader,
    get_zotero_config,
    require_config,
)
from .credentials import CredentialsError, load_credentials
from .errors import (
    APITimeoutError,
    ChinaXivError,
    ConfigError,
    DuplicatePaperError,
    OpenAlexError,
    PaperDownloadError,
    ZoteroAPIError,
    ZoteroConnectorError,
    ZoteroUploadError,
    handle_error,
    ignore_error,
    log_and_raise,
    retry_on_error,
    safe_execute,
)
from .journal_ranker import JournalRanker
from .pdf_manager import PDFManager
from .performance import PerformanceMonitor, get_global_monitor, monitor_performance, timeit

__all__ = [
    # Config
    "ConfigLoader",
    "ConfigLoadError",  # config_loader 专用
    "ConfigError",  # errors.ConfigError（统一）
    "get_zotero_config",
    "require_config",
    # Credentials
    "CredentialsError",
    "load_credentials",
    # Errors
    "ZoteroConnectorError",
    "ZoteroAPIError",
    "PaperDownloadError",
    "ZoteroUploadError",
    "APITimeoutError",
    "DuplicatePaperError",
    "ChinaXivError",
    "OpenAlexError",
    "retry_on_error",
    "handle_error",
    "safe_execute",
    "log_and_raise",
    "ignore_error",
    # Utils
    "JournalRanker",
    "PDFManager",
    # Performance
    "PerformanceMonitor",
    "get_global_monitor",
    "monitor_performance",
    "timeit",
    # Logging
    "CollectionLogger",
]
