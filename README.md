# PaperFlow

> 智能论文采集工具 - 从 arXiv 搜索、下载 PDF 并保存到 Zotero 库

[![CI/CD](https://img.shields.io/badge/CI-CD-success-green)](.github/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-2.1.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ 核心功能

- 🔍 **智能搜索** - 关键词、分类、作者、日期范围多维度搜索
- 📥 **自动下载** - 自动下载并附加 PDF 到 Zotero
- 🎯 **期刊排序** - OpenAlex 期刊指标智能排序（影响力优先）
- 🤖 **AI 摘要** - 可选的 AI 驱动论文摘要
- ☁️ **云端模式** - GitHub Actions 定时自动采集最新论文
- 💻 **本地模式** - 手动搜索特定主题文献
- 🎨 **精美 CLI** - Rich 库美化终端输出
- 📊 **搜索分析** - 实时统计和搜索建议

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

获取 API Key: <https://www.zotero.org/settings/keys>

### 使用

```bash
# 本地模式 - 手动搜索论文
python scripts/run_manual_search.py -k "deep learning"

# 启用期刊排序（高质量优先）
python scripts/run_manual_search.py -k "computer vision" -e

# 双语模式：在 arXiv 中使用中英关键词搜索
python scripts/run_manual_search.py -k "autonomous driving" -z "自动驾驶" -x

# 仅保存元数据，不下载 PDF
python scripts/run_manual_search.py -k "neural networks" --no-pdf

# 更多结果
python scripts/run_manual_search.py -k "neural networks" -m 50

# 预览模式
python scripts/run_manual_search.py -k "quantum" --dry-run
```

## 📖 数据源策略

### 主要数据源：arXiv

PaperFlow 主要使用 **arXiv** 作为数据源，原因如下：

- ✅ **完善的 REST API** - 无需认证，稳定可靠
- ✅ **国际覆盖** - 涵盖全球最新研究，包括中文研究者论文
- ✅ **高质量内容** - 严格的审核机制，确保论文质量
- ✅ **丰富元数据** - 提供完整的引用信息、分类、DOI 等
- ✅ **持续更新** - 每日新增数百篇论文

### 关于中文预印本平台

经过技术评估，目前主流中文预印本平台（ChinaXiv、SinoXiv、PubScholar）存在以下限制：

- ❌ **API 限制** - 需要认证令牌或无公开 API
- ❌ **动态渲染** - 页面通过 JavaScript 动态加载，无法直接抓取
- ❌ **访问限制** - 部分平台需要登录或机构访问权限

**建议**：使用 arXiv 即可获取大量高质量的中英文研究论文。如需中文文献，建议：
1. 在 arXiv 中使用中文关键词搜索（许多中国研究者也在 arXiv 发表）
2. 手动访问中文预印本平台进行补充搜索

---

## 📖 两种运行模式

PaperFlow 支持两种运行模式，满足不同场景需求：

### ☁️ 云端模式（自动采集）

- **脚本**: `run_auto_collection.py`
- **部署**: GitHub Actions 定时任务
- **功能**: 每日自动采集 5 个研究方向的最新论文
- **保存位置**: 按分类保存到 5 个对应的 Zotero 集合
- **数据源**: arXiv
- **优势**: 无需本地运行，自动化更新

### 💻 本地模式（手动搜索）

- **脚本**: `run_manual_search.py`
- **运行**: 本地电脑手动执行
- **功能**: 按需搜索特定主题的论文
- **保存位置**: 统一保存到临时集合 `AQNIN4ZZ`
- **数据源**: arXiv（默认最多 60 篇）
- **优势**: 灵活可控，支持预览和自定义参数

## 🔧 GitHub Secrets 配置（云端模式）

在 **Settings → Secrets and variables → Actions** 中添加：

| Secret | 说明 | 获取方式 |
|--------|------|---------|
| `ZOTERO_LIBRARY_ID` | Zotero Library ID | [设置页面](https://www.zotero.org/settings/keys) |
| `ZOTERO_API_KEY` | Zotero API 密钥 | [设置页面](https://www.zotero.org/settings/keys) |

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

**项目名称**: PaperFlow | **版本**: v2.2.0 | **更新**: 2026-02-26 | **状态**: ✅ 活跃维护
