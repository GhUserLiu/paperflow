"""
测试 API 优化效果
"""

import asyncio
import time
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

async def test_optimized_performance():
    """测试优化后的 API 性能"""

    # 配置
    zotero_library_id = "19092277"
    zotero_api_key = "HoLB2EnPj4PpHo1gQ65qy2aw"
    collection_key = "LRML5CDJ"  # general collection

    # 搜索参数 - 5 篇论文用于快速测试
    search_params = ArxivSearchParams(
        keywords=['"autonomous driving" AND perception'],
        max_results=5,
        categories=["cs.CV", "cs.RO"]
    )

    # 创建 collector
    collector = ArxivZoteroCollector(
        zotero_library_id=zotero_library_id,
        zotero_api_key=zotero_api_key,
        collection_key=collection_key
    )

    print("=" * 70)
    print("API 优化效果测试")
    print("=" * 70)
    print()

    # 第一次运行 - 应该添加新论文
    print("[第一次运行] - 处理论文...")
    print("-" * 70)

    start_time = time.time()
    successful_1, failed_1 = await collector.run_collection_async(
        search_params=search_params,
        download_pdfs=False  # 跳过 PDF 以加快测试
    )
    elapsed_1 = time.time() - start_time

    print()
    print(f"第一次运行结果:")
    print(f"  成功: {successful_1} 篇")
    print(f"  失败: {failed_1} 篇")
    print(f"  耗时: {elapsed_1:.1f} 秒")

    # 获取 API 统计
    api_stats = collector.zotero_client.get_api_stats()
    print(f"  API 请求: {api_stats['total_requests']} 次")
    print(f"  平均速率: {api_stats['rate']:.2f} 次/秒")
    print()

    # 等待一下
    await asyncio.sleep(2)

    # 第二次运行 - 应该全部跳过(使用缓存)
    print("[第二次运行] - 测试缓存效果(全部跳过重复)...")
    print("-" * 70)

    start_time = time.time()
    successful_2, failed_2 = await collector.run_collection_async(
        search_params=search_params,
        download_pdfs=False
    )
    elapsed_2 = time.time() - start_time

    print()
    print(f"第二次运行结果:")
    print(f"  成功: {successful_2} 篇(全部被跳过)")
    print(f"  失败: {failed_2} 篇")
    print(f"  耗时: {elapsed_2:.1f} 秒")

    # 获取 API 统计
    api_stats_2 = collector.zotero_client.get_api_stats()
    print(f"  API 请求: {api_stats_2['total_requests']} 次")
    print(f"  第二轮新增: {api_stats_2['total_requests'] - api_stats['total_requests']} 次")
    print(f"  平均速率: {api_stats_2['rate']:.2f} 次/秒")
    print(f"  缓存条目: {api_stats_2['cache_size']} 条")

    # 清理
    await collector.close()

    # 验证结果
    print()
    print("=" * 70)
    print("优化效果分析")
    print("=" * 70)

    new_requests = api_stats['total_requests']
    cached_requests = api_stats_2['total_requests'] - api_stats['total_requests']

    print(f"第一次运行(新论文): {new_requests} 次 API 请求")
    print(f"第二次运行(缓存): {cached_requests} 次 API 请求")
    print(f"减少比例: {(1 - cached_requests/new_requests) * 100:.1f}%")

    # 验证是否符合 Zotero 限制
    print()
    print("Zotero API 限制检查:")
    print(f"  限制: 每 10 分钟 100 次")
    print(f"  第一次运行: {new_requests} 次 {'✅ 符合' if new_requests <= 100 else '❌ 超限'}")
    print(f"  第二次运行: {cached_requests} 次 {'✅ 符合' if cached_requests <= 100 else '❌ 超限'}")

    if cached_requests <= 10:  # 期望: 只有 1 次缓存刷新请求
        print(f"  缓存效果: ✅ 优秀 (只用了 {cached_requests} 次请求)")
    else:
        print(f"  缓存效果: ⚠️ 需要改进 (用了 {cached_requests} 次请求)")

    print()
    print("=" * 70)
    print("测试完成!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_optimized_performance())
