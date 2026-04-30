#!/bin/bash
# 小红书产品经理技能分析器 - 运行脚本 (macOS/Linux)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================="
echo "  小红书产品经理技能分析器 - 安全扫描"
echo "========================================="
echo ""

if [ $# -eq 0 ]; then
    echo "用法: $0 \"包含 GitHub 链接的文本\""
    echo ""
    echo "示例:"
    echo "  $0 \"github.com/user/repo\""
    echo ""
    exit 1
fi

cd "$SCRIPT_DIR"

if command -v python3 &> /dev/null; then
    python3 xhs_analyzer_pipeline.py "$1"
elif command -v python &> /dev/null; then
    python xhs_analyzer_pipeline.py "$1"
else
    echo "❌ 错误: 未找到 Python"
    exit 1
fi
