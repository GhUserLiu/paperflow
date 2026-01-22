# 测试指南 | Testing Guide

本文档说明 arxiv-zotero-connector 的测试结构和运行方式。

This document explains the testing structure and how to run tests for arxiv-zotero-connector.

---

## 📁 测试目录结构 | Test Directory Structure

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和共享 fixtures
├── README.md                # 本文档
│
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_duplicate_detection.py  # 查重功能测试
│   ├── test_imports.py             # 导入测试
│   ├── test_clients/               # 客户端测试（待补充）
│   │   ├── test_arxiv_client.py
│   │   ├── test_chinaxiv_client.py
│   │   ├── test_openalex_client.py
│   │   └── test_zotero_client.py
│   ├── test_core/                  # 核心逻辑测试（待补充）
│   │   ├── test_connector.py
│   │   ├── test_paper_processor.py
│   │   └── test_search_params.py
│   └── test_utils/                 # 工具类测试（待补充）
│       ├── test_journal_ranker.py
│       ├── test_pdf_manager.py
│       └── test_metadata_mapper.py
│
├── integration/              # 集成测试
│   ├── __init__.py
│   ├── test_full_workflow.py       # 完整工作流测试（待补充）
│   ├── test_bilingual_search.py    # 双语搜索测试（待补充）
│   └── test_openalex_ranking.py    # OpenAlex 排序测试（待补充）
│
└── fixtures/                 # 测试数据和 mock
    ├── sample_papers.json          # 示例论文数据（待补充）
    ├── mock_responses.py           # API 响应 mock（待补充）
    └── test_config.yaml            # 测试配置（待补充）
```

---

## 🚀 运行测试 | Running Tests

### 安装测试依赖

```bash
pip install pytest pytest-cov pytest-asyncio
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 带输出详细信息
pytest -v

# 带覆盖率报告
pytest --cov=arxiv_zotero --cov-report=html
```

### 运行特定测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行特定文件
pytest tests/unit/test_clients/test_arxiv_client.py

# 运行特定测试函数
pytest tests/unit/test_clients/test_arxiv_client.py::test_search_arxiv

# 运行标记的测试
pytest -m unit          # 仅单元测试
pytest -m integration   # 仅集成测试
pytest -m "not slow"    # 排除慢速测试
```

### 测试选项

```bash
# 并行运行（需要 pytest-xdist）
pytest -n auto

# 失败时停止
pytest -x

# 显示本地变量
pytest -l

# 跳过慢速测试
pytest -m "not slow"
```

---

## ✅ 测试覆盖 | Test Coverage

### 当前状态

| 模块 | 单元测试 | 集成测试 | 状态 |
|------|---------|---------|------|
| clients/ | ❌ | ❌ | 待补充 |
| core/ | ❌ | ✅ | 部分 |
| utils/ | ❌ | ❌ | 待补充 |
| config/ | ✅ | ❌ | 导入测试 |

### 目标覆盖率

- **整体**: 80% 以上
- **核心模块**: 90% 以上
- **工具模块**: 70% 以上

---

## 📝 编写测试 | Writing Tests

### 单元测试示例

```python
# tests/unit/test_clients/test_arxiv_client.py
import pytest
from arxiv_zotero.clients.arxiv_client import ArxivClient
from arxiv_zotero.core.search_params import ArxivSearchParams


class TestArxivClient:
    """ArxivClient 测试"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.client = ArxivClient()

    def test_search_arxiv(self, mock_arxiv_response):
        """测试 arXiv 搜索"""
        params = ArxivSearchParams(
            keywords=["autonomous driving"],
            max_results=10
        )

        results = self.client.search_arxiv(params)

        assert len(results) > 0
        assert results[0]["title"] is not None

    def test_extract_metadata(self):
        """测试元数据提取"""
        # 测试代码
        pass
```

### 集成测试示例

