# Tests - 测试指南

PaperFlow 项目测试文档。

## 🚀 快速开始

```bash
# 安装测试依赖
pip install -e ".[test]"

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=paperflow --cov-report=html
```

## 📁 测试结构

```
tests/
├── unit/           # 单元测试
│   ├── test_clients/      # 客户端测试
│   ├── test_core/         # 核心逻辑测试
│   └── test_utils/        # 工具类测试
└── integration/    # 集成测试
```

## 🧪 运行特定测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行特定文件
pytest tests/unit/test_clients/test_arxiv_client.py

# 运行特定测试函数
pytest tests/unit/test_clients/test_arxiv_client.py::test_search_arxiv

# 排除慢速测试
pytest -m "not slow"
```

## 📊 测试标记

| 标记 | 说明 |
|------|------|
| `unit` | 单元测试（快速） |
| `integration` | 集成测试（慢速） |
| `slow` | 需要外部 API |

## 📚 相关文档

- [主 README](../README.md)
- [脚本文档](../scripts/README.md)
