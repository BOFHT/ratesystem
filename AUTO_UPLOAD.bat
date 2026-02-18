@echo off
echo ========================================
echo 自动上传脚本
echo ========================================
echo.
echo 这个脚本会自动：
echo 1. 克隆你的GitHub仓库
echo 2. 复制所有修复文件
echo 3. 提交并推送到GitHub
echo.
echo 你需要：
echo 1. GitHub Token（仅仓库权限）
echo 2. 稳定的网络连接
echo.
set /p token="请输入GitHub Token: "

if "%token%"=="" (
    echo ❌ 需要GitHub Token
    pause
    exit /b 1
)

echo.
echo ========================================
echo 步骤1：克隆仓库
echo ========================================
echo.
echo 正在克隆仓库...
git clone https://%token%@github.com/BOFHT/ratesystem.git temp_ratesystem

if errorlevel 1 (
    echo ❌ 克隆失败，请检查Token
    pause
    exit /b 1
)

echo ✅ 仓库克隆成功
cd temp_ratesystem

echo.
echo ========================================
echo 步骤2：复制修复文件
echo ========================================
echo.
echo 正在复制文件...
xcopy /Y "..\*" "." > nul
xcopy /Y "..\backend\*" "backend\" > nul

echo ✅ 文件复制完成

echo.
echo ========================================
echo 步骤3：验证文件
echo ========================================
echo.
echo 检查必需文件：
echo.

if exist "backend\app_simple.py" (
    echo ✅ backend/app_simple.py
) else (
    echo ❌ backend/app_simple.py (缺失)
)

if exist "backend\database_sqlite.py" (
    echo ✅ backend/database_sqlite.py
) else (
    echo ❌ backend/database_sqlite.py (缺失)
)

if exist "Dockerfile" (
    echo ✅ Dockerfile
) else (
    echo ❌ Dockerfile (缺失)
)

if exist "requirements.txt" (
    echo ✅ requirements.txt
) else (
    echo ❌ requirements.txt (缺失)
)

if exist "main.py" (
    echo ✅ main.py
) else (
    echo ❌ main.py (缺失)
)

echo.
set /p continue="是否继续上传？(y/n): "
if /i not "%continue%"=="y" (
    echo 操作取消
    cd ..
    rmdir /s /q temp_ratesystem
    pause
    exit /b 0
)

echo.
echo ========================================
echo 步骤4：提交更改
echo ========================================
echo.
echo 正在提交更改...
git add .
git commit -m "修复部署问题：添加缺失模块和配置文件"
git push origin main

if errorlevel 1 (
    echo ❌ 提交/推送失败
    cd ..
    rmdir /s /q temp_ratesystem
    pause
    exit /b 1
)

echo ✅ 更改已推送到GitHub

echo.
echo ========================================
echo 步骤5：清理
echo ========================================
echo.
cd ..
rmdir /s /q temp_ratesystem
echo ✅ 临时文件已清理

echo.
echo ========================================
echo 🎉 上传完成！
echo ========================================
echo.
echo 下一步操作：
echo.
echo 1. 访问 https://render.com
echo 2. 找到你的应用
echo 3. 点击 "Manual Deploy"
echo 4. 选择 "Deploy latest commit"
echo 5. 等待5-10分钟
echo.
echo 测试应用：
echo   - https://你的应用.onrender.com/health
echo   - https://你的应用.onrender.com/docs
echo.
echo 重要：完成后请撤销GitHub Token
echo      访问：https://github.com/settings/tokens
echo.
pause