"""
测试配置 | Test Configuration

pytest 配置和共享 fixtures
"""

import os
import sys
from pathlib import Path

import pytest  # 必须在文件开头导入

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Pytest 配置"""
    import pytest

    # 自定义标记
    config.addinivalue_line("markers", "unit: 单元测试标记")
    config.addinivalue_line("markers", "integration: 集成测试标记")
    config.addinivalue_line("markers", "slow: 慢速测试标记（需要网络或外部API）")


@pytest.fixture(autouse=True)
def clear_env_before_tests(monkeypatch):
    """在每个测试前清除环境变量，防止 .env 文件干扰测试"""
    # 清除所有可能的环境变量
    for key in [
        "ZOTERO_LIBRARY_ID",
        "ZOTERO_API_KEY",
        "TEMP_COLLECTION_KEY",
        "ENABLE_CHINAXIV",
        "COLLECTION_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)

    yield


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    # 清除所有可能的环境变量
    for key in ["ZOTERO_LIBRARY_ID", "ZOTERO_API_KEY",
                "TEMP_COLLECTION_KEY", "ENABLE_CHINAXIV"]:
        monkeypatch.delenv(key, raising=False)

    # 设置测试环境变量
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_library_id")
    monkeypatch.setenv("ZOTERO_API_KEY", "test_api_key")
    monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection_key")

    yield

    # 清理会在 monkeypatch 自动完成


@pytest.fixture
def sample_paper_data():
    """示例论文数据"""
    return {
        "title": "Test Paper: Autonomous Driving",
        "authors": ["John Doe", "Jane Smith"],
        "summary": "This is a test paper about autonomous driving systems.",
        "published": "2026-01-22T00:00:00Z",
        "arxiv_id": "2401.12345",
        "doi": "10.1234/test.doi",
        "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf",
        "journal_ref": "Test Journal vol 123 pages 456-789",
    }


@pytest.fixture
def sample_openalex_metrics():
    """示例 OpenAlex 指标"""
    return {
        "cited_by_percentile": 95.5,
        "h_index": 250,
        "impact_factor": 14.255,
        "journal_name": "Nature",
        "source": "openalex_work_api",
    }


@pytest.fixture
def temp_cache_dir(tmp_path):
    """临时缓存目录"""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
