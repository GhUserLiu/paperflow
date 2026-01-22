# ArXiv-Zotero 自动化论文采集系统

> 自动从 arXiv 和 ChinaXiv 采集最新研究论文，智能分类并同步到 Zotero 文献库

**版本**: 2.1.0 | 支持中英文双语搜索、OpenAlex 期刊排序

---

## 📋 项目概述

自动化文献管理工具，支持：

- 🤖 **自动采集**: 从 arXiv 和 ChinaXiv 自动检索论文
- 🌍 **双语搜索**: 支持中英文关键词
- 📥 **PDF 下载**: 自动下载并上传到 Zotero
- 📊 **智能排序**: 基于 OpenAlex 期刊指标排序
- 🔍 **查重检测**: 全局或集合内查重
- ⏰ **定时运行**: 支持 GitHub Actions 每日自动运行

---

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/StepanKropachev/arxiv-zotero-connector.git
cd arxiv-zotero-connector
pip install -r requirements.txt
pip install -e .
```

### 2. 配置 Zotero

创建 `.env` 文件：

```bash
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_API_KEY=your_api_key
TEMP_COLLECTION_KEY=your_temp_collection_key
```

**获取 API Key**:
1. 访问 https://www.zotero.org/settings/keys
2. 创建新密钥，勾选 "允许写入访问"
3. 复制 Library ID 和 API Key

### 3. 运行

```bash
# 手动搜索论文
python scripts/search_papers.py --keywords "autonomous driving"

# 或运行定时采集
python scripts/auto_collect.py
```

---

## 📖 使用指南

### 工具对比

| 工具 | 使用场景 | 关键词输入 | 时间过滤 |
|------|---------|-----------|---------|
| **search_papers.py** | 手动搜索、特定主题 | 输入一种（中英任选） | ❌ 无限制 |
| **auto_collect.py** | 定时任务、批量采集 | 双语自动（配置文件） | ✅ 25小时内 |

### 工具 1: search_papers.py - 灵活搜索

#### 基础用法

```bash
# 搜索论文（默认 20 篇）
python scripts/search_papers.py --keywords "autonomous driving"

# 搜索 50 篇
python scripts/search_papers.py --keywords "deep learning" --max-results 50

# 不下载 PDF（更快）
python scripts/search_papers.py --keywords "test" --no-pdf
```

#### 高级功能

**1. OpenAlex 期刊排序**（优先显示高质量论文）

```bash
# 按期刊影响力排序
python scripts/search_papers.py --keywords "machine learning" --enable-openalex

# 自定义权重
python scripts/search_papers.py --keywords "neural networks" --enable-openalex \
  --openalex-weights '{"cited_by_percentile": 0.7, "h_index": 0.2, "impact_factor": 0.1}'
```

**排序指标说明**：
- `cited_by_percentile` (50%): 被引百分位 - 最重要
- `h_index` (30%): 期刊 h 指数
- `impact_factor` (20%): 影响因子

**2. 双语搜索**

```bash
# 英文论文（arXiv）
python scripts/search_papers.py --keywords "autonomous driving"

# 中文论文（arXiv + ChinaXiv）
python scripts/search_papers.py --keywords "自动驾驶" --enable-chinaxiv
```

**3. 自动补充数量**（智能补充直到达到目标）

```bash
# 目标保存 50 篇（初始搜索 1.2-2.0 倍，自动补充）
python scripts/search_papers.py --keywords "deep learning" \
  --max-results 50 --target-results 50
```

**4. 集合内查重**（更快）

```bash
# 只在目标集合内查重（0.5-1秒 vs 全局2-3秒）
python scripts/search_papers.py --keywords "test" --collection-only-dupcheck
```

#### 所有参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 搜索关键词（必需） | - |
| `--max-results` | 最大结果数 | 20 |
| `--no-pdf` | 不下载 PDF | False |
| `--enable-chinaxiv` | 启用 ChinaXiv 来源 | False |
| `--enable-openalex` | 启用 OpenAlex 排序 | False |
| `--openalex-weights` | 自定义权重（JSON） | - |
| `--target-results` | 目标保存数量（自动补充） | - |
| `--collection-only-dupcheck` | 集合内查重 | False |
| `--no-auto-preload` | 禁用自动缓存预热 | False |

---

### 工具 2: auto_collect.py - 定时采集

#### 配置文件

编辑 `config/bilingual_keywords.yaml`:

```yaml
sources:
  arxiv:
    keywords:
      general: '"intelligent connected vehicles" OR "autonomous driving"'
      perception: '"computer vision" OR "object detection"'
  chinaxiv:
    keywords:
      general: '"智能网联汽车" OR "自动驾驶"'
      perception: '"计算机视觉" OR "目标检测"'
```

#### 运行

```bash
# 手动运行
python scripts/auto_collect.py

# 查看帮助
python scripts/auto_collect.py --help
```

#### GitHub Actions 自动化

1. Fork 本项目
2. Settings > Secrets > 添加:
   - `ZOTERO_LIBRARY_ID`
   - `ZOTERO_API_KEY`
   - `ENABLE_CHINAXIV` (可选)
3. 启用 Actions → 每天 UTC 3:00 自动运行

---

## 📊 OpenAlex 排序详解

### 工作原理

```
论文 → OpenAlex API → 期刊指标 → 综合评分 → 排序
                              ↓
                        缓存（提速 70-90%）
