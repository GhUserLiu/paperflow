#!/bin/bash
# Clean Collection Log Script
# 清理 collection_log.md，只保留最近的 N 条记录

# 配置：保留最近 30 天的日志
KEEP_DAYS=${1:-30}
LOG_FILE="logs/collection_log.md"

# 检查文件是否存在
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在: $LOG_FILE"
    exit 1
fi

# 显示当前文件大小
echo "📊 当前日志文件信息:"
echo "  文件: $LOG_FILE"
echo "  大小: $(du -h "$LOG_FILE" | cut -f1)"
echo "  行数: $(wc -l < "$LOG_FILE")"
echo ""

# 备份原文件
BACKUP_FILE="${LOG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$LOG_FILE" "$BACKUP_FILE"
echo "✅ 已备份到: $BACKUP_FILE"

# 提取最近的 N 条记录
# 每个 record 以 "## 📚 Paper Collection Log" 开头
# 我们保留最近的 N 个完整记录

# 方法1: 保留最近的 N 个日志块（按日期标记）
if [ "$KEEP_DAYS" -gt 0 ]; then
    # 使用 awk 保留最近的记录
    awk -v days="$KEEP_DAYS" '
        BEGIN { found = 0 }
        /^## 📚 Paper Collection Log/ {
            # 提取日期
            match($0, /[0-9]{4}-[0-9]{2}-[0-9]{2}/, date_arr)
            if (date_arr[0] != "") {
                log_date = date_arr[0]
                # 计算日期差（简化版：只保留最近的几个记录）
                if (++count <= days) {
                    print_current = 1
                } else {
                    print_current = 0
                }
            }
        }
        print_current { print }
    ' "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"

    echo "✅ 已保留最近 $KEEP_DAYS 条记录"
else
    echo "⚠️  保留天数为 0，清空所有日志"
    > "$LOG_FILE"
fi

# 显示清理后的文件大小
echo ""
echo "📊 清理后日志文件信息:"
echo "  文件: $LOG_FILE"
echo "  大小: $(du -h "$LOG_FILE" | cut -f1)"
echo "  行数: $(wc -l < "$LOG_FILE")"

# 询问是否删除备份
echo ""
read -p "🗑️  是否删除备份文件? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$BACKUP_FILE"
    echo "✅ 已删除备份文件"
else
    echo "💾 备份文件已保留: $BACKUP_FILE"
fi
