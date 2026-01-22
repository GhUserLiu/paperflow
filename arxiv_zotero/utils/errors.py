"""
统一错误处理模块 | Unified Error Handling

定义项目中所有自定义异常类和错误处理工具
"""

import functools
import logging
import time
from typing import Any, Callable

T = None  # Type placeholder for generic functions
logger = logging.getLogger(__name__)

# ==================== 自定义异常类 ====================


class ZoteroConnectorError(Exception):
    """基础异常类 - 所有自定义异常的父类"""

    pass


class ConfigError(ZoteroConnectorError):
    """配置错误"""

    pass


class ZoteroAPIError(ZoteroConnectorError):
    """Zotero API 错误"""

    def __init__(self, message: str, status_code: int = None,
                 response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

    def __str__(self):
        msg = super().__str__()
        if self.status_code:
            msg += f" (状态码: {self.status_code})"
        if self.response:
            msg += f"\n响应: {self.response[:200]}"
        return msg


class PaperDownloadError(ZoteroConnectorError):
    """论文下载失败"""

    def __init__(self, paper_title: str, url: str, reason: str):
        self.paper_title = paper_title
        self.url = url
        self.reason = reason
        super().__init__(f"下载失败 [{paper_title}]: {reason}\nURL: {url}")


class ZoteroUploadError(ZoteroConnectorError):
    """Zotero 上传失败"""

    def __init__(self, paper_title: str, reason: str):
        self.paper_title = paper_title
        self.reason = reason
        super().__init__(f"上传失败 [{paper_title}]: {reason}")


class APITimeoutError(ZoteroConnectorError):
    """API 超时"""

    def __init__(self, api_name: str, timeout: float):
        self.api_name = api_name
        self.timeout = timeout
        super().__init__(f"{api_name} 请求超时（{timeout}秒）")


class DuplicatePaperError(ZoteroConnectorError):
    """重复论文错误"""

    def __init__(self, paper_id: str, collection: str = None):
        self.paper_id = paper_id
        self.collection = collection
        msg = f"论文已存在: {paper_id}"
        if collection:
            msg += f" (集合: {collection})"
        super().__init__(msg)


class ChinaXivError(ZoteroConnectorError):
    """ChinaXiv API 错误"""

    pass


class OpenAlexError(ZoteroConnectorError):
    """OpenAlex API 错误"""

    pass


# ==================== 重试装饰器 ====================


def retry_on_error(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: logging.Logger = None,
):
    """
    智能重试装饰器

    Args:
        max_attempts: 最大尝试次数
        backoff_factor: 退避因子（每次重试等待时间翻倍）
        exceptions: 需要重试的异常类型
        logger: 日志记录器

    Returns:
        装饰器函数

    Example:
        @retry_on_error(max_attempts=3, exceptions=(RequestException,))
        def fetch_data(url):
            return requests.get(url)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        # 最后一次尝试失败
                        logger.error(
                            f"{func.__name__} 失败（已重试 {max_attempts} 次）: {e}")
                        raise

                    # 计算等待时间
                    wait_time = backoff_factor ** (attempt - 1)
                    logger.warning(
                        f"{func.__name__} 第 {attempt} 次尝试失败: {e}，" f"{wait_time}秒后重试..."
                    )
                    time.sleep(wait_time)

            # 理论上不会到达这里
            raise last_exception

        return wrapper

    return decorator


# ==================== 错误处理工具函数 ====================


def handle_error(error: Exception, context: str = "") -> None:
    """
    统一错误处理

    Args:
        error: 捕获的异常
        context: 错误上下文信息
    """
    if context:
        logger.error(f"{context}: {error}")
    else:
        logger.error(f"错误: {error}")

    # 根据错误类型提供具体建议
    if isinstance(error, ConfigError):
        logger.info("💡 提示: 检查 .env 文件配置")
    elif isinstance(error, ZoteroAPIError):
        logger.info("💡 提示: 检查 Zotero API 密钥和网络连接")
    elif isinstance(error, PaperDownloadError):
        logger.info("💡 提示: 论文可能没有公开的 PDF 或网络问题")
    elif isinstance(error, APITimeoutError):
        logger.info("💡 提示: 网络较慢，请稍后重试")


def safe_execute(func, default=None):
    """
    安全执行函数，捕获所有异常

    Args:
        func: 要执行的函数
        default: 发生异常时返回的默认值

    Returns:
        函数执行结果或默认值

    Example:
        result = safe_execute(lambda: risky_operation(), default=None)
    """
    try:
        return func()
    except Exception as e:
        handle_error(e)
        return default


# ==================== 便捷函数 ====================


def log_and_raise(error: Exception, context: str = "") -> None:
    """
    记录错误并重新抛出

    Args:
        error: 异常对象
        context: 错误上下文
    """
    handle_error(error, context)
    raise error


def ignore_error(func, default=None):
    """
    忽略错误的装饰器

    Args:
        func: 要执行的函数
        default: 发生异常时返回的默认值

    Returns:
        装饰后的函数
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.debug(f"{func.__name__} 被忽略的错误: {e}")
            return default

    return wrapper
