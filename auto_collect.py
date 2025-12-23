"""
Automated Paper Collection Script for 5 Research Categories
自动采集5类研究方向的论文
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

# Fix Windows encoding issue
# 修复Windows编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Query configuration for 5 research categories
# 五类研究方向的查询配置
QUERY_MAP: Dict[str, str] = {
    "general": (
        '("intelligent connected vehicles" OR "autonomous driving") '
        "AND (communication OR perception OR \"sensor fusion\" OR planning) "
        "NOT survey NOT review"
    ),
    "communication": (
        '("V2X" OR "vehicle-to-everything" OR VANET) '
        "AND (security OR \"semantic communication\" OR "
        "latency OR \"beamforming\") "
        "NOT survey NOT review"
    ),
    "perception": (
        "(camera OR lidar OR radar OR \"sensor fusion\") "
        "AND (\"autonomous driving\" OR \"object detection\" OR "
        "\"trajectory prediction\") "
        "NOT survey NOT review"
    ),
    "control": (
        '("path planning" OR "motion planning" OR "model predictive "'
        '"control" OR MPC) '
        "AND vehicle NOT survey NOT review"
    ),
    "security": (
        "(safety OR security OR privacy OR \"adversarial attack\") "
        "AND (\"autonomous vehicle\" OR \"connected vehicle\") "
        "NOT survey NOT review"
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
# Read from environment variables, with fallback to defaults for local testing
# 从环境变量读取，本地测试时有默认值回退
ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "19092277")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "HoLB2EnPj4PpHo1gQ65qy2aw")
MAX_RESULTS_PER_CATEGORY = 10  # 每个类别最多获取论文数
START_DATE = "2023-01-01"  # 起始日期


async def collect_papers_for_category(
    category: str,
    query: str,
    collection_key: str
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
    print(f"{'='*60}")

    try:
        # Initialize collector with specific collection
        # 初始化采集器，指定集合
        collector = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=collection_key
        )

        # Configure search parameters
        # 配置搜索参数
        search_params = ArxivSearchParams(
            keywords=[query],
            max_results=MAX_RESULTS_PER_CATEGORY
        )

        # Run collection
        # 执行采集
        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=True
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
    print("\n" + "="*60)
    print("ArXiv论文自动采集系统")
    print("Auto Paper Collection System")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"采集类别数: {len(QUERY_MAP)}")
    print(f"每类最多论文数: {MAX_RESULTS_PER_CATEGORY}")
    print(f"起始日期: {START_DATE}")

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

        successful, failed = await collect_papers_for_category(
            category=category,
            query=query,
            collection_key=collection_key
        )

        results[category] = {
            "successful": successful,
            "failed": failed,
            "collection_key": collection_key
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
    print("\n" + "="*60)
    print("采集完成！Collection Summary")
    print("="*60)
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

    print("\n" + "="*60)


if __name__ == "__main__":
    # Run the async main function
    # 运行异步主函数
    asyncio.run(main())
