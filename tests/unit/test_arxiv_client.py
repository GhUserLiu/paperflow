"""
ArxivClient 单元测试 | ArxivClient Unit Tests
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
import pytz

from paperflow.clients.arxiv_client import ArxivClient
from paperflow.core.search_params import ArxivSearchParams


class TestArxivClient:
    """ArxivClient 测试"""

    def test_init(self):
        """测试初始化"""
        client = ArxivClient()
        assert client is not None
        assert client.client is not None
        # 验证客户端配置
        assert client.client.page_size == 100
        assert client.client.delay_seconds == 3
        assert client.client.num_retries == 5

    @patch("arxiv_zotero.clients.arxiv_client.arxiv.Client")
    def test_search_arxiv_success(self, mock_client_class):
        """测试成功搜索"""
        # 模拟 arxiv.Result 对象
        mock_result = Mock()
        mock_result.title = "Test Paper"
        mock_result.summary = "Test abstract"
        mock_result.published = datetime(2026, 1, 22, tzinfo=pytz.UTC)
        mock_result.entry_id = "http://arxiv.org/abs/2401.12345"
        mock_result.pdf_url = "http://arxiv.org/pdf/2401.12345.pdf"
        mock_result.primary_category = "cs.AI"
        mock_result.categories = ["cs.AI", "cs.LG"]
        mock_result.journal_ref = None
        mock_result.doi = None
        mock_result.comment = None
        mock_result.authors = [Mock(name="Test Author")]

        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.results.return_value = [mock_result]
        mock_client_class.return_value = mock_client_instance

        client = ArxivClient()
        # 替换客户端为模拟对象
        client.client = mock_client_instance

        params = ArxivSearchParams(keywords=["test"], max_results=10)

        results = client.search_arxiv(params)

        assert len(results) > 0
        assert results[0]["title"] == "Test Paper"
        assert results[0]["arxiv_id"] == "2401.12345"

    def test_filter_by_date_no_filter(self):
        """测试无日期过滤"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.published = datetime(2026, 1, 22, tzinfo=pytz.UTC)

        result = client.filter_by_date(mock_result, None, None)
        assert result is True

    def test_filter_by_date_within_range(self):
        """测试日期在范围内"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.published = datetime(2026, 1, 22, tzinfo=pytz.UTC)

        start_date = datetime(2026, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime(2026, 1, 31, tzinfo=pytz.UTC)

        result = client.filter_by_date(mock_result, start_date, end_date)
        assert result is True

    def test_filter_by_date_before_start(self):
        """测试日期在开始日期之前"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.published = datetime(2025, 12, 31, tzinfo=pytz.UTC)

        start_date = datetime(2026, 1, 1, tzinfo=pytz.UTC)

        result = client.filter_by_date(mock_result, start_date, None)
        assert result is False

    def test_filter_by_date_after_end(self):
        """测试日期在结束日期之后"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.published = datetime(2026, 2, 1, tzinfo=pytz.UTC)

        end_date = datetime(2026, 1, 31, tzinfo=pytz.UTC)

        result = client.filter_by_date(mock_result, None, end_date)
        assert result is False

    def test_filter_by_date_naive_datetime(self):
        """测试无时区的日期时间"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.published = datetime(2026, 1, 22, tzinfo=pytz.UTC)

        # 传入无时区的日期时间（应该假定为 UTC）
        start_date = datetime(2026, 1, 1)  # 无时区

        result = client.filter_by_date(mock_result, start_date, None)
        assert result is True

    def test_filter_by_content_type_no_filter(self):
        """测试无内容类型过滤"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.comment = None
        mock_result.journal_ref = None

        result = client.filter_by_content_type(mock_result, None)
        assert result is True

    def test_filter_by_content_type_journal(self):
        """测试期刊类型过滤"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.comment = None
        mock_result.journal_ref = "Nature vol 123 pages 456-789"

        result = client.filter_by_content_type(mock_result, "journal")
        assert result is True

    def test_filter_by_content_type_preprint(self):
        """测试预印本过滤"""
        client = ArxivClient()
        mock_result = Mock()
        mock_result.comment = None
        mock_result.journal_ref = None

        result = client.filter_by_content_type(mock_result, "preprint")
        assert result is True

    def test_filter_by_content_type_conference(self):
        """测试会议论文过滤"""
        client = ArxivClient()
        mock_result = Mock()
        # 添加 "conference" 关键词以匹配实现逻辑
        mock_result.comment = "Presented at CVPR 2024 conference"
        mock_result.journal_ref = None

        result = client.filter_by_content_type(mock_result, "conference")
        assert result is True

    def test_prepare_arxiv_metadata_success(self):
        """测试元数据准备成功"""
        mock_result = Mock()
        mock_result.title = "Test Paper"
        mock_result.summary = "Test abstract"
        mock_result.published = datetime(2026, 1, 22)
        mock_result.entry_id = "http://arxiv.org/abs/2401.12345v1"
        mock_result.pdf_url = "http://arxiv.org/pdf/2401.12345v1.pdf"
        mock_result.primary_category = "cs.AI"
        mock_result.categories = ["cs.AI", "cs.LG"]
        mock_result.journal_ref = "Test Journal 123:456-789"
        mock_result.doi = "10.1234/test.doi"
        mock_result.comment = "Test comment"

        mock_author = Mock()
        mock_author.name = "Test Author"
        mock_result.authors = [mock_author]

        client = ArxivClient()

        # 直接调用（使用 asyncio.run）
        import asyncio

        metadata = asyncio.run(client._prepare_arxiv_metadata(mock_result))

        assert metadata is not None
        assert metadata["title"] == "Test Paper"
        assert metadata["abstract"] == "Test abstract"
        assert metadata["arxiv_id"] == "2401.12345v1"
        assert metadata["authors"] == ["Test Author"]
        assert metadata["journal_ref"] == "Test Journal 123:456-789"
        assert metadata["doi"] == "10.1234/test.doi"
        assert metadata["comment"] == "Test comment"
        assert metadata["categories"] == ["cs.AI", "cs.LG"]

    def test_prepare_arxiv_metadata_error_handling(self):
        """测试元数据准备错误处理"""
        mock_result = Mock()
        # 设置一个会导致错误的属性
        mock_result.title = Mock(side_effect=Exception("Test error"))

        client = ArxivClient()

        # 直接调用
        import asyncio

        metadata = asyncio.run(client._prepare_arxiv_metadata(mock_result))

        # 应该返回 None 而不是抛出异常
        assert metadata is None

    @patch("arxiv_zotero.clients.arxiv_client.arxiv.Client")
    def test_search_arxiv_empty_results(self, mock_client_class):
        """测试空结果"""
        # 模拟空结果
        mock_client_instance = Mock()
        mock_client_instance.results.return_value = []
        mock_client_class.return_value = mock_client_instance

        client = ArxivClient()
        client.client = mock_client_instance

        params = ArxivSearchParams(keywords=["nonexistent"], max_results=10)

        results = client.search_arxiv(params)

        assert len(results) == 0

    @patch("arxiv_zotero.clients.arxiv_client.arxiv.Client")
    def test_search_arxiv_with_date_filter(self, mock_client_class):
        """测试带日期过滤的搜索"""
        mock_result = Mock()
        mock_result.title = "Recent Paper"
        mock_result.summary = "Recent abstract"
        mock_result.published = datetime(2026, 1, 22, tzinfo=pytz.UTC)
        mock_result.entry_id = "http://arxiv.org/abs/2401.99999"
        mock_result.pdf_url = "http://arxiv.org/pdf/2401.99999.pdf"
        mock_result.primary_category = "cs.CV"
        mock_result.categories = ["cs.CV"]
        mock_result.journal_ref = None
        mock_result.doi = None
        mock_result.comment = None
        mock_result.authors = [Mock(name="Author")]

        mock_client_instance = Mock()
        mock_client_instance.results.return_value = [mock_result]
        mock_client_class.return_value = mock_client_instance

        client = ArxivClient()
        client.client = mock_client_instance

        # 设置日期范围（过去7天）
        start_date = datetime.now(pytz.UTC) - timedelta(days=7)
        params = ArxivSearchParams(keywords=["recent"], start_date=start_date, max_results=10)

        results = client.search_arxiv(params)

        assert len(results) > 0
        assert results[0]["title"] == "Recent Paper"
