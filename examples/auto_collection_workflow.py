#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端模式示例 | Cloud Mode Collection Example

运行方式 | Usage:
    cd examples
    python auto_collection_workflow.py

功能 | Features:
    - 多研究方向分类（5个类别）
    - 每个方向独立集合
    - 批量采集和统计

适用场景 | Use Cases:
    - 云端定时任务（配合 cron 或 GitHub Actions）
    - 批量历史数据采集
    - 多研究方向并行管理

环境要求 | Requirements:
    - 设置环境变量：ZOTERO_LIBRARY_ID, ZOTERO_API_KEY
    - 配置各研究方向的 collection_key

文档 | Documentation: ../README.md
"""

import asyncio
from datetime import datetime

from paperflow import ArxivSearchParams, ArxivZoteroCollector


async def auto_collection_example():
    """
    云端模式采集示例（类似于 scripts/run_auto_collection.py）
    """

    import os

    ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "your_library_id")
    ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "your_api_key")

    # 定义研究方向和集合
    research_areas = {
        "general": {
            "collection_key": "your_general_collection",
            "keywords": ["autonomous driving", "intelligent vehicles"],
        },
        "perception": {
            "collection_key": "your_perception_collection",
            "keywords": ["computer vision", "object detection"],
        },
        "decision": {
            "collection_key": "your_decision_collection",
            "keywords": ["reinforcement learning", "decision making"],
        },
        "control": {
            "collection_key": "your_control_collection",
            "keywords": ["vehicle control", "path planning"],
        },
        "communication": {
            "collection_key": "your_communication_collection",
            "keywords": ["V2X communication", "connected vehicles"],
        },
    }

    print("=" * 60)
    print("云端模式采集示例 | Cloud Mode Collection Example")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"研究方向: {len(research_areas)} 个")
    print("=" * 60 + "\n")

    total_success = 0
    total_failed = 0

    # 遍历所有研究方向
    for area_name, area_config in research_areas.items():
        print(f"\n{'='*60}")
        print(f"研究方向: {area_name}")
        print(f"集合: {area_config['collection_key']}")
        print(f"关键词: {', '.join(area_config['keywords'])}")
        print(f"{'='*60}\n")

        # 初始化采集器
        collector = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=area_config["collection_key"],
        )

        try:
            # 配置搜索参数
            search_params = ArxivSearchParams(keywords=area_config["keywords"], max_results=25)

            # 执行采集
            successful, failed = await collector.run_manual_collection_async(
                search_params=search_params, download_pdfs=True, use_all_sources=False
            )

            total_success += successful
            total_failed += failed

            print(f"\n{area_name} 结果: 成功 {successful}, 失败 {failed}")

        except Exception as e:
            print(f"\n{area_name} 错误: {e}")
            total_failed += 1

    # 总结
    print(f"\n{'='*60}")
    print("采集完成 | Collection Complete")
    print(f"{'='*60}")
    print(f"总成功: {total_success}")
    print(f"总失败: {total_failed}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(auto_collection_example())
