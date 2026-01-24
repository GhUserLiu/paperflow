# 日志清理配置总结 | Log Cleanup Setup Summary

## ✅ 完成的配置

### 1️⃣ 自动清理（GitHub Actions）

**位置**：[`.github/workflows/daily-paper-collection.yml:77-111`](../.github/workflows/daily-paper-collection.yml#L77-L111)

**功能**：
- ✅ 每次自动运行后检查日志记录数
- ✅ 超过 30 条自动清理
- ✅ 保留最近 30 条记录
- ✅ 自动提交清理后的文件

**清理策略**：
```yaml
if [ "$RECORD_COUNT" -gt 30 ]; then
    # 保留最近 30 条记录
    # 删除旧记录
    # 提交更改
fi
```

**优点**：
- 完全自动化，无需手动干预
- 每次运行后自动维护
- 保持文件大小稳定（~150 KB）

---

### 2️⃣ 手动清理脚本

#### Linux/Mac 脚本
**文件**：[`scripts/clean_logs.sh`](../scripts/clean_logs.sh)
**权限**：`chmod +x scripts/clean_logs.sh` ✅

#### Windows 脚本
**文件**：[`scripts/clean_logs.bat`](../scripts/clean_logs.bat)

**功能**：
- ✅ 自动备份原文件
- ✅ 保留指定数量的记录
- ✅ 显示清理前后大小
- ✅ 询问是否删除备份

**使用示例**：
```bash
# 默认保留 30 条
bash scripts/clean_logs.sh

# 自定义保留数量
bash scripts/clean_logs.sh 50
```

---

### 3️⃣ 文档

**详细指南**：[docs/LOG_CLEANUP_GUIDE.md](LOG_CLEANUP_GUIDE.md)

**包含内容**：
- 自动清理说明
- 手动清理方法
- 日志大小估算
- 自定义配置
- 常见问题解答

**脚本文档**：[scripts/README.md](../scripts/README.md)（已更新）

---

## 📊 配置效果

### 自动清理效果

| 时间 | 运行次数 | 记录数 | 文件大小 | 状态 |
|------|---------|-------|---------|------|
| **初始** | 0 | 0 | 0 B | ✅ |
| **1 个月** | 30 | 30 | ~150 KB | ✅ 达到阈值 |
| **31 天** | 31 | 30 | ~150 KB | ✅ 自动清理 |
| **1 年** | 365 | 30 | ~150 KB | ✅ 持续维护 |

### 日志增长控制

**清理前**（无控制）：
```
30 天  → ~150 KB
90 天  → ~450 KB
1 年  → ~1.8 MB
```

**清理后**（自动控制）：
```
任何时间 → ~150 KB（稳定）
```

---

## 🎯 清理策略对比

### 方案 1：自动清理（当前配置）✅ 推荐

| 特性 | 说明 |
|------|------|
| **触发** | 每次运行后自动检查 |
| **阈值** | 30 条记录 |
| **维护** | 零维护，完全自动 |
| **文件大小** | ~150 KB（稳定） |
| **历史保存** | 30 天记录 + GitHub Artifacts |

### 方案 2：手动清理

| 特性 | 说明 |
|------|------|
| **触发** | 手动运行脚本 |
| **灵活性** | 可自定义保留数量 |
| **适用场景** | 紧急清理、自定义策略 |

### 方案 3：禁用清理 ❌ 不推荐

| 特性 | 说明 |
|------|------|
| **文件大小** | 1 年 ~2 MB |
| **风险** | 可能持续增长 |
| **建议** | 仅用于测试 |

---

## 🔧 自定义配置

### 修改自动清理阈值

编辑 `.github/workflows/daily-paper-collection.yml`：

```yaml
# 第 87 行 - 修改数字
if [ "$RECORD_COUNT" -gt 30 ]; then  # ← 改为你想要的数字
```

**推荐值**：
- **10** - 激进清理（~50 KB）
- **30** - 平衡推荐（~150 KB）✅
- **60** - 更多历史（~300 KB）
- **90** - 3 个月历史（~450 KB）

### 修改 Artifacts 保留期

```yaml
# 第 85 行
retention-days: 30  # ← 修改天数（1-90 天）
```

---

## 📝 使用建议

### 日常使用
1. ✅ **保持自动清理开启**：无需手动干预
2. ✅ **定期检查**：每月查看一次日志文件大小
3. ✅ **监控 GitHub Actions**：查看清理是否正常执行

### 手动清理时机
- ⚠️ **日志过大**：手动运行清理脚本
- ⚠️ **测试新策略**：先手动测试，再修改自动配置
- ⚠️ **紧急情况**：快速清理大量记录

### 最佳实践
1. ✅ 使用默认配置（30 条记录）
2. ✅ 利用 GitHub Artifacts 保存完整日志（30 天）
3. ✅ Git 提交历史包含所有更改
4. ✅ 本地备份重要日志（如需要）

---

## 🚀 快速开始

### 立即清理（手动）

```bash
# Linux/Mac
bash scripts/clean_logs.sh

# Windows
scripts\clean_logs.bat
```

### 查看当前状态

```bash
# 查看日志大小
du -h logs/collection_log.md

# 统计记录数
grep -c "^## 📚 Paper Collection Log" logs/collection_log.md

# 查看最近日志
tail -50 logs/collection_log.md
```

---

## 📚 相关文档

- [日志清理详细指南](LOG_CLEANUP_GUIDE.md)
- [GitHub Actions 工作流](../.github/workflows/daily-paper-collection.yml)
- [清理脚本（Linux/Mac）](../scripts/clean_logs.sh)
- [清理脚本（Windows）](../scripts/clean_logs.bat)
- [脚本文档](../scripts/README.md)

---

## ✅ 配置清单

- [x] GitHub Actions 自动清理（30 条记录）
- [x] Linux/Mac 清理脚本
- [x] Windows 清理脚本
- [x] 详细文档
- [x] 脚本执行权限
- [x] README 更新

---

**配置完成时间**：2026-01-24
**配置版本**：v1.0
**状态**：✅ 已启用
