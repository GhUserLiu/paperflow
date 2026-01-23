#!/bin/bash
echo "=== CI 诊断脚本 ==="
echo ""
echo "1. 检查 .gitattributes 文件:"
if [ -f ".gitattributes" ]; then
    echo "   ✓ .gitattributes 存在"
    head -5 .gitattributes
else
    echo "   ✗ .gitattributes 不存在"
fi

echo ""
echo "2. 检查文件换行符:"
CRLF_COUNT=$(find arxiv_zotero scripts tests -name "*.py" -exec file {} \; | grep -c "CRLF" || true)
LF_COUNT=$(find arxiv_zotero scripts tests -name "*.py" -exec file {} \; | grep -c "LF" || true)
echo "   CRLF 文件: $CRLF_COUNT"
echo "   LF 文件: $LF_COUNT"

echo ""
echo "3. 运行 Black 检查:"
black --check arxiv_zotero scripts tests && echo "   ✓ Black 通过" || echo "   ✗ Black 失败"

echo ""
echo "4. 运行 isort 检查:"
isort --check-only arxiv_zotero scripts tests && echo "   ✓ isort 通过" || echo "   ✗ isort 失败"

echo ""
echo "5. 运行测试:"
pytest tests/ -v --tb=short 2>&1 | tail -10

echo ""
echo "6. Git 状态:"
git status --short

echo ""
echo "7. 最新提交:"
git log --oneline -3

echo ""
echo "=== 诊断完成 ==="
