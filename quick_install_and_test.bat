@echo off
echo ============================================================
echo 智能评分系统 - 快速安装和测试
echo ============================================================

REM 检查Python
echo.
echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo Python未找到，请确保已安装Python 3.8+
    pause
    exit /b 1
)

REM 安装依赖
echo.
echo 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo 依赖安装完成！

REM 运行快速测试
echo.
echo 运行快速系统测试...
python simple_test_no_emoji.py
if %errorlevel% neq 0 (
    echo 快速测试失败！
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 系统基本功能测试通过！
echo ============================================================
echo.
echo 下一步：
echo 1. 设置数据库连接（修改config.py中的数据库URL）
echo 2. 运行数据库初始化：python scripts/init_database.py
echo 3. 启动服务器：python backend/app.py
echo 4. 访问API文档：http://localhost:8000/docs
echo.
echo ============================================================
pause