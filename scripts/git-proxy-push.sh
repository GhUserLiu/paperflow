#!/bin/bash
# Git Proxy Push - 使用代理推送代码
# 用途: 当推送失败时自动使用代理重试

PROXY_PORT=7897
PROXY_URL="http://127.0.0.1:${PROXY_PORT}"

echo "🔄 尝试推送..."
if git push; then
    echo "✅ 推送成功！"
    exit 0
fi

echo "⚠️  推送失败，尝试使用代理 ${PROXY_URL}..."
git config --global http.proxy "$PROXY_URL"
git config --global https.proxy "$PROXY_URL"

if git push; then
    echo "✅ 使用代理推送成功！"
    echo "ℹ️  代理配置已保留，如需取消请运行: git config --global --unset http.proxy && git config --global --unset https.proxy"
    exit 0
else
    echo "❌ 推送仍然失败，请检查网络和代理设置"
    exit 1
fi
