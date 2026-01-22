#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例 | Basic Usage Example

运行方式 | Usage:
    cd examples
    python basic_usage.py

功能 | Features:
    - 基础搜索：简单的 arXiv 论文搜索
    - 高级搜索：带 OpenAlex 期刊排序的搜索
    - 双语搜索：同时从 arXiv 和 ChinaXiv 检索

环境要求 | Requirements:
    - 设置环境变量：ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, TEMP_COLLECTION_KEY
    - 或修改脚本中的默认值

文档 | Documentation: ../README.md
"""

import asyncio
import os
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams


async def basic_search_example():
    """基础搜索示例"""

    # 配置你的 Zotero 凭证
    ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "your_library_id")
    ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "your_api_key")
    TEMP_COLLECTION_KEY = os.getenv("TEMP_COLLECTION_KEY", "your_collection_key")

    print("="*60)
    print("基础搜索示例 | Basic Search Example")
    print("="*60)

    # 初始化采集器
    collector = ArxivZoteroCollector(
        zotero_library_id=ZOTERO_LIBRARY_ID,
        zotero_api_key=ZOTERO_API_KEY,
        collection_key=TEMP_COLLECTION_KEY
    )

    try:
        # 配置搜索参数
        search_params = ArxivSearchParams(
            keywords=["autonomous driving"],
            max_results=10
        )

        print(f"\n正在搜索: {search_params.keywords[0]}")
        print(f"最大结果数: {search_params.max_results}\n")

        # 执行采集
        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=True,
            use_all_sources=False  # 仅 arXiv
        )

        print(f"\n结果:")
        print(f"  成功: {successful}")
        print(f"  失败: {failed}")

    finally:
        # 清理资源
        if collector.openalex_client:
            collector.openalex_client.close()


async def advanced_search_example():
    """高级搜索示例（带 OpenAlex 排序）"""

    ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "your_library_id")
    ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "your_api_key")
    TEMP_COLLECTION_KEY = os.getenv("TEMP_COLLECTION_KEY", "your_collection_key")

    print("\n" + "="*60)
    print("高级搜索示例（OpenAlex 排序）| Advanced Search with OpenAlex")
    print("="*60)

    # 自定义 OpenAlex 权重
    custom_weights = {
        'cited_by_percentile': 0.7,  # 被引百分位权重 70%
        'h_index': 0.2,               # h 指数权重 20%
        'impact_factor': 0.1          # 影响因子权重 10%
    }

    # 初始化采集器（启用 OpenAlex 排序）
    collector = ArxivZoteroCollector(
        zotero_library_id=ZOTERO_LIBRARY_ID,
        zotero_api_key=ZOTERO_API_KEY,
        collection_key=TEMP_COLLECTION_KEY,
        enable_openalex_ranking=True,
        openalex_weights=custom_weights
    )

    try:
        # 搜索参数
        search_params = ArxivSearchParams(
            keywords=["deep learning"],
            max_results=20
        )

        print(f"\n正在搜索: {search_params.keywords[0]}")
        print(f"OpenAlex 排序: 已启用")
        print(f"自定义权重: {custom_weights}\n")

        # 执行采集
        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=True,
            use_all_sources=False
        )

        print(f"\n结果:")
        print(f"  成功: {successful}")
        print(f"  失败: {failed}")

    finally:
        if collector.openalex_client:
            collector.openalex_client.close()


async def bilingual_search_example():
    """双语搜索示例（arXiv + ChinaXiv）"""

    ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "your_library_id")
    ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "your_api_key")
    TEMP_COLLECTION_KEY = os.getenv("TEMP_COLLECTION_KEY", "your_collection_key")

    print("\n" + "="*60)
    print("双语搜索示例（arXiv + ChinaXiv）| Bilingual Search")
    print("="*60)

    # 初始化采集器（启用 ChinaXiv）
    collector = ArxivZoteroCollector(
        zotero_library_id=ZOTERO_LIBRARY_ID,
        zotero_api_key=ZOTERO_API_KEY,
        collection_key=TEMP_COLLECTION_KEY,
        enable_chinaxiv=True
    )

    try:
        # 搜索参数（中英文）
        search_params = ArxivSearchParams(
            keywords=["智能网联汽车"],
            max_results=15
        )

        print(f"\n正在搜索: {search_params.keywords[0]}")
        print(f"数据来源: arXiv + ChinaXiv\n")

        # 执行采集（启用多来源）
        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=True,
            use_all_sources=True  # 启用多来源搜索
        )

        print(f"\n结果:")
        print(f"  成功: {successful}")
        print(f"  失败: {failed}")

    finally:
        if collector.openalex_client:
            collector.openalex_client.close()


if __name__ == "__main__":
    print("""
选择示例 | Choose an example:
  1. 基础搜索 | Basic search
  2. 高级搜索（OpenAlex 排序）| Advanced search with OpenAlex
  3. 双语搜索（arXiv + ChinaXiv）| Bilingual search
    """)

    choice = input("输入选项 (1-3) | Enter option (1-3): ").strip()

    if choice == "1":
        asyncio.run(basic_search_example())
    elif choice == "2":
        asyncio.run(advanced_search_example())
    elif choice == "3":
        asyncio.run(bilingual_search_example())
    else:
        print("无效选项 | Invalid option")
