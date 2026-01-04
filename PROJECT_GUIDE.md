# ArXiv-Zotero Auto 项目完整指南

> 自动从 arXiv 采集最新研究论文,智能分类并同步到 Zotero 文献库

**版本**: 2.0.0 (优化版)
**最后更新**: 2026-01-04

---

## 🎯 项目概述

本系统是一个自动化文献管理工具,专门用于智能网联汽车和自动驾驶领域的研究人员。

### ✨ 核心特性

- 🤖 **自动采集**: 从 arXiv 自动检索最新论文
- 📂 **智能分类**: 自动将论文分配到 5 个研究方向的 Zotero 集合
- ⏰ **时间过滤**: 只添加过去 25 小时内的论文
- 📥 **PDF 下载**: 自动下载并上传 PDF 到 Zotero
- 🚀 **API 优化**: 符合 Zotero API 限制,安全可靠
- ⏰ **定时运行**: 支持 GitHub Actions 定时任务
- 📊 **日志追踪**: 详细的采集日志和 API 统计

---

## 🗂️ 项目结构

```
arxiv-zotero-auto/
├── 📦 arxiv_zotero/              # 核心包
│   ├── clients/
│   │   ├── arxiv_client.py       # arXiv API
│   │   └── zotero_client.py      # Zotero API (含缓存+限速)
│   ├── config/
│   │   ├── arxiv_config.py       # 字段映射
│   │   └── metadata_config.py    # 元数据处理
│   ├── core/
│   │   ├── connector.py          # 主连接器
│   │   ├── paper_processor.py    # 论文处理器
│   │   └── search_params.py      # 搜索参数
│   └── utils/
│       ├── credentials.py        # 凭证加载
│       ├── pdf_manager.py        # PDF 管理
│       └── summarizer.py         # AI 摘要
│
├── 🛠️ dev-tools/                 # 开发工具
│   ├── test_api_optimization.py  # API 性能测试
│   ├── cleanup_duplicates.py     # 清理重复论文
│   └── debug_*.py                # 调试脚本
│
├── 📜 scripts/                    # 运行脚本
│   └── auto_collect.py           # 主采集脚本 (含时间过滤)
│
├── 🧪 tests/                      # 测试文件
│   ├── test_duplicate_detection.py
│   └── test_imports.py
│
├── 📚 docs/                       # 详细文档
│   └── api-docs.md
│
├── 📊 logs/                       # 日志目录
│   └── .gitkeep
│
├── ⚙️ 配置文件
│   ├── .env.example              # 环境变量模板
│   ├── .gitignore                # Git 忽略规则
│   ├── requirements.txt          # 依赖列表
│   ├── setup.py                  # 安装配置
│   └── pyproject.toml            # 项目配置
│
├── 📖 文档
│   ├── README.md                 # 项目说明
│   ├── PROJECT_GUIDE.md          # 本文件 - 完整指南
│   ├── API_OPTIMIZATION_SUMMARY.md  # API 优化详情
│   ├── PROJECT_STRUCTURE.md      # 项目结构说明
│   └── SETUP_ENVIRONMENT.md      # 环境配置指南
│
├── 🔧 其他
│   ├── automation.py             # 自动化脚本
│   └── examples/                 # 使用示例
│
└── 🚀 GitHub Actions
    └── .github/workflows/
        └── daily-paper-collection.yml
```

---

## 🚀 快速开始

### 1️⃣ **前置准备**

```bash
# 克隆项目
git clone https://github.com/StepanKropachev/arxiv-zotero-connector.git
cd arxiv-zotero-connector
```

### 2️⃣ **设置虚拟环境** (推荐)

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ **安装依赖**

```bash
pip install -r requirements.txt
pip install -e .
```

### 4️⃣ **配置环境**

```bash
# 复制配置模板
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/macOS

# 编辑 .env 文件,填入你的凭证
```

### 5️⃣ **运行采集**

```bash
# 方式一: 直接运行脚本
python scripts/auto_collect.py

# 方式二: 使用命令行接口
python -m arxiv_zotero.cli --help
```

---

## 🎯 五类研究方向

