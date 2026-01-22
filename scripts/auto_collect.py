"""
Automated Paper Collection Script for 5 Research Categories
自动采集5类研究方向的论文
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict

from arxiv_zotero import ArxivSearchParams, ArxivZoteroCollector
from arxiv_zotero.utils import ConfigLoader, get_global_monitor
from arxiv_zotero.utils.errors import ConfigError

# Fix Windows encoding issue
# 修复Windows编码问题
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def load_config():
    """加载并验证配置"""
    try:
        config = ConfigLoader.load_zotero_config()
        return config["library_id"], config["api_key"], config["enable_chinaxiv"]
    except ConfigError as e:
        print(f"\n❌ 配置错误: {e}")
        print("\n💡 快速配置:")
        print("   1. 复制 .env.example 到 .env:")
        print("      cp .env.example .env")
        print("   2. 在 .env 中填入你的 Zotero 凭证")
        print("   3. 重新运行程序\n")
        sys.exit(1)


# Query configuration for 5 research categories
# 五类研究方向的查询配置
QUERY_MAP: Dict[str, str] = {
    "general": (
        '("intelligent connected vehicles" OR "autonomous driving") '
        'AND (communication OR perception OR "sensor fusion" OR planning)'
    ),
    "communication": (
        '("V2X" OR "vehicle-to-everything" OR VANET) '
        'AND (security OR "semantic communication" OR '
        'latency OR "beamforming")'
    ),
    "perception": (
        '(camera OR lidar OR radar OR "sensor fusion") '
        'AND ("autonomous driving" OR "object detection" OR '
        '"trajectory prediction")'
    ),
    "control": (
        '("path planning" OR "motion planning" OR "model predictive "'
        '"control" OR MPC) '
        "AND vehicle"
    ),
    "security": (
        '(safety OR security OR privacy OR "adversarial attack") '
        'AND ("autonomous vehicle" OR "connected vehicle")'
    ),
}

# Zotero collection keys for each category
# 每个类别的Zotero集合KEY
COLLECTION_MAP: Dict[str, str] = {
    "communication": "3E4NFDPR",
    "control": "8862N8CE",
    "general": "LRML5CDJ",
    "perception": "8CQV3SDV",
    "security": "S97HI5KX",
}

# Global configuration
# 全局配置
# Read from environment variables (removed hardcoded credentials for security)
# 从环境变量读取（已移除硬编码凭证以提高安全性）
ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, ENABLE_CHINAXIV = load_config()

MAX_RESULTS_PER_CATEGORY = 10  # 每个类别最多获取论文数

# Time filter: only collect papers from the last N hours
# 时间过滤:只收集过去 N 小时内的论文
TIME_FILTER_HOURS = 25

# Bilingual configuration
# 双语配置
USE_BILINGUAL_CONFIG = os.getenv("USE_BILINGUAL_CONFIG", "true").lower() == "true"  # 启用双语配置
BILINGUAL_CONFIG_PATH = os.getenv("BILINGUAL_CONFIG_PATH", "config/bilingual_keywords.yaml")


async def collect_papers_for_category_bilingual(
    category: str, collection_key: str
) -> tuple[int, int]:
    """
    Collect papers for a specific category using bilingual keywords configuration
    使用双语关键词配置为特定类别采集论文

    Args:
        category: Category name (类别名称)
        collection_key: Zotero collection key (Zotero集合KEY)

    Returns:
        Tuple of (successful_count, failed_count)
    """
    print(f"\n{'='*60}")
    print(f"开始采集类别: {category} (双语模式)")
    print(f"目标集合: {collection_key}")
    print(f"时间范围: 过去 {TIME_FILTER_HOURS} 小时")
    print(f"配置文件: {BILINGUAL_CONFIG_PATH}")
    print(f"数据来源: arXiv (英文) + ChinaXiv (中文)")
    print(f"每个来源上限: 25 篇")
    print(f"{'='*60}")

    try:
        # Initialize collector with ChinaXiv enabled
        collector = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=collection_key,
            enable_chinaxiv=True,  # Always enable for bilingual mode
        )

        # Calculate time filter (past N hours)
        start_date = datetime.now() - timedelta(hours=TIME_FILTER_HOURS)
        print(f"起始时间: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Run bilingual collection
        successful, failed = await collector.run_bilingual_collection_async(
            category=category,
            start_date=start_date,
            config_path=BILINGUAL_CONFIG_PATH,
            download_pdfs=True,
        )

        print(f"\n[OK] {category} bilingual collection completed:")
        print(f"  Successful: {successful} papers")
        print(f"  Failed: {failed} papers")

        return successful, failed

    except Exception as e:
        print(f"\n[ERROR] {category} bilingual collection failed: {e}")
        import traceback

        traceback.print_exc()
        return 0, 0


async def collect_papers_for_category(
    category: str, query: str, collection_key: str
) -> tuple[int, int]:
    """
    Collect papers for a specific category
    为特定类别采集论文

    Args:
        category: Category name (类别名称)
        query: Search query (搜索查询)
        collection_key: Zotero collection key (Zotero集合KEY)

    Returns:
        Tuple of (successful_count, failed_count)
    """
    print(f"\n{'='*60}")
    print(f"开始采集类别: {category}")
    print(f"查询语句: {query}")
    print(f"目标集合: {collection_key}")
    print(f"时间范围: 过去 {TIME_FILTER_HOURS} 小时")
    print(f"数据来源: arXiv" + (", ChinaXiv" if ENABLE_CHINAXIV else ""))
    print(f"{'='*60}")

    try:
        # Initialize collector with specific collection and ChinaXiv enabled
        # 初始化采集器，指定集合并启用 ChinaXiv
        collector = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=collection_key,
            enable_chinaxiv=ENABLE_CHINAXIV,
        )

        # Calculate time filter (past N hours)
        # 计算时间过滤(过去 N 小时)
        start_date = datetime.now() - timedelta(hours=TIME_FILTER_HOURS)

        # Configure search parameters with time filter
        # 配置搜索参数(包含时间过滤)
        search_params = ArxivSearchParams(
            keywords=[query], start_date=start_date, max_results=MAX_RESULTS_PER_CATEGORY
        )

        print(f"起始时间: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Run collection with multi-source support
        # 执行采集(支持多来源)
        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=True,
            use_all_sources=True,  # 启用多来源搜索(arXiv + ChinaXiv)
        )

        print(f"\n[OK] {category} collection completed:")
        print(f"  Successful: {successful} papers")
        print(f"  Failed: {failed} papers")

        return successful, failed

    except Exception as e:
        print(f"\n[ERROR] {category} collection failed: {e}")
        return 0, 0


async def main():
    """
    Main function to collect papers for all categories
    主函数，采集所有类别的论文
    """
    print("\n" + "=" * 60)
    print("ArXiv论文自动采集系统")
    print("Auto Paper Collection System")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"采集类别数: {len(QUERY_MAP)}")

    # Display mode
    if USE_BILINGUAL_CONFIG:
        print(f"采集模式: 双语模式 (Bilingual)")
        print(f"  - arXiv: 英文关键词 (每类上限25篇)")
        print(f"  - ChinaXiv: 中文关键词 (每类上限25篇)")
        print(f"  - 总计上限: 每类50篇")
    else:
        print(f"采集模式: 标准模式 (Standard)")
        print(f"  - 数据源: arXiv" + (", ChinaXiv" if ENABLE_CHINAXIV else ""))
        print(f"  - 每类最多论文数: {MAX_RESULTS_PER_CATEGORY}")

    print(f"时间范围: 过去 {TIME_FILTER_HOURS} 小时")
    print(f"查重功能: 已启用（基于论文ID全局去重）")

    # Statistics
    total_successful = 0
    total_failed = 0
    results = {}

    # Collect papers for each category
    # 为每个类别采集论文
    for category, query in QUERY_MAP.items():
        collection_key = COLLECTION_MAP.get(category)

        if not collection_key:
            print(f"\n[WARNING] {category} has no collection key configured, skipping")
            continue

        # Choose collection method based on mode
        # 根据模式选择采集方法
        if USE_BILINGUAL_CONFIG:
            # Use bilingual config with different keywords for each source
            # 使用双语配置，为不同来源使用不同的关键词
            successful, failed = await collect_papers_for_category_bilingual(
                category=category, collection_key=collection_key
            )
        else:
            # Use standard mode (single query for all sources)
            # 使用标准模式（所有来源使用单一查询）
            successful, failed = await collect_papers_for_category(
                category=category, query=query, collection_key=collection_key
            )

        results[category] = {
            "successful": successful,
            "failed": failed,
            "collection_key": collection_key,
        }

        total_successful += successful
        total_failed += failed

        # Small delay between categories to be respectful to APIs
        # 类别之间稍作延迟，避免对API造成压力
        if category != list(QUERY_MAP.keys())[-1]:
            print("\n等待3秒后继续下一类别...")
            await asyncio.sleep(3)

    # Print summary
    # 打印总结
    print("\n" + "=" * 60)
    print("采集完成！Collection Summary")
    print("=" * 60)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n总计:")
    print(f"  成功采集: {total_successful} 篇")
    print(f"  失败: {total_failed} 篇")

    print(f"\n分类详情:")
    for category, stats in results.items():
        print(f"\n  {category.upper()}:")
        print(f"    集合KEY: {stats['collection_key']}")
        print(f"    成功: {stats['successful']} 篇")
        print(f"    失败: {stats['failed']} 篇")

    print("\n" + "=" * 60)

    # 生成性能报告（如果性能监控已启用）
    # Generate performance report (if monitoring is enabled)
    monitor = get_global_monitor()
    if monitor.stats:
        print("\n")
        monitor.print_report(sort_by="total_time")


if __name__ == "__main__":
    # Run the async main function
    # 运行异步主函数
    asyncio.run(main())
