# API Usage Guide | API 使用指南

本文档提供 arxiv-zotero-connector 的详细 API 使用示例和最佳实践。

## 目录 | Table of Contents

1. [快速开始](#快速开始)
2. [核心 API](#核心-api)
3. [高级功能](#高级功能)
4. [错误处理](#错误处理)
5. [最佳实践](#最佳实践)

---

## 快速开始

### 基本论文搜索

```python
import asyncio
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

async def main():
    # 初始化采集器
    collector = ArxivZoteroCollector(
        zotero_library_id="your_library_id",
        zotero_api_key="your_api_key",
        collection_key="your_collection_key"
    )

    # 配置搜索参数
    search_params = ArxivSearchParams(
        keywords=["machine learning"],
        max_results=10,
        categories=["cs.AI", "cs.LG"]
    )

    # 执行采集
    successful, failed = await collector.run_manual_collection_async(
        search_params=search_params,
        download_pdfs=True
    )

    print(f"成功: {successful}, 失败: {failed}")

    # 清理资源
    await collector.close()

asyncio.run(main())
```

---

## 核心 API

### ArxivZoteroCollector

主要的论文采集器类。

#### 初始化参数

```python
collector = ArxivZoteroCollector(
    zotero_library_id: str,           # Zotero library ID (必需)
    zotero_api_key: str,              # Zotero API key (必需)
    collection_key: str = None,       # 目标集合 key (可选)
    enable_chinaxiv: bool = False,    # 启用 ChinaXiv (默认: False)
    enable_openalex_ranking: bool = False,  # 启用 OpenAlex 排序 (默认: False)
    openalex_weights: Dict = None,    # OpenAlex 权重配置 (可选)
    collection_only_dupcheck: bool = False  # 集合内查重 (默认: False)
)
```

#### 主要方法

##### search_arxiv()

搜索 arXiv 论文。

```python
papers = collector.search_arxiv(search_params)
```

**参数:**
- `search_params`: ArxivSearchParams 对象

**返回:**
- `List[Dict]`: 论文元数据列表

---

##### search_all_sources()

搜索所有启用的来源（arXiv 和 ChinaXiv）。

```python
papers = collector.search_all_sources(search_params)
```

**注意:** 需要启用 `enable_chinaxiv=True` 才会搜索 ChinaXiv。

---

##### run_manual_collection_async()

异步执行论文采集。

```python
successful, failed = await collector.run_manual_collection_async(
    search_params: ArxivSearchParams,
    download_pdfs: bool = True,
    use_all_sources: bool = False
)
```

**参数:**
- `search_params`: 搜索参数
- `download_pdfs`: 是否下载 PDF (默认: True)
- `use_all_sources`: 是否使用所有来源 (默认: False)

**返回:**
- `Tuple[int, int]`: (成功数量, 失败数量)

---

##### rank_papers_with_openalex()

使用 OpenAlex 期刊指标对论文排序。

```python
ranked_papers = collector.rank_papers_with_openalex(papers)
```

**评分算法:**
- `cited_by_percentile` (50%): 论文引用百分位
- `h_index` (30%): 期刊 h 指数
- `impact_factor` (20%): 期刊影响因子

**返回:**
- `List[Dict]`: 添加了 `openalex_score` 字段的论文列表

---

### ArxivSearchParams

搜索参数配置类。

```python
search_params = ArxivSearchParams(
    keywords: List[str] = None,        # 搜索关键词列表
    title_search: str = None,          # 标题搜索
    categories: List[str] = None,      # arXiv 分类
    start_date: datetime = None,       # 开始日期
    end_date: datetime = None,         # 结束日期
    author: str = None,                # 作者名
    content_type: str = None,          # 内容类型
    max_results: int = 20              # 最大结果数
)
```

**使用示例:**

```python
from datetime import datetime, timedelta

# 搜索最近一周的 AI 论文
search_params = ArxivSearchParams(
    keywords=["deep learning"],
    categories=["cs.AI"],
    start_date=datetime.now() - timedelta(days=7),
    max_results=50
)
```

---

## 高级功能

### OpenAlex 排序

启用期刊影响力指标排序：

```python
collector = ArxivZoteroCollector(
    zotero_library_id="your_library_id",
    zotero_api_key="your_api_key",
    enable_openalex_ranking=True
)

# 自定义权重
custom_weights = {
    "cited_by_percentile": 0.7,  # 70%
    "h_index": 0.2,               # 20%
    "impact_factor": 0.1          # 10%
}

collector = ArxivZoteroCollector(
    zotero_library_id="your_library_id",
    zotero_api_key="your_api_key",
    enable_openalex_ranking=True,
    openalex_weights=custom_weights
)
```

**注意事项:**
- 首次运行会自动预加载常见期刊缓存（15-30秒）
- 缓存文件保存在 `config/journal_metrics_cache.json`
- 后续查询使用缓存，速度提升 70-90%

---

### 双语采集

为不同来源使用不同关键词：

```python
successful, failed = await collector.run_auto_collection_async(
    category="communication",  # 配置文件中的类别
    start_date=datetime.now() - timedelta(days=1),
    config_path="config/bilingual_config.yaml",
    download_pdfs=True
)
```

**配置文件示例:** (`config/bilingual_config.yaml`)

```yaml
sources:
  arxiv:
    enabled: true
    max_results: 20

  chinaxiv:
    enabled: true
    max_results: 10

categories:
  general:
    arxiv_keywords:
      - "artificial intelligence"
      - "machine learning"
    chinaxiv_keywords:
      - "人工智能"
      - "机器学习"
```

---

### 集合内查重

启用集合内查重模式，提升查重速度：

```python
collector = ArxivZoteroCollector(
    zotero_library_id="your_library_id",
    zotero_api_key="your_api_key",
    collection_key="your_collection",
    collection_only_dupcheck=True  # 仅在目标集合内查重
)
```

**性能对比:**
- 全局查重: 2-3 秒/次
- 集合内查重: 0.5-1 秒/次

**注意:** 集合内查重允许跨集合重复。

---

## 错误处理

### 常见异常类型

```python
from arxiv_zotero.utils.errors import (
    ConfigError,           # 配置错误
    PaperDownloadError,    # PDF 下载失败
    ZoteroUploadError,     # Zotero 上传失败
    DuplicatePaperError,   # 重复论文检测
    ZoteroConnectorError,  # 连接器错误
    APIError,              # API 调用错误
    OpenAlexError          # OpenAlex API 错误
)
```

### 错误处理示例

```python
import asyncio
import logging
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams
from arxiv_zotero.utils.errors import ConfigError, APIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        collector = ArxivZoteroCollector(
            zotero_library_id="your_library_id",
            zotero_api_key="your_api_key"
        )

        search_params = ArxivSearchParams(
            keywords=["quantum computing"],
            max_results=10
        )

        successful, failed = await collector.run_manual_collection_async(
            search_params=search_params
        )

        logger.info(f"采集完成: 成功 {successful}, 失败 {failed}")

    except ConfigError as e:
        logger.error(f"配置错误: {e}")
        logger.info("请检查 .env 文件中的凭证设置")

    except APIError as e:
        logger.error(f"API 调用失败: {e}")
        logger.info("请检查网络连接和 API 密钥")

    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        raise

    finally:
        if 'collector' in locals():
            await collector.close()

asyncio.run(main())
```

---

## 最佳实践

### 1. 资源清理

始终在完成后关闭 collector：

```python
try:
    collector = ArxivZoteroCollector(...)
    # 使用 collector
finally:
    await collector.close()
```

或使用异步上下文管理器（推荐）：

```python
async with ArxivZoteroCollector(...) as collector:
    # 使用 collector
    pass
# 自动清理
```

### 2. 并发控制

默认限制同时处理 5 篇论文，避免 API 速率限制：

```python
# 已内置并发控制，无需手动设置
successful, failed = await collector.run_manual_collection_async(
    search_params=search_params
)
```

### 3. 缓存利用

OpenAlex 排序会自动使用缓存，首次运行后后续查询会更快：

```python
# 首次运行：60-90 秒（冷启动）
ranked = collector.rank_papers_with_openalex(papers)

# 后续运行：1-2 秒（热启动）
ranked = collector.rank_papers_with_openalex(more_papers)
```

### 4. 批量处理

使用 `target_results` 自动补充到目标数量：

```python
search_params = ArxivSearchParams(
    keywords=["neural networks"],
    max_results=75  # 初始搜索数量
)

# 自动补充直到达到 50 篇
successful, failed = await collector.run_manual_collection_async(
    search_params=search_params,
    target_results=50
)
```

### 5. 错误重试

内置自动重试机制，无需手动实现：

```python
# API 调用失败会自动重试（指数退避，最多 3 次）
successful, failed = await collector.run_manual_collection_async(
    search_params=search_params
)
```

### 6. 日志记录

使用 Python logging 模块记录详细信息：

```python
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 日志文件位置: logs/arxiv_zotero.log
```

---

## 完整示例

### 示例 1: 基本论文采集

```python
import asyncio
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

async def collect_papers():
    collector = ArxivZoteroCollector(
        zotero_library_id="your_library_id",
        zotero_api_key="your_api_key"
    )

    search_params = ArxivSearchParams(
        keywords=["computer vision"],
        max_results=20
    )

    try:
        successful, failed = await collector.run_manual_collection_async(
            search_params=search_params,
            download_pdfs=True
        )
        print(f"采集完成: {successful} 篇成功, {failed} 篇失败")
    finally:
        await collector.close()

asyncio.run(collect_papers())
```

### 示例 2: 高质量论文优先

```python
import asyncio
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

async def collect_high_quality_papers():
    collector = ArxivZoteroCollector(
        zotero_library_id="your_library_id",
        zotero_api_key="your_api_key",
        enable_openalex_ranking=True  # 启用期刊排序
    )

    search_params = ArxivSearchParams(
        keywords=["deep learning"],
        max_results=50
    )

    try:
        # OpenAlex 排序会自动应用
        successful, failed = await collector.run_manual_collection_async(
            search_params=search_params
        )
        print(f"高质量论文优先采集完成: {successful} 篇")
    finally:
        await collector.close()

asyncio.run(collect_high_quality_papers())
```

### 示例 3: 双语采集

```python
import asyncio
from datetime import datetime, timedelta
from arxiv_zotero import ArxivZoteroCollector

async def bilingual_collection():
    collector = ArxivZoteroCollector(
        zotero_library_id="your_library_id",
        zotero_api_key="your_api_key",
        enable_chinaxiv=True
    )

    try:
        successful, failed = await collector.run_auto_collection_async(
            category="general",
            start_date=datetime.now() - timedelta(days=1),
            config_path="config/bilingual_config.yaml"
        )
        print(f"双语采集完成: {successful} 篇")
    finally:
        await collector.close()

asyncio.run(bilingual_collection())
```

---

## 更多资源

- **项目 README**: [README.md](../README.md)
- **优化建议**: [PROJECT_OPTIMIZATION_SUGGESTIONS.md](../PROJECT_OPTIMIZATION_SUGGESTIONS.md)
- **配置示例**: [config/bilingual_config.yaml](../config/bilingual_config.yaml.example)
- **Zotero API**: https://www.zotero.org/settings/keys
- **arXiv API**: https://info.arxiv.org/help/api/index.html
- **OpenAlex API**: https://docs.openalex.org/

---

**文档版本**: 2.1.0
**最后更新**: 2026-01-23
