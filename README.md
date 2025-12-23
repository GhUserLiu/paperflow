# ArXiv-Zotero 自动化论文采集系统

> 自动从 arXiv 采集最新研究论文，智能分类并同步到 Zotero 文献库，支持重复检测、自动下载 PDF 和 GitHub Actions 定时任务。

## 📋 项目概述

本系统是一个自动化文献管理工具，专门用于智能网联汽车和自动驾驶领域的研究人员。它能够：

- 🤖 **自动采集**: 从 arXiv 自动检索最新论文
- 📂 **智能分类**: 自动将论文分配到 5 个研究方向的 Zotero 集合
- 🔍 **重复检测**: 自动跳过已存在的文献，避免重复
- 📥 **PDF 下载**: 自动下载并上传 PDF 到 Zotero
- ⏰ **定时运行**: 支持 GitHub Actions 每天自动运行
- 📊 **日志追踪**: 详细的采集日志和历史记录

## 🎯 五类研究方向

| 类别 | Zotero 集合 | 研究主题 | 查询关键词 |
|------|------------|---------|-----------|
| **general** | LRML5CDJ | 智能网联汽车综合研究 | 智能网联汽车、自动驾驶 (通信/感知/融合/规划) |
| **communication** | 3E4NFDPR | V2X 车联网通信 | V2X、车联网、通信安全、语义通信、波束成形 |
| **perception** | 8CQV3SDV | 环境感知技术 | 摄像头、激光雷达、雷达、传感器融合、目标检测 |
| **control** | 8862N8CE | 路径规划与控制 | 路径规划、运动规划、模型预测控制 MPC |
| **security** | S97HI5KX | 安全与隐私保护 | 车辆安全、隐私保护、对抗攻击 |

## 🚀 快速开始

### 方式一：手动运行

```bash
# 进入项目目录
cd arxiv-zotero-connector

# 运行采集脚本
python auto_collect.py
```

### 方式二：GitHub Actions 自动运行（推荐）

配置 GitHub Actions 后，系统将每天 **UTC 3:00**（北京时间 11:00）自动运行。

详见下文「GitHub Actions 自动化配置」章节。

## 📦 安装配置

### 1. 系统要求

- Python 3.7 或更高版本
- Zotero 账户
- 稳定的网络连接

### 2. 安装依赖

```bash
# 克隆或下载项目
git clone https://github.com/StepanKropachev/arxiv-zotero-connector.git
cd arxiv-zotero-connector

# 安装包
pip install -e .
```

### 3. 配置 Zotero 凭证

项目已预配置以下信息（在 [.env](.env) 文件中）：

```env
ZOTERO_LIBRARY_ID=19092277
ZOTERO_API_KEY=HoLB2EnPj4PpHo1gQ65qy2aw
```

**如需使用自己的账户**：

1. 获取 Zotero Library ID：访问 https://www.zotero.org/settings/keys
2. 创建 API Key：点击 "New Private Key"，授予所有权限
3. 获取集合 KEY：打开 Zotero 网页版，从 URL 中复制集合 KEY

### 4. 验证安装

```bash
# 运行测试
python -m pytest tests/ -v

# 测试命令行工具
python -m arxiv_zotero.cli --help
```

## 📖 使用方法

### 基础使用

#### 运行完整采集（5 个类别）

```bash
python auto_collect.py
```

**默认配置**：
- 每个类别最多采集 **50 篇** 论文
- 总计最多 **250 篇** 论文
- 自动下载 PDF 并上传
- 自动跳过重复文献

#### 修改采集数量

