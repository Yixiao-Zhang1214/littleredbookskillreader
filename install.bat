@echo off
REM 小红书产品经理技能分析器 - 安装脚本 (Windows)

echo =========================================
echo   小红书产品经理技能分析器 - 安装向导
echo =========================================
echo.

REM 检查 Python 版本
echo 🔍 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.10 或更高版本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ 检测到 Python %PYTHON_VERSION%

echo.
echo 🎉 安装完成!
echo.
echo 📖 使用方法:
echo   1. 在 Trae 中解压并打开此目录
echo   2. 复制 SKILL.md 到 Trae 的技能目录
echo   3. 或者直接运行: run.bat
echo.
echo 💡 提示: 建议在 Trae 中使用 Qwen3.6-Plus 或 Gemini-3.1-Pro-Preview 模型
echo.
pause
