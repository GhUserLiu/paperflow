"""
测试重复检测修复
"""

import asyncio
import logging
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_duplicate_detection():
    """测试重复检测功能"""

    # 配置
    zotero_library_id = "19092277"
    zotero_api_key = "HoLB2EnPj4PpHo1gQ65qy2aw"
    collection_key = "LRML5CDJ"  # general collection

    # 搜索参数 - 少量论文用于测试
    search_params = ArxivSearchParams(
        keywords=['"autonomous driving" AND perception'],
        max_results=3,
        categories=["cs.CV", "cs.RO"]
    )

    # 创建 collector
    collector = ArxivZoteroCollector(
        zotero_library_id=zotero_library_id,
        zotero_api_key=zotero_api_key,
        collection_key=collection_key
    )

    print("=" * 70)
    print("重复检测修复测试")
    print("=" * 70)
    print()

    # 第一次运行 - 应该添加论文
    print("[第一次运行] - 添加论文到 Zotero...")
    print("-" * 70)

    successful_1, failed_1 = await collector.run_collection_async(
        search_params=search_params,
        download_pdfs=False  # 跳过 PDF 以加快测试
    )

    print()
    print(f"第一次运行结果:")
    print(f"  成功: {successful_1} 篇")
    print(f"  失败: {failed_1} 篇")
    print()

    # 等待一下
    await asyncio.sleep(2)

    # 第二次运行 - 应该跳过重复
    print("[第二次运行] - 检查重复...")
    print("-" * 70)

    successful_2, failed_2 = await collector.run_collection_async(
        search_params=search_params,
        download_pdfs=False
    )

    print()
    print(f"第二次运行结果:")
    print(f"  成功: {successful_2} 篇 (应该都是被跳过的重复)")
    print(f"  失败: {failed_2} 篇")
    print()

    # 验证结果
    print("=" * 70)
    print("验证结果")
    print("=" * 70)

    if successful_2 == successful_1 and failed_2 == 0:
        print("✓ 成功: 重复检测正常工作!")
        print(f"  所有 {successful_2} 篇论文都被识别为重复并跳过。")
        result = True
    else:
        print("✗ 失败: 重复检测可能存在问题。")
        print(f"  期望: {successful_1} 成功, 0 失败")
        print(f"  实际: {successful_2} 成功, {failed_2} 失败")
        result = False

    # 清理
    await collector.close()

    return result

if __name__ == "__main__":
    result = asyncio.run(test_duplicate_detection())
    exit(0 if result else 1)