```

### 查询策略（三层降级）

1. **DOI 查询**（最准确）→ 期刊名查询 → 默认分数
2. **降级保护**: API 失败使用默认分数
3. **自动缓存**: 首次运行预热常见期刊（15-30秒）

### 性能对比

| 场景 | 耗时（50篇） |
|------|------------|
| 无缓存 | ~60秒 |
| 有缓存（80%命中） | ~15秒 |

---

## ⚙️ 配置说明

### 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `ZOTERO_LIBRARY_ID` | Zotero Library ID | ✅ |
| `ZOTERO_API_KEY` | Zotero API Key | ✅ |
| `TEMP_COLLECTION_KEY` | 临时集合 KEY | ✅ |
| `ENABLE_CHINAXIV` | 启用 ChinaXiv | ❌ |

### 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量（不提交到 Git） |
| `config/bilingual_keywords.yaml` | 双语关键词配置 |
| `config/journal_metrics_cache.json` | OpenAlex 缓存（自动生成） |

---

## 🎯 使用示例

### 示例 1: 搜索高质量论文

```bash
python scripts/search_papers.py \
  --keywords "machine learning" \
  --max-results 30 \
  --enable-openalex
```

### 示例 2: 双语搜索

```bash
# 英文
python scripts/search_papers.py --keywords "autonomous driving" --max-results 25

# 中文
python scripts/search_papers.py --keywords "自动驾驶" --enable-chinaxiv --max-results 25
```

### 示例 3: 代码集成

```python
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams
import asyncio

async def search():
    collector = ArxivZoteroCollector(
        zotero_library_id="your_id",
        zotero_api_key="your_key",
        collection_key="your_collection",
        enable_openalex_ranking=True
    )

    search_params = ArxivSearchParams(
        keywords=["deep learning"],
        max_results=20
    )

    successful, failed = await collector.run_collection_async(
        search_params=search_params,
        download_pdfs=True
    )

    print(f"成功: {successful}, 失败: {failed}")

asyncio.run(search())
```

更多示例见 [examples/](examples/)

---

## 🔍 常见问题

### Q: search_papers.py 需要同时输入中英文关键词吗？

**A: 不需要！** 输入什么关键词就搜索什么：
- 想搜英文 → 输入英文关键词
- 想搜中文 → 输入中文关键词
- 想双语 → 运行两次，各输入一种

### Q: OpenAlex 排序安全吗？会影响速度吗？

**A: 完全安全！**
- 首次运行：15-30秒（自动预热缓存）
- 后续运行：提速70-90%（使用缓存）
- 有完整降级机制

### Q: 如何获取 Zotero Library ID？

访问 https://www.zotero.org/settings/keys，页面顶部显示你的 Library ID

### Q: 为什么有些论文没有下载 PDF？

可能原因：
1. 论文没有公开的 PDF
2. 网络问题
3. arXiv 处理延迟

### Q: 可以同时添加多个关键词吗？

可以！使用布尔运算符：

```bash
python scripts/search_papers.py --keywords '"deep learning" AND "computer vision"'
```

---

## 📁 项目结构

```
arxiv-zotero-connector/
├── arxiv_zotero/          # 主包
│   ├── clients/           # API 客户端
│   ├── core/              # 核心逻辑
│   ├── config/            # 配置模块
│   └── utils/             # 工具类
├── scripts/               # 独立脚本
│   ├── auto_collect.py    # 定时采集
│   └── search_papers.py   # 灵活搜索
├── examples/              # 使用示例
├── config/                # 配置文件
├── tests/                 # 测试
├── docs/ARCHITECTURE.md        # 系统架构文档
└── README.md              # 本文档
```

详细架构说明见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 📈 性能和限制

### 运行时间

| 论文数量 | 预计耗时 | API 请求数 |
|---------|---------|-----------|
| 20 篇 | 1-2 分钟 | ~40 次 |
| 50 篇 | 3-5 分钟 | ~100 次 |
| 250 篇 | 10-15 分钟 | ~500 次 |

### API 限制

**Zotero API**:
- 文件上传: 每 10 分钟 100 MB
- 其他请求: 每 10 分钟 100 次
- 程序已内置速率限制保护

**arXiv API**:
- 每个 IP 每 3 秒最多 1 个请求
- 程序已自动遵守此限制

---

## 🛠️ 故障排查

### Windows 编码错误

```bash
chcp 65001  # 切换到 UTF-8
python scripts/auto_collect.py
```

脚本已内置修复，通常无需手动操作。

### API 错误

- 检查网络连接
- 确认 Zotero 凭证正确
- 检查 API Key 权限

### 调试模式

```python
import logging
logging.getLogger('arxiv_zotero').setLevel(logging.DEBUG)
```

---

## 📚 更多资源

- **系统架构**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 详细架构说明
- **项目结构**: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - 目录结构和模块说明
- **优化总结**: [docs/OPTIMIZATION_SUMMARY.md](docs/OPTIMIZATION_SUMMARY.md) - 项目改进记录
- **使用示例**: [examples/](examples/) - 代码示例
- **测试指南**: [tests/README.md](tests/README.md) - 测试文档

### 官方文档

- [arXiv API 文档](https://arxiv.org/help/api)
- [Zotero API 文档](https://www.zotero.org/support/dev/api)
- [OpenAlex API 文档](https://docs.openalex.org/)

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**版本**: 2.1.0
**最后更新**: 2026-01-22
**维护者**: [StepanKropachev](https://github.com/StepanKropachev)

---

Made with ❤️ by [Stepan Kropachev](https://github.com/StepanKropachev)
