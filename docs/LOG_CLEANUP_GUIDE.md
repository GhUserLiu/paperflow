# 日志清理指南 | Log Cleanup Guide

## 📋 概述

PaperFlow 每天自动运行后会在 `logs/collection_log.md` 中添加日志记录。为了防止文件无限增长，项目提供了自动和手动清理机制。

---

## 🤖 自动清理（推荐）

### GitHub Actions 自动清理

**触发时机**：每次 GitHub Actions 运行后
**清理策略**：保留最近 **30 条**日志记录

**工作原理**：
1. 每次运行后，自动检查日志记录数
2. 如果超过 30 条，自动删除旧记录
3. 保留最近 30 条记录
4. 自动提交清理后的文件

**配置位置**：[`.github/workflows/daily-paper-collection.yml:77-111`](../.github/workflows/daily-paper-collection.yml#L77-L111)

**优点**：
- ✅ 完全自动，无需手动干预
- ✅ 每次运行后自动清理
- ✅ 保持文件大小稳定（~5-10 KB）

---

## 🛠️ 手动清理

### 方法 1：使用清理脚本

#### Linux/Mac

```bash
# 保留最近 30 条记录（默认）
bash scripts/clean_logs.sh

# 保留最近 50 条记录
bash scripts/clean_logs.sh 50

# 保留最近 10 条记录
bash scripts/clean_logs.sh 10
```

#### Windows

```batch
REM 保留最近 30 条记录（默认）
scripts\clean_logs.bat

REM 保留最近 50 条记录
scripts\clean_logs.bat 50
```

**脚本功能**：
- 自动备份原文件（`collection_log.md.backup.YYYYMMDD_HHMMSS`）
- 保留指定数量的日志记录
- 显示清理前后的文件大小
- 询问是否删除备份

### 方法 2：手动编辑

```bash
# 1. 打开日志文件
vim logs/collection_log.md

# 2. 删除旧的日志块（以 "## 📚 Paper Collection Log" 开头）
# 3. 保留你需要的记录
# 4. 保存文件
```

---

## 📊 日志大小估算

| 运行天数 | 记录数 | 估算大小 | 实际大小 |
|---------|-------|---------|---------|
| 1 天 | 1 | ~5 KB | 5.5 KB |
| 30 天 | 30 | ~150 KB | ~150 KB |
| 90 天 | 90 | ~450 KB | ~450 KB |
| 365 天 | 365 | ~1.8 MB | ~1.8 MB |

**结论**：即使 1 年不清理，也只有 ~2 MB，完全在可接受范围内。

---

## ⚙️ 自定义清理策略

### 修改自动清理阈值

编辑 `.github/workflows/daily-paper-collection.yml`：

```yaml
# 第 87 行
if [ "$RECORD_COUNT" -gt 30 ]; then  # 修改这个数字
```

**推荐值**：
- **10 条**：激进清理，文件最小（~50 KB）
- **30 条**：平衡推荐（~150 KB）
- **60 条**：保留更多历史（~300 KB）
- **90 条**：保留 3 个月历史（~450 KB）

### 修改 GitHub Artifacts 保留期

编辑 `.github/workflows/daily-paper-collection.yml`：

```yaml
# 第 85 行
retention-days: 30  # 修改这个数字
```

**说明**：
- GitHub Artifacts 自动删除
- 不影响 `logs/collection_log.md`
- 默认保留 30 天

---

## 🔍 查看当前日志状态

```bash
# 查看日志文件大小
du -h logs/collection_log.md

# 统计日志记录数
grep -c "^## 📚 Paper Collection Log" logs/collection_log.md

# 查看最近的日志
tail -100 logs/collection_log.md

# 查看最早的日志
head -50 logs/collection_log.md
```

---

## 🚨 紧急清理

如果日志文件过大（> 1 MB），执行紧急清理：

```bash
# 方案 1：完全清空
> logs/collection_log.md
git add logs/collection_log.md
git commit -m "🧹 Emergency: clear collection log"

# 方案 2：只保留最近 5 条
bash scripts/clean_logs.sh 5
```

---

## 📝 最佳实践

1. **使用自动清理**：默认配置已足够，无需手动干预
2. **定期检查**：每月检查一次日志文件大小
3. **备份重要日志**：如需保存特定日志，复制到其他位置
4. **使用 GitHub Artifacts**：完整的日志保存在 Artifacts 中（30 天）

---

## ❓ 常见问题

### Q: 自动清理会丢失历史数据吗？
**A**: 不会。GitHub Actions Artifacts 保留完整日志 30 天，可以下载查看。

### Q: 可以完全禁用日志记录吗？
**A**: 可以，但不推荐。编辑 `.github/workflows/daily-paper-collection.yml`，注释掉日志提交步骤。

### Q: 日志文件会触发 GitHub 警告吗？
**A**: 不会。即使 1 年不清理也只有 ~2 MB，远低于限制。

### Q: 如何查看历史日志？
**A**:
1. GitHub 仓库提交历史（`git log`）
2. GitHub Actions Artifacts（30 天）
3. 本地备份文件（`collection_log.md.backup.*`）

---

**文档更新**: 2026-01-24
