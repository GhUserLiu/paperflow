@echo off
REM 开发环境设置脚本 | Development Environment Setup Script (Windows)
REM 用途: 安装开发依赖并配置 pre-commit hooks

echo ========================================
echo   ArXiv Zotero Connector - 开发环境设置
echo   Development Environment Setup
echo ========================================
echo.

REM 检查 Python 版本 | Check Python version
echo 📋 检查 Python 版本... | Checking Python version...
python --version
echo.

REM 安装项目及其开发依赖 | Install project with dev dependencies
echo 📦 安装开发依赖... | Installing development dependencies...
pip install -e ".[all]"
echo.

REM 安装 pre-commit | Install pre-commit
echo 🔧 安装 pre-commit... | Installing pre-commit...
pre-commit --version
echo.

REM 安装 pre-commit hooks | Install pre-commit hooks
echo ⚙️  配置 git hooks... | Setting up git hooks...
pre-commit install
echo.

REM 可选: 在 pre-commit push 时运行 | Optional: Run on push
set /p ENABLE_PUSH="是否启用 pre-commit push 钩子? Enable pre-commit on push? [y/N]: "
if /i "%ENABLE_PUSH%"=="y" (
    pre-commit install --hook-type pre-push
    echo    ✅ Pre-push hooks 已启用 | Pre-push hooks enabled
)

REM 运行 pre-commit 对所有文件 | Run pre-commit on all files
echo.
set /p RUN_ALL="是否立即对所有文件运行 pre-commit? Run pre-commit on all files now? [y/N]: "
if /i "%RUN_ALL%"=="y" (
    pre-commit run --all-files
)

echo.
echo ========================================
echo   ✅ 开发环境设置完成! | Setup Complete!
echo ========================================
echo.
echo 📖 使用说明 | Usage:
echo    • Git hooks 会自动在 commit 时运行 | Hooks run automatically on commit
echo    • 跳过 hooks: git commit --no-verify | Skip hooks: git commit --no-verify
echo    • 手动运行: pre-commit run --all-files | Manual run: pre-commit run --all-files
echo    • 更新 hooks: pre-commit autoupdate | Update hooks: pre-commit autoupdate
echo.
pause
