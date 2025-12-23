# ArXiv-Zotero Connector - 项目功能与特性总结

> 最后更新: 2025-12-23 | 版本: 0.1.0

---

## 1. 项目概述

**ArXiv-Zotero Connector** 是一个自动化文献管理系统，专门为研究人员设计，能够从 arXiv 自动采集最新研究论文，并智能分类同步到 Zotero 文献库。

### 核心价值
- 自动化论文采集流程，节省研究人员大量时间
- 智能分类管理，支持多研究方向
- 重复检测机制，避免文献重复
- 支持定时任务，保持文献库最新

---

## 2. 核心功能模块

### 2.1 论文采集与搜索 (ArxivClient + ArxivSearchParams)

#### 功能特性
- **多维度搜索**: 支持关键词、标题、作者、类别、日期范围等组合搜索
- **灵活查询**: 使用 arXiv API 查询语法，支持布尔运算符 (AND, OR, NOT)
- **批量采集**: 一次可采集最多数千篇论文
- **异步处理**: 使用 asyncio 实现并发下载，提升效率

#### ArxivSearchParams 参数说明

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `keywords` | List[str] | 通用关键词列表 | `["autonomous driving", "perception"]` |
| `title_search` | str | 标题精确搜索 | `"deep learning"` |
| `categories` | List[str] | arXiv 分类代码 | `["cs.AI", "cs.RO"]` |
| `start_date` | datetime | 起始日期过滤 | `datetime(2024, 1, 1)` |
| `end_date` | datetime | 结束日期过滤 | `datetime(2024, 12, 31)` |
| `author` | str | 作者姓名搜索 | `"Hinton"` |
| `content_type` | str | 内容类型过滤 | `"journal"` |
| `max_results` | int | 最大结果数 | `100` |

#### 示例代码

```python
from arxiv_zotero import ArxivSearchParams
from datetime import datetime

# 基础关键词搜索
params = ArxivSearchParams(
    keywords=['"autonomous driving" AND perception'],
    max_results=50
)

# 高级组合搜索
params = ArxivSearchParams(
    keywords=['"reinforcement learning"'],
    categories=['cs.AI', 'cs.LG'],
    start_date=datetime(2024, 1, 1),
    max_results=100
)
```

---

### 2.2 Zotero 集成 (ZoteroClient)

#### 功能特性
- **自动创建文献**: 将 arXiv 论文元数据转换为 Zotero 条目
- **集合管理**: 自动将论文分类到指定的 Zotero 集合
- **PDF 上传**: 自动下载并上传 PDF 作为附件
- **重复检测**: 基于 arXiv ID 检测重复文献
- **API 限流保护**: 内置请求速率限制，避免超出 Zotero API 配额

#### 核心方法

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `create_item()` | 创建 Zotero 条目 | `str` (item_key) |
| `add_to_collection()` | 添加到集合 | `bool` |
| `upload_attachment()` | 上传 PDF 附件 | `bool` |
| `check_duplicate()` | 检测重复文献 | `str` or `None` |
| `delete_item()` | 删除条目 | `bool` |
| `create_collection()` | 创建新集合 | `str` (collection_key) |

#### API 限制说明
- **文件上传**: 每 10 分钟 100 MB
- **其他请求**: 每 10 分钟 100 次
- **内置保护**: 自动请求限流，最小间隔 0.1 秒

---

### 2.3 重复检测机制

#### 工作原理
1. 提取论文的 arXiv ID
2. 在 Zotero 库的 `extra` 字段中搜索相同 ID
3. 如果找到匹配，跳过该论文
4. 记录日志说明已跳过

#### 实现细节
- arXiv ID 存储在 Zotero 条目的 `extra` 字段中
- 格式: `arXiv: ID` 或 `arXiv: ID` (支持两种格式)
- 检测在处理每篇论文前自动执行