```python
# tests/integration/test_full_workflow.py
import pytest
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams


@pytest.mark.integration
@pytest.mark.slow
class TestFullWorkflow:
    """完整工作流集成测试"""

    def test_search_and_save(self, mock_env_vars):
        """测试完整搜索和保存流程"""
        collector = ArxivZoteroCollector(
            zotero_library_id="test_id",
            zotero_api_key="test_key",
            collection_key="test_collection"
        )

        search_params = ArxivSearchParams(
            keywords=["machine learning"],
            max_results=5
        )

        successful, failed = await collector.run_collection_async(
            search_params=search_params,
            download_pdfs=False,  # 测试时不下载 PDF
            use_all_sources=False
        )

        assert successful > 0
        assert failed == 0
```

### 使用 Fixtures

```python
def test_with_fixtures(sample_paper_data, sample_openalex_metrics):
    """使用 fixtures 的测试"""
    assert sample_paper_data["title"] is not None
    assert sample_openalex_metrics["h_index"] > 0
```

### Mock 外部 API

```python
from unittest.mock import patch, MagicMock


@patch('arxiv_zotero.clients.arxiv_client.requests.get')
def test_with_mock(mock_get):
    """使用 mock 的测试"""
    # 配置 mock 响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<arxiv>...</arxiv>"
    mock_get.return_value = mock_response

    # 执行测试
    client = ArxivClient()
    results = client.search_arxiv(params)

    # 验证
    assert mock_get.called
    assert len(results) > 0
```

---

## 🏷️ 测试标记 | Test Markers

本项目使用以下 pytest 标记：

| 标记 | 说明 | 示例 |
|------|------|------|
| `unit` | 单元测试（快速，无网络） | `@pytest.mark.unit` |
| `integration` | 集成测试（慢速，可能需要网络） | `@pytest.mark.integration` |
| `slow` | 慢速测试（需要外部 API） | `@pytest.mark.slow` |

### 使用标记

```python
@pytest.mark.unit
def test_fast_calculation():
    """快速单元测试"""
    assert 1 + 1 == 2


@pytest.mark.integration
@pytest.mark.slow
def test_api_integration():
    """集成测试（需要网络）"""
    # 测试代码
    pass
```

---

## 🧪 CI/CD 集成 | CI/CD Integration

### GitHub Actions 示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=arxiv_zotero

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📚 测试最佳实践 | Best Practices

### 1. 测试命名

- 使用描述性名称：`test_search_arxiv_returns_results`
- 使用 `_` 分隔单词
- 以 `test_` 开头

### 2. 测试结构（AAA 模式）

```python
def test_something():
    # Arrange - 准备测试数据和环境
    client = ArxivClient()
    params = ArxivSearchParams(keywords=["test"])

    # Act - 执行被测试的功能
    results = client.search_arxiv(params)

    # Assert - 验证结果
    assert len(results) > 0
```

### 3. 独立性

- 每个测试应该独立运行
- 不依赖其他测试的结果
- 使用 `setup_method` 和 `teardown_method`

### 4. 可读性

- 添加注释说明测试目的
- 使用有意义的断言消息
- 保持测试简洁

### 5. Mock 外部依赖

- Mock API 调用
- Mock 文件系统操作
- 使用测试数据而不是真实数据

---

## 🐛 调试测试 | Debugging Tests

### 运行单个测试

```bash
pytest tests/unit/test_clients/test_arxiv_client.py::TestArxivClient::test_search_arxiv -v
```

### 使用 pdb 调试

```python
def test_something():
    # 测试代码
    import pdb; pdb.set_trace()  # 设置断点
    assert something
```

### 查看详细输出

```bash
pytest -v -s
```

---

## 📈 改进计划 | Improvement Plan

### 短期（1-2 周）
- [ ] 补充核心模块的单元测试
- [ ] 添加 OpenAlex 客户端测试
- [ ] 添加错误处理测试

### 中期（1-2 月）
- [ ] 达到 80% 代码覆盖率
- [ ] 添加性能测试
- [ ] 添加端到端测试

### 长期（3-6 月）
- [ ] 自动化回归测试
- [ ] 压力测试
- [ ] 安全性测试

---

**最后更新**: 2026-01-22
