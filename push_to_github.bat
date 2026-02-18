@echo off
echo ========================================
echo GitHub上传脚本
echo ========================================
echo.

REM 设置GitHub用户名（请修改为你的用户名）
set GITHUB_USERNAME=YOUR_GITHUB_USERNAME

REM 设置仓库名称
set REPO_NAME=project-rating-system

echo 正在准备推送代码到GitHub...
echo 仓库: %REPO_NAME%
echo.

echo 步骤1: 添加远程仓库
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo 步骤2: 重命名分支为main
git branch -M main

echo 步骤3: 推送代码
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo 推送失败！
    echo 请按以下步骤操作：
    echo 1. 访问 https://github.com/new 创建仓库 %REPO_NAME%
    echo 2. 在GitHub创建仓库后，复制推送命令
    echo 3. 手动执行推送命令
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo 推送成功！
    echo 仓库地址: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
    pause
)