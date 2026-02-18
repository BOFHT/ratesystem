@echo off
echo ========================================
echo 项目识别智能评分系统 - 开发环境启动脚本
echo ========================================
echo.

REM 检查Python环境
echo 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 创建虚拟环境
echo.
echo 创建Python虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo 虚拟环境创建成功
) else (
    echo 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 无法激活虚拟环境
    pause
    exit /b 1
)

REM 安装依赖
echo.
echo 安装Python依赖...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo 依赖安装完成！

REM 创建必要的目录
echo.
echo 创建必要的目录...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "models\cache" mkdir models\cache

echo.
echo 启动数据库服务...
echo 提示: 请确保PostgreSQL、MongoDB和Redis已安装并运行
echo 或使用Docker Compose启动所有服务
echo.

REM 询问是否启动后端
set /p start_backend="是否启动后端服务? (Y/N): "
if /i "%start_backend%"=="Y" (
    echo.
    echo 启动后端服务...
    echo API文档: http://localhost:8000/docs
    echo 健康检查: http://localhost:8000/health
    echo.
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
) else (
    echo.
    echo 跳过启动后端服务
    echo 手动启动命令:
    echo   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
)

pause