编辑 [auto_collect.py](auto_collect.py#L54) 中的配置：

```python
MAX_RESULTS_PER_CATEGORY = 100  # 改为每类 100 篇
```

#### 自定义查询语句

编辑 [auto_collect.py](auto_collect.py#L21) 中的 `QUERY_MAP`：

```python
QUERY_MAP = {
    "my_category": (
        '"machine learning" AND "deep learning" '
        'NOT survey NOT review'
    ),
}
```

### 高级功能

#### 单独测试某个类别

```python
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams
import asyncio

async def test_category():
    collector = ArxivZoteroCollector(
        zotero_library_id="19092277",
        zotero_api_key="your_api_key",
        collection_key="LRML5CDJ"  # general 集合
    )

    search_params = ArxivSearchParams(
        keywords=[""autonomous driving" AND perception],
        max_results=10
    )

    successful, failed = await collector.run_collection_async(
        search_params=search_params,
        download_pdfs=True
    )

    print(f"成功: {successful}, 失败: {failed}")

asyncio.run(test_category())
```

#### 使用配置文件

创建 `search_config.yaml`：

```yaml
keywords:
  - "reinforcement learning"
  - "deep learning"
categories:
  - "cs.AI"
  - "cs.LG"
max_results: 50
```

运行：

```bash
python -m arxiv_zotero.cli --config search_config.yaml
```

## ⏰ GitHub Actions 自动化配置

### 快速设置

#### 1. 添加 GitHub Secrets

在 GitHub 仓库中添加 Secrets：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下两个密钥：

| Secret 名称 | 值 |
|------------|-----|
| `ZOTERO_LIBRARY_ID` | `19092277` |
| `ZOTERO_API_KEY` | `HoLB2EnPj4PpHo1gQ65qy2aw` |

#### 2. 推送工作流文件

工作流文件已创建在 [.github/workflows/daily-paper-collection.yml](.github/workflows/daily-paper-collection.yml)

```bash
git add .github/workflows/
git commit -m "Add daily paper collection workflow"
git push
```

#### 3. 验证运行

1. 访问 GitHub 仓库的 **Actions** 标签页
2. 查看 "Daily ArXiv Paper Collection" 工作流
3. 可手动点击 **"Run workflow"** 立即测试

### 调度时间

**默认配置**：
- **UTC 时间**: 每天 03:00
- **北京时间**: 每天 11:00（上午）

**修改运行时间**：

编辑 [.github/workflows/daily-paper-collection.yml](.github/workflows/daily-paper-collection.yml#L6)：

```yaml
schedule:
  - cron: '0 3 * * *'  # 分 时 日 月 周
```

**常用时间示例**：

| Cron 表达式 | UTC 时间 | 北京时间 |
|------------|----------|----------|
| `0 3 * * *` | 03:00 | 11:00 |
| `0 15 * * *` | 15:00 | 23:00 |
| `0 19 * * *` | 19:00 | 03:00 |
| `0 */6 * * *` | 每 6 小时 | - |

### 工作流功能

✅ 自动执行论文采集
✅ 生成并提交采集日志
✅ 失败时发送通知
✅ 支持手动触发
✅ 日志保留 30 天
✅ 自动跳过重复文献

## 🔁 重复检测功能

### 工作原理

系统在添加每篇论文前会自动：

1. 提取论文的 arXiv ID
2. 在 Zotero 库中搜索相同的 arXiv ID
3. 如果找到匹配，跳过该论文
4. 记录日志说明已跳过

### 日志示例

```
INFO - Found duplicate arXiv ID 2512.19694v1 in item JZ8D33RW
INFO - Paper 2512.19694v1 already exists in library (item: JZ8D33RW), skipping
```

### 测试验证

运行重复检测测试：

```bash
python -m pytest tests/test_duplicate_detection.py -v
# 或直接运行
python tests/test_duplicate_detection.py
```

预期结果：第二次运行应跳过所有已存在的论文。

### 统计说明

- **成功计数**：新添加的文献 + 跳过的重复文献
- **失败计数**：真正失败的文献

例如：
- 第一次运行：成功=50（全部是新文献）
- 第二次运行：成功=50（全部是重复文献，被跳过）

## 📊 输出示例

```
============================================================
ArXiv论文自动采集系统
Auto Paper Collection System
============================================================
开始时间: 2025-12-23 15:30:12
采集类别数: 5
每类最多论文数: 50

============================================================
开始采集类别: general
查询语句: ("intelligent connected vehicles" OR "autonomous driving")
         AND (communication OR perception OR "sensor fusion" OR planning)
         NOT survey NOT review
目标集合: LRML5CDJ
============================================================

[OK] general collection completed:
  Successful: 50 papers
  Failed: 0 papers

等待3秒后继续下一类别...

============================================================
采集完成！Collection Summary
============================================================
结束时间: 2025-12-23 17:30:45

总计:
  成功采集: 250 篇
  失败: 0 篇

分类详情:
  GENERAL:
    集合KEY: LRML5CDJ
    成功: 50 篇
    失败: 0 篇

  COMMUNICATION:
    集合KEY: 3E4NFDPR
    成功: 50 篇
    失败: 0 篇

  ... (其他类别)
```

## 🛠️ 自定义配置

### 添加新的研究类别

1. 在 [auto_collect.py](auto_collect.py#L21) 的 `QUERY_MAP` 中添加查询：

```python
QUERY_MAP = {
    # ... 现有类别

    "new_category": (
        '"your keywords" AND "more keywords" '
        'NOT survey NOT review'
    ),
}
```

2. 在 `COLLECTION_MAP` 中添加集合 KEY：

```python
COLLECTION_MAP = {
    # ... 现有映射

    "new_category": "YOUR_COLLECTION_KEY",
}
```

### 修改查询语句

支持布尔运算符：
- `AND` - 逻辑与
- `OR` - 逻辑或
- `NOT` - 逻辑非

示例：

```python
# 精确匹配标题
'"autonomous driving" AND perception'

# 多个关键词
('"V2X" OR "vehicle-to-everything" OR VANET) AND security

# 排除特定内容
'"deep learning" NOT survey NOT review'
```

### 添加日期过滤

编辑 [auto_collect.py](auto_collect.py#L95) 添加日期参数：

```python
from datetime import datetime

search_params = ArxivSearchParams(
    keywords=[query],
    max_results=MAX_RESULTS_PER_CATEGORY,
    start_date=datetime(2024, 1, 1)  # 只采集 2024 年后的论文
)
```

### 添加 arXiv 类别过滤

```python
search_params = ArxivSearchParams(
    keywords=[query],
    max_results=MAX_RESULTS_PER_CATEGORY,
    categories=["cs.AI", "cs.LG", "cs.RO"]  # 限制类别
)
```

## 🔧 故障排查

### 常见问题

#### 1. 编码错误（Windows）

**症状**: 控制台显示乱码或 UnicodeEncodeError

**解决方案**:
```bash
chcp 65001  # 切换到 UTF-8 编码
python auto_collect.py
```

脚本已内置 Windows 编码修复，通常不需要手动操作。

#### 2. API 错误

**症状**: 出现 "Zotero API Error" 或认证失败

**解决方案**:
- 检查网络连接
- 确认 Zotero 凭证正确
- 检查 API Key 权限设置
- 验证集合 KEY 是否有效

#### 3. PDF 下载失败

**症状**: 日志显示 "Failed to download PDF"

**原因**:
- arXiv 暂无该论文的 PDF
- 网络连接问题
- PDF 文件过大

**影响**: 论文元数据仍会添加到 Zotero，只是没有 PDF 附件

#### 4. 所有论文都是重复的

**原因**: 已存在文献，重复检测正常工作

**验证**: 查看日志中是否有 "Paper XXX already exists" 的提示

#### 5. 工作流运行失败

**症状**: GitHub Actions 显示红色失败标记

**解决步骤**:
1. 查看 Actions 页面的详细日志
2. 检查 GitHub Secrets 配置
3. 确认工作流 YAML 语法正确
4. 验证依赖包安装成功

### 调试模式

启用详细日志：

```python
import logging
logging.getLogger('arxiv_zotero').setLevel(logging.DEBUG)
```

查看实时日志文件：

```bash
# Windows
tail -f arxiv_zotero.log

# 或使用文本编辑器打开
```

### 停止程序

按 `Ctrl + C` 停止运行。已添加的论文会保留在 Zotero 中。

## 📈 性能和限制

### 运行时间

| 论文数量 | 预计耗时 | API 请求数 |
|---------|---------|-----------|
| 50 篇（1 类） | 2-3 分钟 | ~100 次 |
| 250 篇（5 类） | 10-15 分钟 | ~500 次 |

### API 限制

**Zotero API**:
- 文件上传: 每 10 分钟 100 MB
- 其他请求: 每 10 分钟 100 次
- 程序已内置速率限制保护

**arXiv API**:
- 每个 IP 每 3 秒最多 1 个请求
- 程序已自动遵守此限制

### 存储空间

- 每篇论文约 1-5 MB
- 250 篇论文约 250 MB - 1.25 GB
- 确保 Zotero 存储空间充足

## 🎯 最佳实践

### 1. 定期运行建议

- **每天运行**: 保持文献库最新
- **每周运行**: 平衡更新频率和 API 使用
- **手动运行**: 需要特定文献时立即运行

### 2. 查询优化

- 使用具体关键词，避免过于宽泛
- 使用 `NOT survey NOT review` 排除综述文章
- 定期更新关键词以匹配最新研究趋势

### 3. 监控和维护

- 每周检查 Zotero 中的论文质量
- 查看采集日志了解运行状况
- 定期更新依赖包：`pip install --upgrade arxiv-zotero-connector`

### 4. 备份配置

- 备份 `.env` 文件中的配置
- 记录集合 KEY 的映射关系
- 保存查询语句的历史版本

### 5. 安全建议

✅ 不要在代码中硬编码 API Key
✅ 定期更换 Zotero API Key
✅ 使用最小权限原则配置 API Key
✅ 监控 GitHub Actions 日志确保安全

## 📁 项目结构

```
arxiv-zotero-connector/
├── arxiv_zotero/              # 核心包
│   ├── __init__.py
│   ├── cli.py                # 命令行接口
│   ├── clients/               # API 客户端
│   │   ├── arxiv_client.py
│   │   └── zotero_client.py
│   ├── config/                # 配置模块
│   │   ├── arxiv_config.py
│   │   └── metadata_config.py
│   ├── core/                  # 核心逻辑
│   │   ├── connector.py
│   │   ├── paper_processor.py
│   │   └── search_params.py
│   └── utils/                 # 工具模块
│       ├── credentials.py
│       ├── pdf_manager.py
│       └── summarizer.py
├── .github/workflows/         # GitHub Actions
│   └── daily-paper-collection.yml
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_imports.py
│   └── test_duplicate_detection.py  # 重复检测测试
├── auto_collect.py            # 主采集脚本
├── .env                       # 环境变量配置
├── .env.example               # 环境变量示例
├── requirements.txt            # 依赖列表
├── setup.py                   # 安装配置
├── README.md                  # 项目说明（本文件）
└── api-docs.md                # API 文档
```

## 📚 相关资源

### 官方文档

- [arXiv API 文档](https://arxiv.org/help/api)
- [Zotero API 文档](https://www.zotero.org/support/dev/api)
- [PyZotero 文档](https://pyzotero.readthedocs.io/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

### 工具和资源

- [Cron 表达式生成器](https://crontab.guru/) - 定时任务配置
- [arXiv Category Taxonomy](https://arxiv.org/category_taxonomy) - arXiv 分类列表

## 🆘 获取帮助

### 遇到问题？

1. **查看日志**: 检查 `arxiv_zotero.log` 文件
2. **运行测试**: `python -m pytest tests/test_duplicate_detection.py -v`
3. **查看文档**: 阅读相关章节的详细说明
4. **提交 Issue**: [GitHub Issues](https://github.com/StepanKropachev/arxiv-zotero-connector/issues)

### 联系方式

- 项目主页: [GitHub Repository](https://github.com/StepanKropachev/arxiv-zotero-connector)
- 作者: Stepan Kropachev

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**版本**: 0.1.0
**最后更新**: 2025-12-23
**维护状态**: 活跃开发中

---

Made with ❤️ by [Stepan Kropachev](https://github.com/StepanKropachev)
