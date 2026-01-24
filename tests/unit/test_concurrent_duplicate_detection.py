"""
Concurrent Duplicate Detection Test

测试并发场景下的去重功能
验证同一批次中的重复论文能够被正确检测和跳过

Usage:
    python -m pytest tests/unit/test_concurrent_duplicate_detection.py -v
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from paperflow.clients.zotero_client import ZoteroClient


@pytest.mark.asyncio
async def test_concurrent_duplicate_detection():
    """
    测试并发场景下的去重功能

    场景: 同一批次中有两篇相同的论文同时被处理
    预期: 只有第一篇被创建，第二篇被检测为重复并跳过
    """

    # 创建 mock 客户端
    with patch("paperflow.clients.zotero_client.zotero.Zotero"):
        client = ZoteroClient(
            library_id="test_library",
            api_key="test_key",
            collection_key=None  # 不验证集合，避免 API 调用
        )

        # Mock zot.items 方法（模拟 Zotero 中没有重复）
        client.zot.items = MagicMock(return_value=[])

        # Mock zot.item_template 和 zot.create_items 方法
        client.zot.item_template = MagicMock(return_value={})
        client.zot.create_items = MagicMock(
            return_value={
                "successful": {
                    "0": {
                        "key": "TEST123"
                    }
                }
            }
        )

        # 测试数据：两篇相同的论文
        paper_metadata = {
            "archiveLocation": "2301.12345",  # arXiv ID
            "title": "Test Paper",
            "creators": [],
            "date": "2023-01-01",
        }

        # 第一次创建（应该成功）
        item_key_1 = client.create_item("journalArticle", paper_metadata.copy())
        assert item_key_1 == "TEST123"
        assert "2301.12345" in client._created_papers
        assert client._created_papers["2301.12345"] == "archiveLocation"

        # 检查去重（应该检测到本次运行中的重复）
        duplicate_key = client.check_duplicate(
            identifier="2301.12345",
            identifier_field="archiveLocation",
            collection_only=False
        )
        assert duplicate_key == "RUNTIME_DUPLICATE"

        # 第二次创建（即使 mock 仍然返回成功，去重也应该阻止）
        # 注意：在实际使用中，process_paper 会在 check_duplicate 返回后就跳过


def test_created_papers_tracking():
    """
    测试 _created_papers 集合的跟踪功能
    """
    with patch("paperflow.clients.zotero_client.zotero.Zotero"):
        client = ZoteroClient(
            library_id="test_library",
            api_key="test_key"
        )

        # Mock zot 方法
        client.zot.item_template = MagicMock(return_value={})
        client.zot.create_items = MagicMock(
            return_value={
                "successful": {
                    "0": {"key": "ITEM1"}
                }
            }
        )

        # 测试 arXiv ID 记录
        metadata1 = {
            "archiveLocation": "cs.AI/2301.00001",
            "title": "Test 1",
            "creators": [],
        }
        client.create_item("journalArticle", metadata1)
        assert "cs.AI/2301.00001" in client._created_papers

        # 测试 DOI 记录
        metadata2 = {
            "DOI": "10.1234/test.doi",
            "title": "Test 2",
            "creators": [],
        }
        client.create_item("journalArticle", metadata2)
        assert "10.1234/test.doi" in client._created_papers

        # 测试 ChinaXiv ID 记录
        metadata3 = {
            "extra": "ChinaXiv ID: CX2023010001\nOther info",
            "title": "Test 3",
            "creators": [],
        }
        client.create_item("journalArticle", metadata3)
        assert "CX2023010001" in client._created_papers

        # 验证所有记录
        assert len(client._created_papers) == 3
        assert client._created_papers["cs.AI/2301.00001"] == "archiveLocation"
        assert client._created_papers["10.1234/test.doi"] == "DOI"
        assert client._created_papers["CX2023010001"] == "extra"


def test_check_duplicate_order():
    """
    测试去重检查的优先级顺序
    1. 本次运行已创建 (_created_papers)
    2. 缓存中的论文
    3. Zotero 库中的论文
    """
    with patch("paperflow.clients.zotero_client.zotero.Zotero"):
        client = ZoteroClient(
            library_id="test_library",
            api_key="test_key"
        )

        # Mock zot 方法
        client.zot.item_template = MagicMock(return_value={})
        client.zot.create_items = MagicMock(
            return_value={
                "successful": {
                    "0": {"key": "NEWITEM"}
                }
            }
        )
        client.zot.items = MagicMock(return_value=[])

        # 先添加到本次运行集合
        metadata = {
            "archiveLocation": "2301.99999",
            "title": "Test",
            "creators": [],
        }
        client.create_item("journalArticle", metadata)

        # 验证去重顺序：
        # 1. 首先检查 _created_papers（应该立即返回，不调用 API）
        client.zot.items.assert_not_called()

        duplicate = client.check_duplicate(
            identifier="2301.99999",
            identifier_field="archiveLocation"
        )

        # 应该返回本次运行重复的标记
        assert duplicate == "RUNTIME_DUPLICATE"

        # 仍然不应该调用 API（因为已经在 _created_papers 中找到）
        client.zot.items.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