| 类别 | Zotero 集合 | 研究主题 | 查询关键词 |
|------|------------|---------|-----------|
| **general** | LRML5CDJ | 智能网联汽车综合研究 | 智能网联汽车、自动驾驶 (通信/感知/融合/规划) |
| **communication** | 3E4NFDPR | V2X 车联网通信 | V2X、车联网、通信安全、语义通信、波束成形 |
| **perception** | 8CQV3SDV | 环境感知技术 | 摄像头、激光雷达、雷达、传感器融合、目标检测 |
| **control** | 8862N8CE | 路径规划与控制 | 路径规划、运动规划、模型预测控制 MPC |
| **security** | S97HI5KX | 安全与隐私保护 | 车辆安全、隐私保护、对抗攻击 |

---

## ⚙️ 配置说明

### **时间过滤配置**

编辑 `scripts/auto_collect.py`:

```python
# 时间范围: 只收集过去 N 小时内的论文
TIME_FILTER_HOURS = 25  # 可改为 12, 24, 48 等

# 每个类别最多论文数
MAX_RESULTS_PER_CATEGORY = 10  # 可改为 5, 20, 50 等
```

### **自定义查询语句**

编辑 `scripts/auto_collect.py` 中的 `QUERY_MAP`:

```python
QUERY_MAP = {
    "my_category": (
        '"machine learning" AND "deep learning" '
        'NOT survey NOT review'
    ),
}
```

### **添加新类别**

1. 在 `QUERY_MAP` 添加查询
2. 在 `COLLECTION_MAP` 添加集合 KEY
3. 重新运行脚本

---

## 📊 性能与优化

### **API 使用优化**

本项目已针对 Zotero API 进行全面优化:

✅ **arXiv ID 缓存机制**
- 首次调用: 1 次 API 请求(加载 500 篇)
- 后续调用: 0 次 API 请求(从缓存)
- **减少 99.6% 的重复检测请求**

✅ **速率限制保护**
- Zotero 限制: 每 10 分钟 100 次
- 自动检测并等待
- **确保不被封禁**

✅ **时间过滤**
- 只检索过去 25 小时内的论文
- 避免加载大量旧数据
- **减少不必要的 API 请求**

### **性能对比**

| 场景 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| **API 请求数** | 250-1,500 次 | 1-50 次 | ⬇️ **97%** |
| **运行速度** | 基准 | 2-3 倍 | ⬆️ **200%** |
| **符合限制** | ❌ 超限 | ✅ 符合 | **安全** |

### **实际使用情况**

```
配置: 5 个类别 × 10 篇 = 50 篇论文
API 请求: ~50 次
使用率: 50% (Zotero 限制 100 次)
安全裕度: 50% ✅
```

---

## 🔁 重复检测说明

### **查重功能已删除**

**原因**:
- 时间过滤(过去 25 小时)已避免重复
- 删除后减少大量 API 请求
- 简化代码逻辑

**影响**:
- ❌ 不再检查重复
- ✅ 直接添加所有符合时间条件的论文
- ⚠️ 多次运行可能添加重复

**建议**:
- ✅ 使用 GitHub Actions 每天定时运行
- ✅ 调整 `TIME_FILTER_HOURS` 略大于运行间隔
- ✅ 定期手动清理 Zotero 中的重复

**清理工具**:
```bash
# 使用开发工具清理重复
python dev-tools/cleanup_duplicates.py
```

---

## 📈 输出示例

```
============================================================
ArXiv论文自动采集系统
Auto Paper Collection System
============================================================
开始时间: 2026-01-04 22:00:00
采集类别数: 5
每类最多论文数: 10
时间范围: 过去 25 小时
查重功能: 已禁用(直接添加所有论文)

============================================================
开始采集类别: general
查询语句: ("intelligent connected vehicles" OR "autonomous driving")...
目标集合: LRML5CDJ
时间范围: 过去 25 小时
起始时间: 2026-01-03 21:00:00
============================================================

刷新 arXiv ID 缓存...
arXiv ID 缓存已刷新,共 42 条记录

Processing paper: 2512.24922v1
Processing paper: 2512.24331v1
...

[OK] general collection completed:
  Successful: 10 papers
  Failed: 0 papers

API 请求统计: 50 次, 耗时 120.5 秒, 平均速率 0.41 次/秒

等待3秒后继续下一类别...

============================================================
采集完成！Collection Summary
============================================================
结束时间: 2026-01-04 22:15:30

总计:
  成功采集: 50 篇
  失败: 0 篇

分类详情:
  GENERAL:
    集合KEY: LRML5CDJ
    成功: 10 篇
    失败: 0 篇

  ... (其他类别)
```

---

## ⏰ GitHub Actions 自动化

