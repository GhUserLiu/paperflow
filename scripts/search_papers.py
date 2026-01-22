#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵活的 arXiv 论文搜索脚本（独立于每日定时任务）
Flexible arXiv Paper Search Script (Independent from Daily Tasks)

用法 | Usage:
    # 搜索自动驾驶相关论文（默认20篇）
    python search_papers.py --keywords "autonomous driving"

    # 深度学习和计算机视觉
    python search_papers.py --keywords '"deep learning" AND "computer vision"'

    # 指定结果数量
    python search_papers.py --keywords "V2X communication" --max-results 50

    # 只搜索元数据，不下载 PDF
    python search_papers.py --keywords "reinforcement learning" --no-pdf
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Optional
import argparse
import io

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

# 配置
ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "19092277")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "HoLB2EnPj4PpHo1gQ65qy2aw")
TEMP_COLLECTION_KEY = "AQNIN4ZZ"  # temp 集合


async def search_papers(
    keywords: str,
    max_results: int = 20,
    download_pdfs: bool = True,
    collection_key: str = TEMP_COLLECTION_KEY
):
    """
    搜索并保存论文到指定集合

    Args:
        keywords: 搜索关键词
        max_results: 最大结果数（默认 20）
        download_pdfs: 是否下载 PDF
        collection_key: 目标集合 KEY（默认 temp 集合）
    """
    print("\n" + "="*70)
    print("arXiv 论文灵活搜索工具 | Flexible Search")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"搜索关键词: {keywords}")
    print(f"最大结果数: {max_results}")
    print(f"目标集合: {collection_key} (temp)")
    print(f"下载 PDF: {'是' if download_pdfs else '否'}")
    print("="*70 + "\n")

    try:
        # Initialize collector
        collector = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=collection_key
        )

        # Configure search parameters (no date filter - get latest papers)
        # 配置搜索参数（无日期过滤 - 获取最新论文）
        search_params = ArxivSearchParams(
            keywords=[keywords],
            max_results=max_results
        )

        print(f"正在搜索 arXiv...")
        print(f"提示: 这是独立的搜索脚本，不影响每日定时任务\n")

        # Run collection
        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=download_pdfs
        )

        print(f"\n{'='*70}")
        print("搜索完成 | Search Complete")
        print(f"{'='*70}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n总计:")
        print(f"  成功采集: {successful} 篇")
        print(f"  失败: {failed} 篇")
        print(f"  保存位置: Temp 集合 ({collection_key})")
        print("\n提示: 重复检测已启用，已存在的论文会被跳过")
        print("="*70 + "\n")

        return successful, failed

    except Exception as e:
        print(f"\n❌ 错误 | Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='灵活的 arXiv 论文搜索工具（独立脚本）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 | Examples:
  # 搜索自动驾驶相关论文（默认20篇）
  python search_papers.py --keywords "autonomous driving"

  # 深度学习和计算机视觉
  python search_papers.py --keywords '"deep learning" AND "computer vision"'

  # 指定结果数量
  python search_papers.py --keywords "V2X communication" --max-results 50

  # 只搜索元数据，不下载 PDF
  python search_papers.py --keywords "reinforcement learning" --no-pdf

注意 | Notes:
  - 这是独立的搜索脚本，不影响 scripts/auto_collect.py
  - 保存到 Temp 集合，与定时任务分开
  - 重复检测已启用，自动跳过已存在的论文
        """
    )

    parser.add_argument(
        '--keywords',
        type=str,
        help='搜索关键词（例如: "autonomous driving"）'
    )

    parser.add_argument(
        '--max-results',
        type=int,
        default=20,
        metavar='N',
        help='最大结果数（默认: 20）'
    )

    parser.add_argument(
        '--no-pdf',
        action='store_true',
        help='不下载 PDF 文件'
    )

    parser.add_argument(
        '--collection',
        type=str,
        default=TEMP_COLLECTION_KEY,
        help=f'目标集合 KEY（默认: {TEMP_COLLECTION_KEY} - temp集合）'
    )

    args = parser.parse_args()

    # 验证参数
    if not args.keywords:
        parser.error("必须提供 --keywords 参数\n示例: python search_papers.py --keywords \"autonomous driving\"")

    # 运行搜索
    try:
        successful, failed = asyncio.run(search_papers(
            keywords=args.keywords,
            max_results=args.max_results,
            download_pdfs=not args.no_pdf,
            collection_key=args.collection
        ))

        # 根据结果设置退出码
        if failed > 0:
            sys.exit(1)  # 有失败的情况
        else:
            sys.exit(0)  # 全部成功

    except KeyboardInterrupt:
        print("\n\n操作已取消 | Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误 | Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
