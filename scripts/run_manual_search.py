#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Mode: Flexible arXiv Paper Search Script
本地模式：灵活的 arXiv 论文搜索脚本

运行在本地电脑，按需手动搜索论文（区别于云端自动采集模式）
Run on local machine for manual on-demand paper searching (distinct from cloud auto-collection)

用法 | Usage:
    # 搜索自动驾驶相关论文（默认20篇）
    python run_manual_search.py --keywords "autonomous driving"

    # 深度学习和计算机视觉
    python run_manual_search.py --keywords '"deep learning" AND "computer vision"'

    # 指定结果数量
    python run_manual_search.py --keywords "V2X communication" --max-results 50

    # 只搜索元数据，不下载 PDF
    python run_manual_search.py --keywords "reinforcement learning" --no-pdf
"""

import argparse
import asyncio
import io
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
from dotenv import load_dotenv
ENV_FILE = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_FILE)

from paperflow.utils.collection_logger import CollectionLogger

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Fix Windows encoding issue
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from paperflow import ArxivSearchParams, ArxivZoteroCollector
from paperflow.utils import ConfigLoader
from paperflow.utils.errors import ConfigError


def validate_keywords(keywords: str) -> str:
    """验证搜索关键词的合法性和长度"""
    if not keywords or not keywords.strip():
        raise ValueError("关键词不能为空")

    keywords = keywords.strip()

    # 长度验证
    if len(keywords) > 500:
        raise ValueError(f"关键词过长（最多500字符，当前: {len(keywords)}字符）")

    # 检查潜在的注入攻击字符
    dangerous_chars = [";", "\n", "\r", "\x00", "\x1a"]
    if any(char in keywords for char in dangerous_chars):
        raise ValueError("关键词包含非法字符（不允许: ; \\n \\r 等）")

    return keywords


def validate_max_results(max_results: int) -> int:
    """验证最大结果数"""
    if max_results < 1:
        raise ValueError("max-results 必须大于 0")
    if max_results > 1000:
        raise ValueError("max-results 不能超过 1000（API 限制）")
    return max_results


def validate_collection_key(collection_key: Optional[str]) -> Optional[str]:
    """验证集合 KEY"""
    if collection_key is None:
        return None

    collection_key = collection_key.strip()
    if not collection_key:
        raise ValueError("集合 KEY 不能为空字符串")

    # Zotero collection keys 通常是 uppercase alphanumeric
    if not collection_key.replace("_", "").replace("-", "").isalnum():
        print(f"⚠️  警告: 集合 KEY '{collection_key}' 格式可能不正确")

    return collection_key


def load_config():
    """加载并验证配置"""
    try:
        config = ConfigLoader.load_zotero_config()
        return (
            config["library_id"],
            config["api_key"],
            config["collection_key"],
            config["enable_chinaxiv"],
        )
    except ConfigError as e:
        print(f"\n❌ 配置错误: {e}")
        print("\n💡 快速配置:")
        print("   1. 复制 .env.example 到 .env:")
        print("      cp .env.example .env")
        print("   2. 在 .env 中填入你的 Zotero 凭证:")
        print("      ZOTERO_LIBRARY_ID=your_library_id")
        print("      ZOTERO_API_KEY=your_api_key")
        print("      TEMP_COLLECTION_KEY=your_collection_key")
        print("   3. 重新运行程序\n")
        sys.exit(1)


def _estimate_cache_hit_rate(enable_openalex_ranking: bool) -> float:
    """
    估算 OpenAlex 缓存命中率

    Args:
        enable_openalex_ranking: 是否启用 OpenAlex 排序

    Returns:
        估算的缓存命中率 (0.0-1.0)
    """
    from paperflow.clients.openalex_client import OpenAlexClient

    if not enable_openalex_ranking:
        return 0.0

    try:
        client = OpenAlexClient()
        cache_file = client.cache_file

        # 检查缓存文件是否存在和大小
        if not cache_file.exists():
            return 0.0  # 无缓存，首次运行

        # 检查缓存文件大小（估算命中率）
        size_mb = cache_file.stat().st_size / (1024 * 1024)

        # 基于缓存文件大小的经验估算
        # < 0.1 MB: 约 10% 命中率（新缓存）
        # 0.1-1 MB: 约 50% 命中率
        # > 1 MB: 约 80% 命中率（成熟缓存）

        if size_mb < 0.1:
            return 0.1
        elif size_mb < 1.0:
            return 0.5
        else:
            return 0.8

    except Exception:
        return 0.0  # 保守估算：无缓存


async def search_papers(
    keywords: str,
    max_results: int = 20,
    download_pdfs: bool = True,
    collection_key: Optional[str] = None,
    enable_chinaxiv: bool = False,
    chinaxiv_keywords: Optional[str] = None,
    enable_openalex_ranking: bool = False,
    openalex_weights: Optional[dict] = None,
    target_results: Optional[int] = None,
    collection_only_dupcheck: bool = False,
    auto_preload: bool = True,
):
    """
    搜索并保存论文到指定集合

    Args:
        keywords: 搜索关键词
        max_results: 最大结果数（默认 20）
        download_pdfs: 是否下载 PDF
        collection_key: 目标集合 KEY（默认 temp 集合）
        enable_chinaxiv: 是否启用 ChinaXiv 来源
        chinaxiv_keywords: ChinaXiv 中文关键词（可选，默认使用 keywords）
        enable_openalex_ranking: 是否启用 OpenAlex 期刊指标排序
        openalex_weights: OpenAlex 指标权重配置
        target_results: 目标保存数量（自动补充到该数量）
        collection_only_dupcheck: 是否仅在目标集合内查重
        auto_preload: 是否自动预热缓存（默认 True）
    """
    # Load configuration
    ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, _, _ = load_config()

    print("\n" + "=" * 70)
    print("论文灵活搜索工具 | Flexible Search")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if enable_chinaxiv:
        # 双语模式
        chinaxiv_kw = chinaxiv_keywords if chinaxiv_keywords else keywords
        print(f"🌏 双语模式: 在 arXiv 中使用中英关键词搜索")
        print(f"  📝 英文关键词: {keywords}")
        print(f"  📝 中文关键词: {chinaxiv_kw}")
        print(f"  📊 每种语言上限: 30 篇，总上限: 60 篇")
        print(f"  🔍 数据来源: arXiv（去重合并）")
    else:
        # 单语模式
        print(f"搜索关键词: {keywords}")
        print(f"最大结果数: {max_results}")
        print(f"数据来源: arXiv")

    if target_results:
        print(f"目标保存数量: {target_results}（自动补充）")
    print(f"目标集合: {collection_key} (temp)")
    print(f"OpenAlex 排序: {'启用' if enable_openalex_ranking else '禁用'}")
    if enable_openalex_ranking and openalex_weights:
        print(f"  权重配置: {openalex_weights}")
    print(f"查重模式: {'集合内（更快）' if collection_only_dupcheck else '全局（更安全）'}")
    print(f"下载 PDF: {'是' if download_pdfs else '否'}")
    print("=" * 70 + "\n")

    try:
        # Initialize collector with ChinaXiv and OpenAlex support
        # 初始化采集器（支持 ChinaXiv 和 OpenAlex）
        collector = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=collection_key,
            enable_chinaxiv=enable_chinaxiv,
            enable_openalex_ranking=enable_openalex_ranking,
            openalex_weights=openalex_weights,
            collection_only_dupcheck=collection_only_dupcheck,
        )

        # 自动预热缓存（如果启用 OpenAlex 且缓存为空）
        if enable_openalex_ranking and auto_preload:
            from paperflow.clients.openalex_client import OpenAlexClient

            print("🔄 检查 OpenAlex 缓存状态...")
            openalex_client = OpenAlexClient()

            # 检查是否需要预热
            should_preload = False
            if not openalex_client.cache_file.exists():
                print("   📭 缓存文件不存在，首次运行")
                should_preload = True
            else:
                size_mb = openalex_client.cache_file.stat().st_size / (1024 * 1024)
                if size_mb < 0.01:  # 小于 10KB 视为空缓存
                    print(f"   📭 缓存文件为空 ({size_mb:.3f} MB)")
                    should_preload = True
                else:
                    print(f"   ✅ 缓存已存在 ({size_mb:.2f} MB)")

            # 执行预热
            if should_preload:
                print("\n🚀 自动预热常见期刊缓存（提升后续查询速度）...")
                print("   预计耗时: 15-30 秒（仅首次运行）\n")

                openalex_client.auto_preload_common_journals(silent=False)

                # 显示缓存大小
                if openalex_client.cache_file.exists():
                    new_size_mb = openalex_client.cache_file.stat().st_size / (1024 * 1024)
                    print(f"\n✅ 缓存预热完成！当前缓存大小: {new_size_mb:.2f} MB")
                    print("   后续查询将使用缓存，速度提升 70-90%\n")
                else:
                    print("\n⚠️  缓存预热可能未完全成功，但不影响继续使用\n")

            # 清理客户端
            openalex_client.close()

        # 自动补充逻辑（智能策略）
        if target_results:
            # 智能补充策略：基于缓存命中率动态调整初始搜索数量
            cache_hit_rate = _estimate_cache_hit_rate(enable_openalex_ranking)

            if cache_hit_rate > 0.5:
                # 高缓存命中率（>50%）：初始搜索 1.2倍
                multiplier = 1.2
                strategy = "高缓存命中率"
            elif cache_hit_rate > 0.2:
                # 中等缓存命中率（20-50%）：初始搜索 1.5倍
                multiplier = 1.5
                strategy = "中等缓存命中率"
            else:
                # 低缓存命中率（<20%）或首次运行：初始搜索 2.0倍
                multiplier = 2.0
                strategy = "低缓存命中率（首次运行）"

            initial_results = int(max_results * multiplier)
            print(f"📊 智能补充模式：{strategy}")
            print(f"   初始搜索: {initial_results} 篇")
            print(f"   目标保存: {target_results} 篇")
            print(f"   预估缓存命中率: {cache_hit_rate * 100:.0f}%\n")

            # Configure search parameters with initial results
            search_params = ArxivSearchParams(keywords=[keywords], max_results=initial_results)

            print(f"正在搜索论文来源...")
            print(f"提示: 本地模式，不影响云端自动采集\n")

            # Run collection with multi-source support
            # 执行采集（支持多来源）
            successful, failed = await collector.run_manual_collection_async(
                search_params=search_params,
                download_pdfs=download_pdfs,
                use_all_sources=enable_chinaxiv,  # 启用多来源搜索
                chinaxiv_keywords=chinaxiv_keywords,  # ChinaXiv 中文关键词
            )

            # 检查是否需要补充
            if successful < target_results:
                print(f"\n⚠️  当前保存 {successful} 篇，目标是 {target_results} 篇")
                print(f"正在补充更多论文...")

                # 智能补充：动态调整补充数量
                # 如果第一次搜索成功率很低，增加补充数量
                success_rate = successful / initial_results
                if success_rate < 0.3:
                    # 成功率很低（<30%），可能是重复率高，大幅增加补充
                    additional_multiplier = 3
                elif success_rate < 0.6:
                    # 成功率中等（30-60%），适度增加补充
                    additional_multiplier = 2
                else:
                    # 成功率较高（>60%），少量补充
                    additional_multiplier = 1.5

                needed = target_results - successful
                additional_results = min(int(needed * additional_multiplier), 100)  # 最多再搜100篇

                print(f"补充搜索: 再搜索 {additional_results} 篇\n")

                # 新的搜索参数（避免重复）
                search_params补充 = ArxivSearchParams(
                    keywords=[keywords], max_results=additional_results
                )

                # 继续采集
                additional_successful, additional_failed = (
                    await collector.run_manual_collection_async(
                        search_params=search_params补充,
                        download_pdfs=download_pdfs,
                        use_all_sources=enable_chinaxiv,
                    )
                )

                successful += additional_successful
                failed += additional_failed

                if successful >= target_results:
                    print(f"\n✅ 已达到目标数量: {successful} 篇")
                else:
                    print(f"\n⚠️  已尽力补充，当前: {successful} 篇（可能遇到重复或API限制）")
            else:
                print(f"\n✅ 已达到目标数量: {successful} 篇")
        else:
            # 配置搜索参数（无日期过滤 - 获取最新论文）
            # 配置搜索参数（无日期过滤 - 获取最新论文）
            search_params = ArxivSearchParams(keywords=[keywords], max_results=max_results)

            print(f"正在搜索论文来源...")
            print(f"提示: 本地模式，不影响云端自动采集\n")

            # Run collection with multi-source support
            # 执行采集（支持多来源）
            successful, failed = await collector.run_manual_collection_async(
                search_params=search_params,
                download_pdfs=download_pdfs,
                use_all_sources=enable_chinaxiv,  # 启用多来源搜索
                chinaxiv_keywords=chinaxiv_keywords,  # ChinaXiv 中文关键词
            )

        print(f"\n{'=' * 70}")
        print("搜索完成 | Search Complete")
        print(f"{'=' * 70}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n总计:")
        print(f"  成功采集: {successful} 篇")
        print(f"  失败: {failed} 篇")
        print(f"  保存位置: Temp 集合 ({collection_key})")
        print("\n提示: 重复检测已启用，已存在的论文会被跳过")
        print("=" * 70 + "\n")

        return successful, failed

    except Exception as e:
        print(f"\n❌ 错误 | Error: {e}")
        import traceback

        traceback.print_exc()
        return 0, 0


async def main():
    """主函数 - 命令行接口"""
    # 加载配置（移除硬编码密钥）
    ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, TEMP_COLLECTION_KEY, ENABLE_CHINAXIV = load_config()

    parser = argparse.ArgumentParser(
        description="本地模式：灵活的 arXiv 论文搜索工具",
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

  # 显式下载 PDF（默认行为，可省略 --pdf 参数）
  python search_papers.py --keywords "deep learning" --pdf

  # 启用 OpenAlex 期刊指标排序
  python search_papers.py --keywords "deep learning" --enable-openalex

  # 自定义 OpenAlex 权重
  python search_papers.py --keywords "neural networks" --enable-openalex \\
    --openalex-weights '{"cited_by_percentile": 0.7, "h_index": 0.2, "impact_factor": 0.1}'

  # 双语模式：在 arXiv 中使用中英关键词搜索
  # 英文关键词搜索 30 篇 + 中文关键词搜索 30 篇，去重后总上限 60 篇
  python search_papers.py --keywords "autonomous driving" --chinaxiv-keywords "自动驾驶" -x

  # 双语模式：相同的中英关键词
  python search_papers.py --keywords "自动驾驶" --enable-chinaxiv

  # 目标数量自动补充（初始搜索 75 篇，确保保存 50 篇）
  python search_papers.py --keywords "deep learning" --max-results 50 --target-results 50

  # 集合内查重（更快，适合单一集合使用）
  python search_papers.py --keywords "autonomous driving" --collection-only-dupcheck

  # 禁用自动缓存预热（如果已有缓存）
  python search_papers.py --keywords "deep learning" --enable-openalex --no-auto-preload

注意 | Notes:
  - 本地模式，不影响云端自动采集（scripts/run_auto_collection.py）
  - 保存到 Temp 集合（AQNIN4ZZ），与云端模式分开
  - 重复检测已启用，自动跳过已存在的论文
  - 双语模式（--enable-chinaxiv）：在 arXiv 中使用中英关键词分别搜索，总上限60篇，自动去重
  - 使用 --chinaxiv-keywords 指定中文关键词（不指定则使用相同关键词）
  - PDF 下载：默认启用（--pdf），使用 --no-pdf 仅保存元数据
  - OpenAlex 排序按期刊影响力指标综合评分，优先显示高质量论文
  - 自动预热：启用 OpenAlex 时首次运行会自动预加载常见期刊缓存（15-30秒）
  - 如需禁用自动预热，使用 --no-auto-preload 参数
        """,
    )

    parser.add_argument(
        "--keywords", "-k", type=str, help='搜索关键词（例如: "autonomous driving"）'
    )

    parser.add_argument(
        "--chinaxiv-keywords",
        "-z",
        type=str,
        help="中文关键词（双语模式：在 arXiv 中使用中英关键词分别搜索）",
    )

    parser.add_argument(
        "--max-results",
        "-m",
        type=int,
        default=50,
        metavar="N",
        help="最大结果数（默认: 50，手动模式）",
    )

    parser.add_argument(
        "--pdf",
        "-p",
        dest="download_pdf",
        action="store_true",
        help="下载 PDF 文件（默认启用）",
    )

    parser.add_argument(
        "--no-pdf",
        "-n",
        dest="download_pdf",
        action="store_false",
        help="不下载 PDF 文件（仅保存元数据）",
    )

    # 设置默认值为 True（下载PDF）
    parser.set_defaults(download_pdf=True)

    parser.add_argument(
        "--collection",
        "-c",
        type=str,
        default=None,
        help="目标集合 KEY（默认: TEMP_COLLECTION_KEY 环境变量）",
    )

    parser.add_argument(
        "--enable-chinaxiv",
        "-x",
        action="store_true",
        help="启用双语模式（使用中英关键词在 arXiv 中分别搜索，总上限60篇）",
    )

    parser.add_argument(
        "--enable-openalex",
        "-e",
        action="store_true",
        help="启用 OpenAlex 期刊指标排序（手动模式推荐，默认启用）",
    )

    parser.add_argument(
        "--no-openalex",
        action="store_true",
        help="禁用 OpenAlex 排序（覆盖默认启用）",
    )

    parser.add_argument(
        "--openalex-weights",
        "-w",
        type=str,
        help='OpenAlex 指标权重配置（JSON 格式，例如: \'{"cited_by_percentile": 0.5, "h_index": 0.3, "impact_factor": 0.2}\'）',
    )

    parser.add_argument(
        "--target-results",
        "-t",
        type=int,
        metavar="N",
        help="目标保存数量（自动补充到该数量，例如: --target-results 50）",
    )

    parser.add_argument(
        "--collection-only-dupcheck",
        "-d",
        action="store_true",
        help="仅在该集合内查重（更快，但允许跨集合重复）",
    )

    parser.add_argument(
        "--no-auto-preload",
        action="store_true",
        help="禁用自动缓存预热（默认：启用 OpenAlex 时自动预热）",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：显示将要执行的操作但不实际执行",
    )

    args = parser.parse_args()

    # 验证参数
    if not args.keywords:
        parser.error(
            '必须提供 --keywords 参数\n示例: python search_papers.py --keywords "autonomous driving"'
        )

    # 输入验证
    try:
        args.keywords = validate_keywords(args.keywords)
        args.max_results = validate_max_results(args.max_results)
        args.collection = validate_collection_key(args.collection)
    except ValueError as e:
        parser.error(f"参数验证失败: {e}")

    # 使用默认 collection_key 如果未指定
    if args.collection is None:
        args.collection = TEMP_COLLECTION_KEY

    # 手动模式默认启用 OpenAlex 排序（除非用户明确禁用）
    if not args.no_openalex and not args.enable_openalex:
        args.enable_openalex = True

    # 解析 OpenAlex 权重配置
    openalex_weights = None
    if args.openalex_weights:
        try:
            import json

            openalex_weights = json.loads(args.openalex_weights)
            # 验证权重总和
            total_weight = sum(openalex_weights.values())
            if abs(total_weight - 1.0) > 0.01:
                print(f"警告: 权重总和为 {total_weight}，将自动归一化")
        except json.JSONDecodeError:
            parser.error("--openalex-weights 必须是有效的 JSON 格式")
        except Exception as e:
            parser.error(f"解析权重配置失败: {e}")

    # Dry-run 模式：显示配置但不执行
    if args.dry_run:
        if RICH_AVAILABLE:
            console = Console()
            console.print("\n[bold cyan]🔍 Dry-Run 预览模式[/bold cyan]\n")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("配置项", style="cyan", width=30)
            table.add_column("值", style="yellow")

            table.add_row("搜索关键词", args.keywords)
            table.add_row("最大结果数", str(args.max_results))
            table.add_row("下载 PDF", "是" if args.download_pdf else "否")
            table.add_row("目标集合", args.collection)
            table.add_row(
                "启用 ChinaXiv", "是" if args.enable_chinaxiv or ENABLE_CHINAXIV else "否"
            )
            table.add_row("启用 OpenAlex", "是" if args.enable_openalex else "否")
            if args.enable_openalex and openalex_weights:
                table.add_row("OpenAlex 权重", str(openalex_weights))
            if args.target_results:
                table.add_row("目标保存数量", str(args.target_results))
            table.add_row("集合内查重", "是" if args.collection_only_dupcheck else "否")
            table.add_row(
                "自动预热缓存", "否" if args.no_auto_preload else "是（如果启用 OpenAlex）"
            )

            console.print(table)
            console.print(
                "\n[dim]💡 这是预览模式，不会实际执行操作。去掉 --dry-run 参数以运行程序。[/dim]\n"
            )
        else:
            print("\n🔍 Dry-Run 预览模式\n")
            print(f"搜索关键词: {args.keywords}")
            print(f"最大结果数: {args.max_results}")
            print(f"下载 PDF: {'是' if args.download_pdf else '否'}")
            print(f"目标集合: {args.collection}")
            print(f"启用 ChinaXiv: {'是' if args.enable_chinaxiv or ENABLE_CHINAXIV else '否'}")
            print(f"启用 OpenAlex: {'是' if args.enable_openalex else '否'}")
            if args.enable_openalex and openalex_weights:
                print(f"OpenAlex 权重: {openalex_weights}")
            if args.target_results:
                print(f"目标保存数量: {args.target_results}")
            print(f"集合内查重: {'是' if args.collection_only_dupcheck else '否'}")
            print(f"自动预热缓存: {'否' if args.no_auto_preload else '是（如果启用 OpenAlex）'}")
            print("\n💡 这是预览模式，不会实际执行操作。去掉 --dry-run 参数以运行程序。\n")

        sys.exit(0)

    # 运行搜索
    collector_instance = None
    try:
        # Initialize logger
        collector_instance = ArxivZoteroCollector(
            zotero_library_id=ZOTERO_LIBRARY_ID,
            zotero_api_key=ZOTERO_API_KEY,
            collection_key=CollectionLogger.LOG_COLLECTION_KEY,  # Use log collection
        )
        logger = CollectionLogger(collector_instance.zotero_client)
        logger.start_timer()

        successful, failed = await search_papers(
            keywords=args.keywords,
            max_results=args.max_results,
            download_pdfs=args.download_pdf,
            collection_key=args.collection,
            enable_chinaxiv=args.enable_chinaxiv or ENABLE_CHINAXIV,
            chinaxiv_keywords=args.chinaxiv_keywords,
            enable_openalex_ranking=args.enable_openalex,
            openalex_weights=openalex_weights,
            target_results=args.target_results,
            collection_only_dupcheck=args.collection_only_dupcheck,
            auto_preload=not args.no_auto_preload,
        )

        # Generate and upload log
        print("\n生成日志文件...")
        source_stats = {
            "arxiv": {
                "found": successful + failed,
                "successful": successful,
                "duplicates": 0,
                "failed": failed,
            },
            "chinaxiv": {
                "found": 0,
                "successful": 0,
                "duplicates": 0,
                "failed": 0,
            },  # TODO: Track separately
        }
        log_content = logger.generate_manual_log(
            keywords=args.keywords,
            max_results=args.max_results,
            download_pdfs=args.download_pdf,
            openalex_enabled=args.enable_openalex,
            openalex_stats=None,  # TODO: Collect stats
            source_stats=source_stats,
        )
        log_filename = logger.generate_filename(mode="manual")

        if await logger.upload_to_zotero(log_content, log_filename):
            print(f"✓ 日志已上传到 Zotero: {log_filename}")
        else:
            print(f"✗ 日志上传失败: {log_filename}")

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
    finally:
        if collector_instance:
            await collector_instance.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            # Handle cases where event loop is already running (e.g., in IDE)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise
