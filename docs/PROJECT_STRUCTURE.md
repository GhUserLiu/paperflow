# 项目结构 | Project Structure

## 目录概览 | Directory Overview

```
arxiv-zotero-connector/
├── arxiv_zotero/              # 主包目录
│   ├── __init__.py           # 包初始化
│   ├── __main__.py           # 命令行入口
│   ├── cli.py                # CLI 实现
│   ├── clients/              # API 客户端
│   │   ├── arxiv_client.py   # arXiv API 客户端
│   │   ├── chinaxiv_client.py # ChinaXiv API 客户端
│   │   ├── openalex_client.py # OpenAlex API 客户端
│   │   └── zotero_client.py  # Zotero API 客户端
│   ├── config/               # 配置模块
│   │   ├── arxiv_config.py   # arXiv 配置
│   │   ├── bilingual_config.py # 双语关键词配置
│   │   └── metadata_config.py # 元数据处理配置
│   ├── core/                # 核心功能
│   │   ├── connector.py      # 主连接器
│   │   ├── paper_processor.py # 论文处理
│   │   └── search_params.py  # 搜索参数
│   └── utils/               # 工具模块
│       ├── config_loader.py  # 配置加载器
│       ├── credentials.py    # 凭证管理
│       ├── errors.py        # 错误处理
│       ├── journal_ranker.py # 期刊排序
│       ├── pdf_manager.py   # PDF 管理
│       ├── performance.py   # 性能监控
│       └── summarizer.py    # AI 摘要
├── scripts/                 # 脚本工具
│   ├── auto_collect.py      # 自动采集脚本
│   ├── preload_journal_cache.py # 缓存预加载
│   └── search_papers.py     # 论文搜索脚本
├── tests/                   # 测试
│   ├── unit/                # 单元测试
│   │   ├── test_arxiv_client.py
│   │   ├── test_journal_ranker.py
│   │   ├── test_performance.py
│   │   └── ...
│   ├── integration/          # 集成测试
│   └── conftest.py          # pytest 配置
├── config/                  # 配置文件
│   ├── bilingual_keywords.yaml
│   └── journal_metrics_cache.json
├── docs/                    # 文档
│   ├── ARCHITECTURE.md      # 架构文档
│   ├── IMPROVEMENTS.md      # 改进记录
│   └── PROJECT_STRUCTURE.md # 本文件
├── examples/                # 使用示例
│   ├── basic_usage.py
│   └── auto_collection_workflow.py
├── .env.example             # 环境变量模板
├── pyproject.toml          # 项目配置
├── setup.py                # 安装脚本
└── README.md               # 主文档
```

## 模块说明 | Module Descriptions

### 客户端模块 (clients/)
- **arxiv_client.py**: arXiv API 交互，论文搜索和元数据提取
- **chinaxiv_client.py**: ChinaXiv API 交互，中文论文检索
- **openalex_client.py**: OpenAlex API 交互，期刊指标查询
- **zotero_client.py**: Zotero API 交互，论文上传和管理

### 核心模块 (core/)
- **connector.py**: 主连接器，协调各组件完成论文采集流程
- **paper_processor.py**: 论文处理，去重、排序、PDF下载
- **search_params.py**: 搜索参数封装，支持多源查询

### 工具模块 (utils/)
- **config_loader.py**: 统一配置加载，验证环境变量
- **credentials.py**: 凭证管理，安全存储和加载
- **errors.py**: 自定义异常，错误处理装饰器
- **journal_ranker.py**: 基于多指标的论文排序
- **pdf_manager.py**: PDF 下载和处理
- **performance.py**: 性能监控，统计分析
- **summarizer.py**: AI 驱动的论文摘要生成

### 脚本工具 (scripts/)
- **auto_collect.py**: 定时任务脚本，自动采集多方向论文
- **search_papers.py**: 交互式论文搜索工具
- **preload_journal_cache.py**: 预加载期刊指标缓存

## 设计模式 | Design Patterns

### 1. 策略模式 (Strategy Pattern)
- 不同数据源的客户端实现统一接口
- `ArxivClient`, `ChinaXivClient`, `OpenAlexClient`

### 2. 装饰器模式 (Decorator Pattern)
- 性能监控: `@monitor_performance`, `@timeit`
- 错误重试: `@retry_on_error`
- 错误处理: `@ignore_error`

### 3. 工厂模式 (Factory Pattern)
- 配置加载: `ConfigLoader.load_zotero_config()`
- 客户端创建: 在 `Connector` 中按需创建

### 4. 单例模式 (Singleton Pattern)
- 全局性能监控器: `get_global_monitor()`

## 数据流 | Data Flow

```
用户请求 (CLI/脚本)
    ↓
Connector (主协调器)
    ↓
    ├─→ ArxivClient ──→ arXiv API
    ├─→ ChinaXivClient ──→ ChinaXiv API
    └─→ OpenAlexClient ──→ OpenAlex API (可选)
    ↓
PaperProcessor (处理论文)
    ├─→ 去重检查
    ├─→ OpenAlex 排序 (可选)
    └─→ ZoteroClient ──→ Zotero API
    ↓
完成: 上传到 Zotero 集合
```

## 扩展指南 | Extension Guide

### 添加新的数据源
1. 在 `clients/` 中创建新的客户端类
2. 实现统一的搜索接口
3. 在 `Connector` 中注册

### 添加新的排序算法
1. 在 `utils/` 中创建新的排序器
2. 实现评分接口
3. 集成到 `PaperProcessor`

### 添加新的脚本
1. 在 `scripts/` 中创建脚本
2. 使用 `ConfigLoader` 加载配置
3. 可选: 添加性能监控装饰器
