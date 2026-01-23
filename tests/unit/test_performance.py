"""
性能监控模块单元测试 | Performance Monitor Unit Tests
"""

import time

import pytest

from arxiv_zotero.utils.performance import (
    PerformanceMonitor,
    get_global_monitor,
    monitor_performance,
    timeit,
)


class TestPerformanceMonitor:
    """PerformanceMonitor 测试"""

    def test_init(self):
        """测试初始化"""
        monitor = PerformanceMonitor()
        assert monitor.stats == {}
        assert len(monitor.stats) == 0

    def test_track_decorator_no_args(self):
        """测试装饰器（无参数）"""
        monitor = PerformanceMonitor()

        @monitor.track(name="test_function")
        def test_function():
            time.sleep(0.01)
            return "result"

        result = test_function()
        assert result == "result"

        # 验证统计信息被记录
        stats = monitor.get_stats("test_function")
        assert stats["call_count"] == 1
        assert stats["total_time"] > 0
        assert stats["success_count"] == 1
        assert stats["error_count"] == 0

    def test_track_decorator_with_name(self):
        """测试装饰器（自定义名称）"""
        monitor = PerformanceMonitor()

        @monitor.track(name="CustomFunction")
        def test_function():
            time.sleep(0.01)
            return "result"

        test_function()

        # 验证使用自定义名称
        stats = monitor.get_stats("CustomFunction")
        assert stats["call_count"] == 1
        assert stats["success_count"] == 1

    def test_track_multiple_calls(self):
        """测试多次调用"""
        monitor = PerformanceMonitor()

        @monitor.track(name="test_function")
        def test_function():
            time.sleep(0.01)
            return "result"

        # 调用3次
        for _ in range(3):
            test_function()

        stats = monitor.get_stats("test_function")
        assert stats["call_count"] == 3
        assert stats["success_count"] == 3
        assert stats["total_time"] > 0

    def test_track_with_error(self):
        """测试错误处理"""
        monitor = PerformanceMonitor()

        @monitor.track(name="failing_function")
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        stats = monitor.get_stats("failing_function")
        assert stats["call_count"] == 1
        assert stats["error_count"] == 1
        assert stats["success_count"] == 0
        assert stats["last_error"] == "Test error"

    def test_track_mixed_success_and_error(self):
        """测试混合成功和错误"""
        monitor = PerformanceMonitor()

        @monitor.track(name="conditional_function")
        def conditional_function(should_fail):
            time.sleep(0.01)
            if should_fail:
                raise RuntimeError("Error")
            return "success"

        # 成功调用
        conditional_function(should_fail=False)
        # 失败调用
        with pytest.raises(RuntimeError):
            conditional_function(should_fail=True)
        # 再次成功
        conditional_function(should_fail=False)

        stats = monitor.get_stats("conditional_function")
        assert stats["call_count"] == 3
        assert stats["success_count"] == 2
        assert stats["error_count"] == 1
        assert abs(stats["success_rate"] - (2 / 3 * 100)) < 0.1

    def test_get_stats_nonexistent(self):
        """测试获取不存在的函数统计"""
        monitor = PerformanceMonitor()
        stats = monitor.get_stats("nonexistent_function")
        assert stats == {}

    def test_get_all_stats_empty(self):
        """测试获取所有统计信息（空）"""
        monitor = PerformanceMonitor()
        stats = monitor.get_all_stats()
        assert stats == {}

    def test_get_all_stats_with_data(self):
        """测试获取所有统计信息"""
        monitor = PerformanceMonitor()

        @monitor.track(name="Func1")
        def func1():
            return 1

        @monitor.track(name="Func2")
        def func2():
            return 2

        func1()
        func2()

        all_stats = monitor.get_all_stats()
        assert len(all_stats) == 2
        assert "Func1" in all_stats
        assert "Func2" in all_stats

    def test_min_max_time(self):
        """测试最小/最大时间记录"""
        monitor = PerformanceMonitor()

        @monitor.track(name="variable_function")
        def variable_time_function(delay):
            time.sleep(delay)
            return delay

        # 第一次调用（最短）
        variable_time_function(0.01)
        # 第二次调用（最长）
        variable_time_function(0.05)
        # 第三次调用（中等）
        variable_time_function(0.02)

        stats = monitor.get_stats("variable_function")
        assert stats["min_time"] > 0
        assert stats["max_time"] > stats["min_time"]
        assert stats["max_time"] > 0.04  # 至少0.05秒
        assert stats["min_time"] < 0.05  # 放宽限制以适应CI环境性能波动

    def test_avg_time_calculation(self):
        """测试平均时间计算"""
        monitor = PerformanceMonitor()

        @monitor.track(name="avg_test_function")
        def test_function():
            time.sleep(0.01)
            return "result"

        # 调用3次
        for _ in range(3):
            test_function()

        stats = monitor.get_stats("avg_test_function")
        assert stats["avg_time"] > 0
        assert abs(stats["avg_time"] - (stats["total_time"] / 3)) < 0.001

    def test_generate_report_empty(self):
        """测试生成报告（空数据）"""
        monitor = PerformanceMonitor()
        report = monitor.generate_report()
        assert "暂无性能数据" in report or "No performance data" in report

    def test_generate_report_with_data(self):
        """测试生成报告（有数据）"""
        monitor = PerformanceMonitor()

        @monitor.track(name="TestFunction")
        def test_function():
            time.sleep(0.01)
            return "result"

        test_function()

        report = monitor.generate_report()
        assert "性能监控报告" in report or "Performance Monitoring Report" in report
        assert "TestFunction" in report
        assert "调用次数" in report or "Calls" in report

    def test_generate_report_sort_by(self):
        """测试报告排序"""
        monitor = PerformanceMonitor()

        @monitor.track(name="FastFunc")
        def fast_function():
            time.sleep(0.01)
            return "fast"

        @monitor.track(name="SlowFunc")
        def slow_function():
            time.sleep(0.05)
            return "slow"

        fast_function()
        slow_function()

        # 按总时间排序（SlowFunc 应该在前）
        report = monitor.generate_report(sort_by="total_time")
        slow_pos = report.find("SlowFunc")
        fast_pos = report.find("FastFunc")
        assert slow_pos < fast_pos  # SlowFunc 应该出现在 FastFunc 之前

    def test_reset(self):
        """测试重置统计信息"""
        monitor = PerformanceMonitor()

        @monitor.track(name="reset_test_function")
        def test_function():
            return "result"

        test_function()
        assert len(monitor.stats) > 0

        monitor.reset()
        assert len(monitor.stats) == 0

    def test_export_stats(self):
        """测试导出统计数据"""
        monitor = PerformanceMonitor()

        @monitor.track(name="ExportFunc")
        def test_function():
            time.sleep(0.01)
            return "result"

        test_function()

        exported = monitor.export_stats()
        assert "ExportFunc" in exported
        assert exported["ExportFunc"]["call_count"] == 1
        assert exported["ExportFunc"]["total_time"] > 0
        assert "last_call" in exported["ExportFunc"]

    def test_global_monitor_singleton(self):
        """测试全局监控器单例"""
        monitor1 = get_global_monitor()
        monitor2 = get_global_monitor()
        assert monitor1 is monitor2

    def test_monitor_performance_decorator(self):
        """测试 monitor_performance 装饰器"""

        @monitor_performance(name="global_test_function")
        def test_function():
            time.sleep(0.01)
            return "result"

        test_function()

        # 全局监控器应该记录了这次调用
        monitor = get_global_monitor()
        all_stats = monitor.get_all_stats()
        assert len(all_stats) > 0

    def test_timeit_decorator(self):
        """测试 timeit 装饰器"""

        @timeit
        def test_function():
            time.sleep(0.01)
            return "result"

        result = test_function()
        assert result == "result"
        # timeit 只打印，不记录统计信息

    def test_last_call_timestamp(self):
        """测试最后调用时间戳"""
        monitor = PerformanceMonitor()

        @monitor.track(name="timestamp_test_function")
        def test_function():
            return "result"

        test_function()

        stats = monitor.get_stats("timestamp_test_function")
        assert stats["last_call"] is not None
        assert stats["last_call"].year >= 2024  # 合理的年份

    def test_multiple_functions_independence(self):
        """测试多个函数的统计独立性"""
        monitor = PerformanceMonitor()

        @monitor.track(name="FuncA")
        def func_a():
            time.sleep(0.01)
            return "A"

        @monitor.track(name="FuncB")
        def func_b():
            time.sleep(0.02)
            return "B"

        func_a()
        func_a()
        func_b()

        stats_a = monitor.get_stats("FuncA")
        stats_b = monitor.get_stats("FuncB")

        assert stats_a["call_count"] == 2
        assert stats_b["call_count"] == 1
        # 验证两个函数的统计数据是独立的
        assert stats_a is not stats_b
        assert stats_a["total_time"] > 0
        assert stats_b["total_time"] > 0

    def test_success_rate_calculation(self):
        """测试成功率计算"""
        monitor = PerformanceMonitor()

        @monitor.track(name="success_rate_function")
        def conditional_function(should_fail):
            if should_fail:
                raise ValueError("Error")
            return "success"

        # 5次成功，2次失败
        for _ in range(5):
            conditional_function(should_fail=False)

        for _ in range(2):
            try:
                conditional_function(should_fail=True)
            except BaseException:
                pass

        stats = monitor.get_stats("success_rate_function")
        assert stats["call_count"] == 7
        assert stats["success_count"] == 5
        assert stats["error_count"] == 2
        assert abs(stats["success_rate"] - (5 / 7 * 100)) < 0.1

    def test_track_preserves_function_metadata(self):
        """测试装饰器保留函数元数据"""
        monitor = PerformanceMonitor()

        @monitor.track(name="metadata_test_function")
        def documented_function():
            """这是一个文档字符串"""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == """这是一个文档字符串"""
