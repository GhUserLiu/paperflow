"""
性能监控模块 | Performance Monitoring Module

提供函数性能监控、统计和报告功能
"""

import functools
import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    性能监控器 - 跟踪函数执行时间和统计信息

    功能：
    - 记录函数执行时间
    - 统计调用次数
    - 记录成功/失败次数
    - 生成性能报告
    """

    def __init__(self):
        """初始化性能监控器"""
        # 统计数据存储
        self.stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "call_count": 0,
                "total_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "success_count": 0,
                "error_count": 0,
                "last_call": None,
                "last_error": None,
            }
        )

    def track(self, func: Callable = None, *,
              name: Optional[str] = None) -> Callable:
        """
        性能监控装饰器

        Args:
            func: 要监控的函数
            name: 自定义名称（默认使用函数名）

        Usage:
            @monitor.track
            def my_function():
                pass

            或自定义名称：
            @monitor.track(name="CustomName")
            def my_function():
                pass
        """

        def decorator(f: Callable) -> Callable:
            func_name = name or f"{f.__module__}.{f.__qualname__}"

            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                error_occurred = False
                error_msg = None

                try:
                    result = f(*args, **kwargs)
                    return result
                except Exception as e:
                    error_occurred = True
                    error_msg = str(e)
                    raise
                finally:
                    # 计算执行时间
                    execution_time = time.time() - start_time

                    # 更新统计信息
                    stats = self.stats[func_name]
                    stats["call_count"] += 1
                    stats["total_time"] += execution_time
                    stats["min_time"] = min(stats["min_time"], execution_time)
                    stats["max_time"] = max(stats["max_time"], execution_time)
                    stats["last_call"] = datetime.now()

                    if error_occurred:
                        stats["error_count"] += 1
                        stats["last_error"] = error_msg
                    else:
                        stats["success_count"] += 1

            return wrapper

        if func is None:
            # @monitor.track() 或 @monitor.track(name="...")
            return decorator
        else:
            # @monitor.track
            return decorator(func)

    def get_stats(self, func_name: str) -> Dict[str, Any]:
        """
        获取指定函数的统计信息

        Args:
            func_name: 函数名称

        Returns:
            统计信息字典
        """
        if func_name not in self.stats:
            return {}

        stats = self.stats[func_name].copy()
        if stats["call_count"] > 0:
            stats["avg_time"] = stats["total_time"] / stats["call_count"]
            stats["success_rate"] = (
                stats["success_count"] / stats["call_count"]) * 100
        else:
            stats["avg_time"] = 0.0
            stats["success_rate"] = 0.0

        return stats

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有函数的统计信息

        Returns:
            所有统计信息字典
        """
        return {func_name: self.get_stats(func_name)
                for func_name in self.stats}

    def generate_report(self, sort_by: str = "total_time") -> str:
        """
        生成性能报告

        Args:
            sort_by: 排序字段 ('total_time', 'call_count', 'avg_time', 'max_time')

        Returns:
            格式化的报告字符串
        """
        if not self.stats:
            return "暂无性能数据 | No performance data available"

        # 获取所有统计信息
        all_stats = self.get_all_stats()

        # 排序
        valid_sort_fields = {
            "total_time",
            "call_count",
            "avg_time",
            "max_time",
            "min_time"}
        if sort_by not in valid_sort_fields:
            sort_by = "total_time"

        sorted_stats = sorted(
            all_stats.items(), key=lambda x: x[1].get(
                sort_by, 0), reverse=True)

        # 生成报告
        lines = [
            "=" * 80,
            "性能监控报告 | Performance Monitoring Report",
            f"生成时间 | Generated: {
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            "",
        ]

        for func_name, stats in sorted_stats:
            lines.append(f"函数 | Function: {func_name}")
            lines.append(f"  调用次数 | Calls: {stats['call_count']}")
            lines.append(f"  总耗时 | Total Time: {stats['total_time']:.4f}s")
            lines.append(f"  平均耗时 | Avg Time: {stats['avg_time']:.4f}s")
            lines.append(f"  最小耗时 | Min Time: {stats['min_time']:.4f}s")
            lines.append(f"  最大耗时 | Max Time: {stats['max_time']:.4f}s")
            lines.append(f"  成功次数 | Success: {stats['success_count']}")
            lines.append(f"  失败次数 | Errors: {stats['error_count']}")
            lines.append(f"  成功率 | Success Rate: {stats['success_rate']:.1f}%")

            if stats["last_call"]:
                lines.append(
                    f"  最后调用 | Last Call: {
                        stats['last_call'].strftime('%Y-%m-%d %H:%M:%S')}"
                )

            if stats["last_error"]:
                lines.append(f"  最后错误 | Last Error: {stats['last_error']}")

            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def print_report(self, sort_by: str = "total_time"):
        """
        打印性能报告到控制台

        Args:
            sort_by: 排序字段
        """
        print(self.generate_report(sort_by=sort_by))

    def reset(self):
        """重置所有统计信息"""
        self.stats.clear()
        logger.info("性能统计已重置 | Performance statistics reset")

    def export_stats(self) -> Dict[str, Any]:
        """
        导出统计数据（用于持久化或分析）

        Returns:
            可序列化的统计数据
        """
        export_data = {}
        for func_name, stats in self.stats.items():
            export_data[func_name] = {
                "call_count": stats["call_count"],
                "total_time": stats["total_time"],
                "min_time": stats["min_time"] if stats["min_time"] != float("inf") else 0.0,
                "max_time": stats["max_time"],
                "success_count": stats["success_count"],
                "error_count": stats["error_count"],
                "last_call": stats["last_call"].isoformat() if stats["last_call"] else None,
                "last_error": stats["last_error"],
            }

        return export_data


# 全局性能监控器实例
_global_monitor = None


def get_global_monitor() -> PerformanceMonitor:
    """
    获取全局性能监控器实例

    Returns:
        全局 PerformanceMonitor 实例
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def monitor_performance(
    func: Callable = None, *, name: Optional[str] = None, use_global: bool = True
) -> Callable:
    """
    便捷的性能监控装饰器（使用全局监控器）

    Args:
        func: 要监控的函数
        name: 自定义名称
        use_global: 是否使用全局监控器（默认 True）

    Usage:
        @monitor_performance
        def my_function():
            pass

        @monitor_performance(name="MyFunction")
        def my_function():
            pass
    """

    def decorator(f: Callable) -> Callable:
        monitor = get_global_monitor() if use_global else PerformanceMonitor()
        return monitor.track(f, name=name)

    if func is None:
        return decorator
    else:
        return decorator(func)


def timeit(func: Callable = None, *, verbose: bool = True) -> Callable:
    """
    简单的计时装饰器（仅打印执行时间）

    Args:
        func: 要计时的函数
        verbose: 是否打印执行时间

    Usage:
        @timeit
        def my_function():
            pass
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time

            if verbose:
                logger.info(
                    f"{f.__name__} 执行耗时 | Execution time: {execution_time:.4f}s")

            return result

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)
