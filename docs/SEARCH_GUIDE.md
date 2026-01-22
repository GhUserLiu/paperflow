# 灵活搜索脚本使用说明

## 📋 脚本对比

项目中有两个独立的脚本，互不干扰：

### 1. 每日定时任务 (scripts/auto_collect.py)
- **用途**: GitHub Actions 自动运行
- **集合**: 5个固定研究方向集合
- **时间范围**: 过去25小时
- **关键词**: 固定的5类查询
- **版本**: v2.0.0

### 2. 灵活搜索脚本 (search_papers.py) ⭐ 新增
- **用途**: 手动运行，灵活搜索
- **集合**: Temp 集合 (AQNIN4ZZ)
- **时间范围**: 无限制（最新论文）
- **关键词**: 完全自定义
- **版本**: 独立脚本

---

## 🚀 快速使用

### 基本用法

```bash
# 搜索自动驾驶相关论文（默认20篇）
python search_papers.py --keywords "autonomous driving"
```

### 高级用法

```bash
# 深度学习和计算机视觉
python search_papers.py --keywords '"deep learning" AND "computer vision"'

# 指定结果数量
python search_papers.py --keywords "V2X communication" --max-results 50

# 只搜索元数据，不下载 PDF（更快）
python search_papers.py --keywords "reinforcement learning" --no-pdf

# 保存到自定义集合
python search_papers.py --keywords "neural networks" --collection YOUR_COLLECTION_KEY
```

---

## 📝 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 搜索关键词（必需） | - |
| `--max-results` | 最大结果数 | 20 |
| `--no-pdf` | 不下载 PDF | 否 |
| `--collection` | 目标集合 KEY | AQNIN4ZZ (temp) |

---

## 🎯 使用场景

### 场景1: 探索新领域
你想了解"生成式 AI"在自动驾驶中的应用：

```bash
python search_papers.py --keywords '"generative AI" AND "autonomous driving"' --max-results 30
```

### 场景2: 快速收集特定论文
需要快速收集"强化学习在路径规划中的应用"的最新论文：

```bash
python search_papers.py --keywords '"reinforcement learning" AND "path planning"' --max-results 15
```

### 场景3: 不需要 PDF，只要元数据
只想看看有哪些论文，暂时不需要下载 PDF：

```bash
python search_papers.py --keywords "transformer" --no-pdf
```

---

## ⚠️ 重要说明

### 重复检测

✅ **已启用重复检测**
- 基于论文的 arXiv ID
- 全局搜索所有集合（包括 temp 和其他集合）
- 自动跳过已存在的论文

### 日志示例

```
INFO - Paper 2512.19694v1 already exists in library (item: ABC123), skipping
INFO - Processing paper: 2512.20001v1
INFO - Successfully created item with key: XYZ789
```

### 与定时任务的关系

**完全独立** - 不影响每日定时任务：
- 定时任务继续运行 → 保存到 5 个研究集合
- 手动搜索脚本 → 保存到 Temp 集合
- 两者互不干扰

---

## 🔍 集合说明

### Temp 集合 (AQNIN4ZZ)
- 用途：临时存放手动搜索的论文
- 管理：需要手动整理到正式集合
- 位置：与 5 个研究集合同级

### 整理建议

1. 在 Zotero 中查看 Temp 集合的论文
2. 将有价值的论文移动到相应的研究集合
3. 清理不需要的论文

---

## 📊 预期输出

```
======================================================================
arXiv 论文灵活搜索工具 | Flexible Search
======================================================================
开始时间: 2026-01-06 15:30:00
搜索关键词: autonomous driving
最大结果数: 20
目标集合: AQNIN4ZZ (temp)
下载 PDF: 是
======================================================================

正在搜索 arXiv...
提示: 这是独立的搜索脚本，不影响每日定时任务

[OK] collection completed:
  Successful: 18 papers
  Failed: 2 papers

======================================================================
搜索完成 | Search Complete
======================================================================
结束时间: 2026-01-06 15:35:45

总计:
  成功采集: 18 篇
  失败: 2 篇
  保存位置: Temp 集合 (AQNIN4ZZ)

提示: 重复检测已启用，已存在的论文会被跳过
======================================================================
```

---

## 💡 提示

1. **第一次运行**: 会添加所有论文
2. **再次运行相同关键词**: 会跳过已存在的论文
3. **不同关键词**: 可能会添加新论文
4. **版本**: 不影响 setup.py v2.0.0，保持兼容性

---

**创建时间**: 2026-01-06
**版本**: 独立脚本（不包含在包版本中）
**状态**: ✅ 可用
