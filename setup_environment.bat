@echo off
echo ========================================
echo 智能评分系统 - 环境设置脚本
echo ========================================
echo.

REM 检查Python
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请安装Python 3.8+ 并添加到PATH
    pause
    exit /b 1
)

REM 显示Python版本
python --version
if errorlevel 1 (
    echo ❌ Python版本检查失败
    pause
    exit /b 1
)

echo.
echo ✅ Python环境正常

REM 创建虚拟环境
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b 1
)

echo ✅ 虚拟环境已激活

REM 升级pip
echo.
echo 升级pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️ pip升级失败，继续安装依赖
)

REM 安装依赖
echo.
echo 安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    echo 尝试安装核心依赖...
    pip install fastapi uvicorn sqlalchemy numpy scikit-learn nltk
    if errorlevel 1 (
        echo ❌ 核心依赖安装也失败
        pause
        exit /b 1
    )
    echo ✅ 核心依赖安装成功
) else (
    echo ✅ 所有依赖安装成功
)

REM 创建必要的目录
echo.
echo 创建必要目录...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "models\cache" mkdir models\cache
if not exist "models\trained" mkdir models\trained

echo ✅ 目录结构已创建

REM 验证安装
echo.
echo 验证安装...
python -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'✅ SQLAlchemy {sqlalchemy.__version__}')"
python -c "import numpy; print(f'✅ NumPy {numpy.__version__}')"
python -c "import sklearn; print(f'✅ scikit-learn {sklearn.__version__}')"

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 初始化数据库： python -m scripts.init_database
echo 2. 训练模型： python -m scripts.train_models
echo 3. 运行测试： python -m scripts.integration_test --quick
echo 4. 启动服务： uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
echo.
echo API文档： http://localhost:8000/docs
echo 健康检查： http://localhost:8000/health
echo.
pause