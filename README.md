# arxiv-zotero-connector

> 自动化论文采集工具 - 从 arXiv 搜索、下载 PDF 并保存到 Zotero 库

[![CI/CD](https://img.shields.io/badge/CI-CD-success-green)](.github/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-2.1.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ 核心功能

- 🔍 **智能搜索** - 关键词、分类、作者、日期范围多维度搜索
- 📥 **自动下载** - 自动下载并附加 PDF 到 Zotero
- 🎯 **期刊排序** - OpenAlex 期刊指标智能排序（影响力优先）
- 🌏 **双语采集** - 支持 arXiv 和 ChinaXiv（中科院预印本）
- 🤖 **AI 摘要** - 可选的 AI 驱动论文摘要
- 🔄 **每日定时** - GitHub Actions 自动采集最新论文
- 🎨 **精美 CLI** - Rich 库美化终端输出

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/StepanKropachev/arxiv-zotero-connector.git
cd arxiv-zotero-connector
pip install -e .
```

### 配置

```bash
cp .env.example .env
# 编辑 .env，填入 Zotero 凭证
```

获取 API Key: https://www.zotero.org/settings/keys

### 使用

```bash
# 搜索论文
python scripts/search_papers.py -k "deep learning"

# 启用期刊排序（高质量优先）
python scripts/search_papers.py -k "computer vision" -e

# 更多结果
python scripts/search_papers.py -k "neural networks" -m 50

# 预览模式
python scripts/search_papers.py -k "quantum" --dry-run
```

## 📚 文档

- **[API 使用指南](docs/API_USAGE.md)** - 详细文档和示例
- **[系统架构](docs/ARCHITECTURE.md)** - 架构设计
- **[更新日志](CHANGELOG.md)** - 版本历史

## 💡 高级功能

### OpenAlex 排序

按期刊影响力排序（`cited_by_percentile`, `h_index`, `impact_factor`）：

```bash
python scripts/search_papers.py -k "machine learning" -e
```

### 双语采集

同时采集 arXiv（英文）和 ChinaXiv（中文）：

```bash
python scripts/search_papers.py -k "人工智能" -x
```

### 自定义权重

```bash
python scripts/search_papers.py -k "deep learning" -e \
  -w '{"cited_by_percentile": 0.7, "h_index": 0.2, "impact_factor": 0.1}'
```

## 🧪 开发

```bash
# 测试
pytest tests/ -v

# 性能测试
pytest tests/test_performance.py --benchmark

# 代码检查
black arxiv_zotero scripts tests
mypy arxiv_zotero --ignore-missing-imports
```

## 📊 项目结构

```
arxiv_zotero/
├── clients/       # API 客户端（arXiv, Zotero, OpenAlex）
├── config/        # 配置管理
├── core/          # 核心逻辑（采集器、处理器）
└── utils/         # 工具（缓存、装饰器等）
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**版本**: v2.1.0 | **更新**: 2026-01-23 | **状态**: ✅ 活跃维护