#### 日志示例
```
INFO - Found duplicate arXiv ID 2512.19694v1 in item JZ8D33RW
INFO - Paper 2512.19694v1 already exists in library (item: JZ8D33RW), skipping
```

#### 测试验证
```bash
python -m pytest tests/test_duplicate_detection.py -v
```

---

### 2.4 PDF 管理 (PDFManager)

#### 功能特性
- **自动下载**: 从 arXiv 下载论文 PDF
- **智能命名**: 根据论文标题生成安全的文件名
- **Unicode 支持**: 正确处理特殊字符和多语言标题
- **唯一性保证**: 自动处理文件名冲突
- **异步下载**: 使用 aiohttp 实现高效并发下载

#### 文件名处理
1. Unicode 标准化 (NFKD)
2. 转换为 ASCII，忽略特殊字符
3. 保留原始大小写
4. 替换特殊字符为空格
5. 截断超长文件名 (最多 100 字符)
6. 处理文件名冲突 (自动添加序号)

#### 下载位置
- **默认路径**: `~/Downloads/arxiv_papers/`
- **自定义**: 初始化时可指定下载目录

---

### 2.5 自动采集脚本 (auto_collect.py)

#### 五类研究方向配置

| 类别 | 集合 KEY | 研究主题 | 查询关键词 |
|------|----------|----------|------------|
| **general** | LRML5CDJ | 智能网联汽车综合研究 | 智能网联汽车、自动驾驶 (通信/感知/融合/规划) |
| **communication** | 3E4NFDPR | V2X 车联网通信 | V2X、车联网、通信安全、语义通信、波束成形 |
| **perception** | 8CQV3SDV | 环境感知技术 | 摄像头、激光雷达、雷达、传感器融合、目标检测 |
| **control** | 8862N8CE | 路径规划与控制 | 路径规划、运动规划、模型预测控制 MPC |
| **security** | S97HI5KX | 安全与隐私保护 | 车辆安全、隐私保护、对抗攻击 |

#### 可配置参数
```python
# auto_collect.py 配置
ZOTERO_LIBRARY_ID = "19092277"
ZOTERO_API_KEY = "HoLB2EnPj4PpHo1gQ65qy2aw"
MAX_RESULTS_PER_CATEGORY = 50  # 每个类别最多论文数
START_DATE = "2023-01-01"       # 起始日期
```

#### 运行流程
1. 遍历 5 个研究方向
2. 为每个类别初始化专用采集器
3. 执行 arXiv 搜索和论文采集
4. 自动下载并上传 PDF
5. 跳过重复文献
6. 类别间延迟 3 秒 (避免 API 压力)
7. 输出详细统计报告

---

## 3. 技术架构

### 3.1 项目结构

```
arxiv-zotero-connector/
├── arxiv_zotero/              # 核心包
│   ├── __init__.py
│   ├── cli.py                # 命令行接口
│   ├── clients/               # API 客户端
│   │   ├── arxiv_client.py   # arXiv API 客户端
│   │   └── zotero_client.py  # Zotero API 客户端
│   ├── config/                # 配置模块
│   │   ├── arxiv_config.py   # arXiv 元数据映射
│   │   └── metadata_config.py # Zotero 元数据映射
│   ├── core/                  # 核心逻辑
│   │   ├── connector.py      # 主连接器
│   │   ├── paper_processor.py # 论文处理器
│   │   └── search_params.py  # 搜索参数类
│   └── utils/                 # 工具模块
│       ├── credentials.py    # 凭证管理
│       ├── pdf_manager.py    # PDF 管理
│       └── summarizer.py     # AI 摘要生成 (可选)
├── .github/workflows/         # GitHub Actions
│   └── daily-paper-collection.yml
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_imports.py
│   └── test_duplicate_detection.py
├── auto_collect.py            # 主采集脚本
├── README.md                  # 项目文档
└── api-docs.md                # API 文档
```