### **快速设置**

#### 1. 添加 GitHub Secrets

在 GitHub 仓库中添加 Secrets:

| Secret 名称 | 值 |
|------------|-----|
| `ZOTERO_LIBRARY_ID` | `19092277` |
| `ZOTERO_API_KEY` | `your_api_key` |

#### 2. 推送工作流文件

工作流文件已创建在 `.github/workflows/daily-paper-collection.yml`

```bash
git add .github/workflows/
git commit -m "Add daily paper collection workflow"
git push
```

#### 3. 验证运行

1. 访问 GitHub 仓库的 **Actions** 标签页
2. 查看 "Daily ArXiv Paper Collection" 工作流
3. 可手动点击 **"Run workflow"** 立即测试

### **调度时间**

**默认配置**:
- **UTC 时间**: 每天 03:00
- **北京时间**: 每天 11:00

**修改运行时间**:

编辑 `.github/workflows/daily-paper-collection.yml`:

```yaml
schedule:
  - cron: '0 3 * * *'  # 分 时 日 月 周
```

---

## 🧪 测试

### **运行所有测试**

```bash
python -m pytest tests/ -v
```

### **测试重复检测**

```bash
python -m pytest tests/test_duplicate_detection.py -v
```

### **测试 API 优化**

```bash
python dev-tools/test_api_optimization.py
```

---

## 📖 文档索引

| 文档 | 内容 | 目标读者 |
|------|------|----------|
| [README.md](README.md) | 项目概览和快速开始 | 所有用户 |
| [PROJECT_GUIDE.md](PROJECT_GUIDE.md) | 本文件 - 完整使用指南 | 所有用户 |
| [API_OPTIMIZATION_SUMMARY.md](API_OPTIMIZATION_SUMMARY.md) | API 优化详细说明 | 开发者 |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构和模块说明 | 开发者 |
| [SETUP_ENVIRONMENT.md](SETUP_ENVIRONMENT.md) | 虚拟环境设置指南 | 新手用户 |
| [docs/api-docs.md](docs/api-docs.md) | API 详细文档 | 开发者 |

---

## 🔧 故障排查

### **常见问题**

#### 1. 编码错误（Windows）

**症状**: 控制台显示乱码或 UnicodeEncodeError

**解决方案**:
```bash
chcp 65001  # 切换到 UTF-8 编码
python scripts/auto_collect.py
```

#### 2. API 速率限制

**症状**: 日志显示 "接近 Zotero API 速率限制,等待..."

**说明**: 正常现象,系统会自动等待并继续

**解决**: 等待即可,或减少 `MAX_RESULTS_PER_CATEGORY`

#### 3. 所有论文都是重复的

**原因**: 时间范围内没有新论文

**验证**: 检查日志中的"起始时间"

#### 4. 工作流运行失败

**解决步骤**:
1. 查看 Actions 页面的详细日志
2. 检查 GitHub Secrets 配置
3. 确认依赖包安装成功

---

## 🛡️ 安全注意事项

- ⚠️ **不要**将 `.env` 文件提交到 Git
- ⚠️ **不要**在代码中硬编码 API Key
- ✅ 使用 `.env.example` 提供配置模板
- ✅ 定期更换 Zotero API Key
- ✅ 使用最小权限原则配置 API Key

---

## 💡 最佳实践

### **定期运行建议**

- **每天运行**: 保持文献库最新
- **每周运行**: 平衡更新频率和 API 使用
- **手动运行**: 需要特定文献时立即运行

### **查询优化**

- 使用具体关键词,避免过于宽泛
- 使用 `NOT survey NOT review` 排除综述文章
- 定期更新关键词以匹配最新研究趋势

### **监控和维护**

- 每周检查 Zotero 中的论文质量
- 查看采集日志了解运行状况
- 定期清理重复论文
- 定期更新依赖包

---

## 📞 获取帮助

### **遇到问题？**

1. **查看日志**: 检查 `logs/arxiv_zotero.log` 文件
2. **运行测试**: `python -m pytest tests/`
3. **查看文档**: 阅读相关章节的详细说明
4. **提交 Issue**: [GitHub Issues](https://github.com/StepanKropachev/arxiv-zotero-connector/issues)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**版本**: 2.0.0 (优化版)
**最后更新**: 2026-01-04
**维护状态**: 活跃开发中

---

**Made with ❤️ by [Stepan Kropachev](https://github.com/StepanKropachev)**
