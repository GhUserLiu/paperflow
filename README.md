# PaperFlow

> 自动化论文采集工具 - 从 arXiv/ChinaXiv 搜索、下载 PDF 并保存到 Zotero 库

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
git clone https://github.com/GhUserLiu/paperflow.git
cd paperflow
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
python scripts/run_manual_search.py -k "deep learning"

# 启用期刊排序（高质量优先）
python scripts/run_manual_search.py -k "computer vision" -e

# 更多结果
python scripts/run_manual_search.py -k "neural networks" -m 50

# 预览模式
python scripts/run_manual_search.py -k "quantum" --dry-run
```

### CLI 命令

```bash
# 使用 PaperFlow CLI
paperflow search --keywords "deep learning" --max-results 10
paperflow auto collect
```

## 🔧 GitHub Secrets 配置

在 **Settings → Secrets and variables → Actions** 中添加：

| Secret | 说明 | 获取方式 |
|--------|------|---------|
| `ZOTERO_LIBRARY_ID` | Zotero Library ID | [设置页面](https://www.zotero.org/settings/keys) |
| `ZOTERO_API_KEY` | Zotero API 密钥 | [设置页面](https://www.zotero.org/settings/keys) |
| `ENABLE_CHINAXIV` | 是否启用中文预印本 | `true` 或 `false` |

## 📚 文档

- **[更新日志](CHANGELOG.md)** - 版本历史
- **[脚本文档](scripts/README.md)** - 工具脚本说明
- **[测试文档](tests/README.md)** - 测试指南

## 🧪 开发

```bash
# 测试
pytest tests/ -v

# 代码检查
black paperflow scripts tests
mypy paperflow --ignore-missing-imports
```

## 📊 项目结构

```
paperflow/
├── clients/       # API 客户端（arXiv, Zotero, OpenAlex）
├── config/        # 配置管理
├── core/          # 核心逻辑（采集器、处理器）
└── utils/         # 工具（缓存、装饰器等）
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**项目名称**: PaperFlow | **版本**: v2.1.0 | **更新**: 2026-01-24 | **状态**: ✅ 活跃维护
