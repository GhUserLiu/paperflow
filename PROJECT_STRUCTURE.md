# 项目结构说明

## 📁 目录结构

```
arxiv-zotero-auto/
├── .github/                    # GitHub Actions 配置
│   └── workflows/
│       └── daily-paper-collection.yml  # 定时任务工作流
│
├── arxiv_zotero/              # 核心包源代码
│   ├── __init__.py
│   ├── __main__.py            # 支持 `python -m arxiv_zotero`
│   ├── cli.py                 # 命令行接口
│   │
│   ├── clients/               # API 客户端
│   │   ├── __init__.py
│   │   ├── arxiv_client.py    # arXiv API 客户端
│   │   └── zotero_client.py   # Zotero API 客户端
│   │
│   ├── config/                # 配置模块
│   │   ├── __init__.py
│   │   ├── arxiv_config.py    # arXiv 字段映射配置
│   │   └── metadata_config.py # 元数据处理配置
│   │
│   ├── core/                  # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── connector.py       # 主连接器
│   │   ├── paper_processor.py # 论文处理器
│   │   └── search_params.py   # 搜索参数类
│   │
│   └── utils/                 # 工具模块
│       ├── __init__.py
│       ├── credentials.py     # 凭证加载
│       ├── pdf_manager.py     # PDF 下载管理
│       └── summarizer.py      # 论文摘要生成
│
├── dev-tools/                 # 开发调试工具(不在生产环境使用)
│   ├── cleanup_duplicates.py      # 清理重复论文
│   ├── debug_zotero_api.py        # Zotero API 调试
│   ├── test_duplicate_fix.py      # 重复检测测试
│   └── test_zotero_search_methods.py  # 搜索方法测试
│
├── docs/                      # 项目文档
│   └── api-docs.md            # API 详细文档
│
├── examples/                  # 使用示例
│   └── (示例代码文件)
│
├── scripts/                   # 运行脚本
│   └── auto_collect.py        # 主采集脚本
│
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_duplicate_detection.py  # 重复检测测试
│   └── test_imports.py        # 导入测试
│
├── logs/                      # 日志目录
│   └── .gitkeep               # 保持目录被 Git 跟踪
│
├── .env                       # 环境变量(本地,不提交)
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略规则
├── LICENSE                    # 许可证
├── README.md                  # 项目说明
├── PROJECT_STRUCTURE.md       # 本文件 - 项目结构说明
├── requirements.txt           # 依赖列表
├── setup.py                   # 包安装配置
└── pyproject.toml            # Python 项目配置
```

## 🔧 核心模块说明

### 1. **arxiv_zotero/clients/** - API 客户端
- **arxiv_client.py**: 封装 arXiv API 搜索和获取功能
- **zotero_client.py**: 封装 Zotero API 操作(创建、上传、查重)

### 2. **arxiv_zotero/config/** - 配置管理
- **arxiv_config.py**: arXiv 字段到 Zotero 字段的映射规则
- **metadata_config.py**: 元数据转换逻辑(清理 LaTeX、格式化作者等)

### 3. **arxiv_zotero/core/** - 核心逻辑
- **connector.py**: 主连接器,协调整个采集流程
- **paper_processor.py**: 单篇论文的处理逻辑
- **search_params.py**: 搜索参数封装类

### 4. **arxiv_zotero/utils/** - 工具函数
- **credentials.py**: 从 .env 文件加载 Zotero 凭证
- **pdf_manager.py**: PDF 下载和临时文件管理
- **summarizer.py**: 使用 AI 生成论文摘要(可选功能)

## 📝 配置文件

### 环境变量 (.env)
```bash
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_API_KEY=your_api_key
```

### requirements.txt
项目依赖列表,包括:
- arxiv: arXiv API 客户端
- pyzotero: Zotero API 客户端
- requests: HTTP 请求
- aiohttp: 异步 HTTP 请求
- 其他依赖...

## 🚀 使用方式

### 方式一:直接运行脚本
```bash
python scripts/auto_collect.py
```

### 方式二:作为模块使用
```bash
python -m arxiv_zotero.cli --help
```

### 方式三:作为包导入
```python
from arxiv_zotero import ArxivZoteroCollector, ArxivSearchParams
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_duplicate_detection.py -v
```

## 🔨 开发工具

`dev-tools/` 目录包含开发和调试工具:

- **cleanup_duplicates.py**: 清理 Zotero 中的重复条目
- **debug_zotero_api.py**: 测试 Zotero API 调用
- **test_*.py**: 各种功能测试脚本

⚠️ **注意**: 这些工具仅供开发使用,不应在生产环境中运行。

## 📊 日志

日志文件存储在 `logs/` 目录:
- `arxiv_zotero.log`: 主日志文件
- 包含详细的运行信息、错误和调试信息

## 🔄 数据流程

```
arXiv API 搜索
    ↓
ArxivClient 获取论文列表
    ↓
PaperProcessor 处理每篇论文
    ↓
检查重复 (check_duplicate)
    ↓
创建 Zotero 条目
    ↓
下载并上传 PDF
    ↓
添加到集合
```

## 🛠️ 开发建议

### 添加新功能
1. 在相应的模块目录创建新文件
2. 更新 `__init__.py` 导出新模块
3. 在 `tests/` 添加对应测试
4. 更新文档

### 代码规范
- 遵循 PEP 8 风格指南
- 使用类型注解(Type Hints)
- 编写文档字符串(Docstrings)
- 添加适当的日志记录

### 测试
- 为新功能编写单元测试
- 确保所有测试通过后再提交
- 使用 `dev-tools/` 中的工具验证功能

## 📦 虚拟环境

建议使用 Python 虚拟环境:

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 以可编辑模式安装项目
pip install -e .
```

## 🔐 安全注意事项

- ⚠️ **不要**将 `.env` 文件提交到 Git
- ⚠️ **不要**在代码中硬编码 API Key
- ✅ 使用 `.env.example` 提供配置模板
- ✅ 定期更换 Zotero API Key

## 📞 获取帮助

- 查看 [README.md](README.md) 了解快速开始
- 查看 [docs/api-docs.md](docs/api-docs.md) 了解 API 详情
- 提交 Issue 到 GitHub 仓库

---

**最后更新**: 2026-01-04
