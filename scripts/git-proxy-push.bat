@echo off
REM Git Proxy Push - 使用代理推送代码
REM 用途: 当推送失败时自动使用代理重试

set PROXY_PORT=7897
set PROXY_URL=http://127.0.0.1:%PROXY_PORT%

echo 🔄 尝试推送...
git push
if %errorlevel% equ 0 (
    echo ✅ 推送成功！
    exit /b 0
)

echo ⚠️  推送失败，尝试使用代理 %PROXY_URL%...
git config --global http.proxy %PROXY_URL%
git config --global https.proxy %PROXY_URL%

git push
if %errorlevel% equ 0 (
    echo ✅ 使用代理推送成功！
    echo ℹ️  代理配置已保留，如需取消请运行: git config --global --unset http.proxy ^&^& git config --global --unset https.proxy
    exit /b 0
) else (
    echo ❌ 推送仍然失败，请检查网络和代理设置
    exit /b 1
)
