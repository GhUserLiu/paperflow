# 开发者工具脚本 | Developer Tools Scripts

本目录包含用于项目开发和维护的实用脚本。
This directory contains utility scripts for project development and maintenance.

---

## 📋 脚本列表 | Script List

### 1. setup_dev.sh / setup_dev.bat
**用途**: 一键配置开发环境 | **Purpose**: One-command development environment setup

**功能 | Features**:
- ✅ 检查 Python 版本 | Check Python version
- ✅ 安装所有开发依赖 | Install all development dependencies
- ✅ 配置 pre-commit git hooks | Configure pre-commit git hooks
- ✅ 可选: 启用 pre-push hooks | Optional: Enable pre-push hooks
- ✅ 可选: 首次对所有文件运行检查 | Optional: Run checks on all files

**使用方法 | Usage**:

Linux/Mac:
```bash
bash scripts/setup_dev.sh
# 或
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

Windows:
```batch
scripts\setup_dev.bat
# 或双击运行
```

---

### 2. auto_collect.py
**用途**: 自动收集 ArXiv 论文 | **Purpose**: Automatic ArXiv paper collection

**使用方法 | Usage**:
```bash
python scripts/auto_collect.py
```

**环境变量 | Environment Variables**:
- `ZOTERO_LIBRARY_ID`: Zotero 库 ID
- `ZOTERO_API_KEY`: Zotero API 密钥

---

### 3. git-proxy-push.sh / git-proxy-push.bat
**用途**: 智能推送（失败时自动使用代理）| **Purpose**: Smart push with auto-proxy fallback

**功能 | Features**:
- ✅ 首先尝试直接推送 | Try direct push first
- ✅ 失败时自动使用代理重试 | Auto-retry with proxy on failure
- ✅ 代理端口: 7897（可修改）| Proxy port: 7897 (configurable)

**使用方法 | Usage**:

Linux/Mac:
```bash
bash scripts/git-proxy-push.sh
```

Windows:
```batch
scripts\git-proxy-push.bat
```

**配置代理端口 | Configure Proxy Port**:
编辑脚本中的 `PROXY_PORT` 变量（默认 7897）

---

### 3. search_papers.py
**用途**: 搜索 ArXiv 论文 | **Purpose**: Search ArXiv papers

**使用方法 | Usage**:
```bash
python scripts/search_papers.py --keywords "deep learning"
```

---

## 🔧 Pre-commit Hooks

项目配置了以下 pre-commit hooks:
The project is configured with the following pre-commit hooks:

| Hook | 功能 | Purpose |
|------|------|---------|
| Black | 代码格式化 | Code formatting |
| isort | Import 排序 | Import sorting |
| Flake8 | 代码风格检查 | Style guide enforcement |
| MyPy | 类型检查 | Type checking |
| Bandit | 安全检查 | Security linting |
| trailing-whitespace | 移除尾随空白 | Remove trailing whitespace |
| end-of-file-fixer | 确保文件以换行符结尾 | Ensure files end with newline |
| check-yaml/json/toml | 配置文件语法检查 | Config file syntax check |

---

## 📦 依赖安装选项

### 安装核心依赖 | Core dependencies only
```bash
pip install -e .
```

### 安装开发依赖 | Development dependencies
```bash
pip install -e ".[dev]"
```

### 安装测试依赖 | Testing dependencies
```bash
pip install -e ".[test]"
```

### 安装所有依赖 | All dependencies
```bash
pip install -e ".[all]"
```

---

## 🛠️ 常用开发命令

### 代码质量检查 | Code quality checks
```bash
# 手动运行所有 pre-commit hooks
pre-commit run --all-files

# 运行特定 hook
pre-commit run black --all-files
pre-commit run flake8 --all-files

# 跳过 hooks (紧急情况)
git commit --no-verify -m "message"
```

### 测试 | Testing
```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=arxiv_zotero --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_performance.py

# 运行特定测试函数
pytest tests/unit/test_performance.py::TestPerformanceMonitor::test_init
```

### 代码格式化 | Code formatting
```bash
# 格式化代码
black arxiv_zotero scripts tests

# 排序 imports
isort arxiv_zotero scripts tests
```

---

## 🔄 更新 Pre-commit Hooks

定期更新 pre-commit hooks 以获得最新版本:
Update pre-commit hooks regularly to get the latest versions:

```bash
pre-commit autoupdate
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks"
```

---

## 📚 相关文档

- [项目结构](../docs/PROJECT_STRUCTURE.md)
- [架构文档](../docs/ARCHITECTURE.md)
- [改进记录](../docs/IMPROVEMENTS.md)
- [主 README](../README.md)
