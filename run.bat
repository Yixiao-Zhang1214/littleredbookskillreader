@echo off
REM 小红书产品经理技能分析器 - 运行脚本 (Windows)

set SCRIPT_DIR=%~dp0

echo =========================================
echo   小红书产品经理技能分析器 - 安全扫描
echo =========================================
echo.

if "%~1"=="" (
    echo 用法: %0 "包含 GitHub 链接的文本"
    echo.
    echo 示例:
    echo   %0 "github.com/user/repo"
    echo.
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"
python xhs_analyzer_pipeline.py %1
