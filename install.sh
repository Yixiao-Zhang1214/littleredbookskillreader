#!/bin/bash
# 小红书产品经理技能分析器 - 安装脚本 (macOS/Linux)

set -e

echo "========================================="
echo "  小红书产品经理技能分析器 - 安装向导"
echo "========================================="
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ 错误: 未找到 Python，请先安装 Python 3.10 或更高版本"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | awk '{print $2}')
echo "✅ 检测到 Python $PYTHON_VERSION"

# 检查 Agent Reach (可选依赖) - 非交互模式，跳过
echo ""
echo "🔧 检查可选依赖: Agent Reach..."
if command -v agent-reach &> /dev/null; then
    echo "✅ Agent Reach 已安装"
else
    echo "ℹ️ 未检测到 Agent Reach（可选依赖，用于小红书内容获取）"
    echo "   如需安装，可手动运行: pip install agent-reach"
fi

echo ""
echo "🚀 自动安装到 Trae..."
if [ -f "install_skill_to_trae.py" ]; then
    $PYTHON_CMD install_skill_to_trae.py
fi

echo ""
echo "📖 使用方法:"
echo "  1. 在 Trae 中刷新技能列表"
echo "  2. 对 AI 说: \"请帮我分析这个小红书产品经理技能笔记\""
echo "  3. 或者直接运行安全扫描: ./run.sh"
echo ""
echo "💡 提示: 建议在 Trae 中使用 Qwen3.6-Plus 或 Gemini-3.1-Pro-Preview 模型"
echo ""
