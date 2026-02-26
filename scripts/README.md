# Scripts - 工具脚本

PaperFlow 项目工具脚本目录。

## 📋 脚本列表

### ☁️ 云端模式（自动采集）
- **`run_auto_collection.py`** - 云端自动采集论文（GitHub Actions 定时任务使用）

### 💻 本地模式（手动搜索）
- **`run_manual_search.py`** - 本地手动搜索并保存论文

### 日志管理
- **`clean_logs.sh` / `clean_logs.bat`** - 清理日志文件（保留最近 N 条记录）

```bash
# 使用清理脚本
bash scripts/clean_logs.sh      # Linux/Mac: 保留最近 30 条
scripts\clean_logs.bat          # Windows: 保留最近 30 条
bash scripts/clean_logs.sh 50   # 自定义保留数量
```

```bash
# 基本用法
python scripts/run_manual_search.py -k "deep learning"

# 启用期刊排序
python scripts/run_manual_search.py -k "computer vision" -e

# 更多结果
python scripts/run_manual_search.py -k "neural networks" -m 50

# 预览模式
python scripts/run_manual_search.py -k "quantum" --dry-run
```

## 🔧 常用参数

| 参数 | 短选项 | 说明 |
|------|--------|------|
| `--keywords` | `-k` | 搜索关键词 |
| `--max-results` | `-m` | 最大结果数（默认50） |
| `--no-pdf` | `-n` | 不下载 PDF |
| `--enable-chinaxiv` | `-x` | 启用中文预印本搜索 |
| `--enable-openalex` | `-e` | 启用期刊影响力排序 |
| `--dry-run` | | 预览模式，不实际保存 |

## 📚 相关文档

- [主 README](../README.md)
- [测试文档](../tests/README.md)