### 3.2 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| **核心语言** | Python 3.7+ | 主要开发语言 |
| **异步处理** | asyncio | 并发论文处理 |
| **HTTP 客户端** | aiohttp | 异步 HTTP 请求 |
| **arXiv API** | arxiv | 论文搜索和元数据获取 |
| **Zotero API** | pyzotero | Zotero 库操作 |
| **配置管理** | python-dotenv | 环境变量加载 |
| **测试框架** | pytest | 单元测试 |
| **CI/CD** | GitHub Actions | 定时任务自动化 |

### 3.3 数据流程

```
┌─────────────────┐
│  arXiv API      │
│  (论文搜索)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ArxivClient     │
│ (获取论文元数据) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MetadataMapper  │
│ (元数据格式转换) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│PaperProcessor   │
│ (检查重复)       │
│ ┌─────────────┐ │
│ │Duplicate?   │ │
│ └──────┬──────┘ │
│        │        │
│       Yes      No
│        │        │
│        ▼        ▼
│    (跳过)  ┌─────────────┐
│          │ZoteroClient  │
│          │(创建文献条目) │
│          └──────┬───────┘
│                 │
│                 ▼
│          ┌─────────────┐
│          │PDFManager   │
│          │(下载PDF)    │
│          └──────┬───────┘
│                 │
│                 ▼
│          ┌─────────────┐
│          │ZoteroClient │
│          │(上传附件)    │
│          └─────────────┘
└─────────────────────────┘
```

---

## 4. 测试验证

### 4.1 测试覆盖

| 测试文件 | 测试内容 | 状态 |
|----------|----------|------|
| `test_imports.py` | 模块导入测试 | ✅ PASS |
| `test_imports.py` | ArxivSearchParams 测试 | ✅ PASS |
| `test_duplicate_detection.py` | 重复检测功能测试 | ✅ PASS |

### 4.2 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_duplicate_detection.py -v

# 测试命令行工具
python -m arxiv_zotero.cli --help
```

### 4.3 测试结果 (2025-12-23)

```
============================= test session starts =============================
platform win32 -- Python 3.14.0
plugins: anyio-4.12.0, asyncio-1.3.0
collected 3 items

tests/test_duplicate_detection.py::test_duplicate_detection PASSED    [ 33%]
tests/test_imports.py::test_imports PASSED                           [ 66%]
tests/test_imports.py::test_search_params PASSED                     [100%]

======================= 3 passed, 21 warnings in 15.43s =====================
```

---

## 5. GitHub Actions 自动化

### 5.1 工作流配置

**文件**: [`.github/workflows/daily-paper-collection.yml`](.github/workflows/daily-paper-collection.yml)

**调度时间**: UTC 3:00 (北京时间 11:00)

**功能特性**:
- ✅ 自动执行论文采集
- ✅ 生成并提交采集日志
- ✅ 失败时发送通知
- ✅ 支持手动触发
- ✅ 日志保留 30 天
- ✅ 自动跳过重复文献

### 5.2 GitHub Secrets 配置

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `ZOTERO_LIBRARY_ID` | `19092277` | Zotero 库 ID |
| `ZOTERO_API_KEY` | `HoLB2EnPj4PpHo1gQ65qy2aw` | Zotero API 密钥 |

---

## 6. 性能指标

### 6.1 运行时间

| 论文数量 | 预计耗时 | API 请求数 |
|---------|---------|-----------|
| 50 篇 (1 类) | 2-3 分钟 | ~100 次 |
| 250 篇 (5 类) | 10-15 分钟 | ~500 次 |
| 500 篇 (5 类) | 20-30 分钟 | ~1000 次 |

### 6.2 网络和存储

| 指标 | 数值 |
|------|------|
| 单篇 PDF 大小 | 1-5 MB |
| 250 篇论文存储 | 250 MB - 1.25 GB |
| arXiv API 限制 | 每 3 秒 1 请求 |
| Zotero API 限制 | 每 10 分钟 100 次请求 |

---

## 7. 使用场景

### 7.1 典型使用流程

1. **初始配置**
   ```bash
   # 安装
   pip install arxiv-zotero-connector

   # 配置环境变量 (.env)
   ZOTERO_LIBRARY_ID=your_library_id
   ZOTERO_API_KEY=your_api_key
   ```

2. **运行采集**
   ```bash
   # 手动运行
   python auto_collect.py

   # 或使用 CLI
   python -m arxiv_zotero.cli --config search_config.yaml
   ```

3. **GitHub Actions 自动化**
   - 推送代码到 GitHub
   - 配置 Secrets
   - 每天自动运行

### 7.2 高级使用场景

#### 场景 1: 单一类别深度采集
```python
import asyncio
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams

async def collect_specific_category():
    collector = ArxivZoteroCollector(
        zotero_library_id="19092277",
        zotero_api_key="your_api_key",
        collection_key="LRML5CDJ"  # general 集合
    )

    params = ArxivSearchParams(
        keywords=['"reinforcement learning" AND "autonomous driving"'],
        categories=['cs.AI', 'cs.RO'],
        max_results=200
    )

    successful, failed = await collector.run_collection_async(
        search_params=params,
        download_pdfs=True
    )

    print(f"成功: {successful}, 失败: {failed}")

asyncio.run(collect_specific_category())
```

#### 场景 2: 日期范围过滤
```python
from datetime import datetime

params = ArxivSearchParams(
    keywords=['"V2X" AND security'],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 6, 30),
    max_results=100
)
```

#### 场景 3: 自定义查询逻辑
```python
# 排除综述文章
query = ('"deep learning" AND "computer vision" '
         'NOT survey NOT review')

params = ArxivSearchParams(
    keywords=[query],
    max_results=50
)
```

---

## 8. 故障排查与最佳实践

### 8.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| UnicodeEncodeError | Windows 编码问题 | 脚本已内置 UTF-8 修复 |
| Zotero API Error | API 密钥无效 | 检查密钥权限设置 |
| PDF 下载失败 | 网络问题或 PDF 不存在 | 论文元数据仍会添加 |
| 所有论文重复 | 已存在文献 | 正常的重复检测 |

### 8.2 最佳实践

1. **定期运行**: 每天或每周运行，保持文献库最新
2. **关键词优化**: 使用具体关键词，避免过于宽泛
3. **排除综述**: 使用 `NOT survey NOT review`
4. **监控日志**: 定期查看 `arxiv_zotero.log`
5. **备份数据**: 定期备份 Zotero 库

---

## 9. 扩展性与定制

### 9.1 添加新研究方向

1. 编辑 `auto_collect.py` 中的 `QUERY_MAP`
2. 添加对应的 `COLLECTION_MAP` 条目
3. 重新运行脚本

### 9.2 集成 AI 摘要

项目支持可选的 AI 摘要生成功能（使用 Google Gemini）：

```python
from arxiv_zotero.utils.summarizer import PaperSummarizer

summarizer = PaperSummarizer(api_key="your_gemini_api_key")

collector = ArxivZoteroCollector(
    zotero_library_id="...",
    zotero_api_key="...",
    summarizer=summarizer,
    config={'summarizer': {'enabled': True}}
)
```

### 9.3 自定义元数据映射

编辑 [arxiv_zotero/config/metadata_config.py](arxiv_zotero/config/metadata_config.py) 来自定义 arXiv 到 Zotero 的元数据映射。

---

## 10. 许可与贡献

- **许可证**: MIT License
- **作者**: Stepan Kropachev
- **项目地址**: [GitHub Repository](https://github.com/StepanKropachev/arxiv-zotero-connector)
- **问题反馈**: [GitHub Issues](https://github.com/StepanKropachev/arxiv-zotero-connector/issues)

---

**版本**: 0.1.0 | **最后更新**: 2025-12-23
