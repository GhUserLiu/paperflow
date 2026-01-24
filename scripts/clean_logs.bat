@echo off
REM Clean Collection Log Script (Windows)
REM 清理 collection_log.md，只保留最近的 N 条记录

setlocal enabledelayedexpansion

REM 配置：保留最近 30 天的日志
set KEEP_DAYS=%1
if "%KEEP_DAYS%"=="" set KEEP_DAYS=30

set LOG_FILE=logs\collection_log.md

REM 检查文件是否存在
if not exist "%LOG_FILE%" (
    echo ❌ 日志文件不存在: %LOG_FILE%
    exit /b 1
)

REM 显示当前文件信息
echo 📊 当前日志文件信息:
for %%A in ("%LOG_FILE%") do (
    echo   文件: %LOG_FILE%
    echo   大小: %%~zA 字节
)
for /f %%A in ('type "%LOG_FILE%" ^| find /c /v ""') do set LINES=%%A
echo   行数: %LINES%
echo.

REM 备份原文件
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%LOG_FILE%.backup.%TIMESTAMP%
copy "%LOG_FILE%" "%BACKUP_FILE%" >nul
echo ✅ 已备份到: %BACKUP_FILE%

REM 读取文件并保留最近的记录
REM 由于 Windows batch 处理复杂，我们使用 PowerShell
powershell -Command ^
    "$keepDays = %KEEP_DAYS%; " ^
    "$logFile = '%LOG_FILE%'; " ^
    "$content = Get-Content $logFile -Raw; " ^
    "$matches = [regex]::Matches($content, '## 📚 Paper Collection Log[^\n]*\n(?:[^#]|\n(?!##))*'); " ^
    "$recentMatches = $matches | Select-Object -Last $keepDays; " ^
    "$recentMatches | ForEach-Object { Write-Output $_.Value.Trim() } | Out-File -FilePath $logFile -Encoding utf8"

echo ✅ 已保留最近 %KEEP_DAYS% 条记录

REM 显示清理后的文件信息
echo.
echo 📊 清理后日志文件信息:
for %%A in ("%LOG_FILE%") do (
    echo   文件: %LOG_FILE%
    echo   大小: %%~zA 字节
)
for /f %%A in ('type "%LOG_FILE%" ^| find /c /v ""') do set LINES=%%A
echo   行数: %LINES%

endlocal
