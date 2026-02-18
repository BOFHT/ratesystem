@echo off
echo ========================================
echo 智能评分系统 - Conda环境测试
echo ========================================
echo.

REM 检查conda
where conda >nul 2>nul
if errorlevel 1 (
    echo ❌ Conda未安装或不在PATH中
    echo 请确保Anaconda/Miniconda已正确安装
    pause
    exit /b 1
)

REM 显示conda信息
conda --version

echo.
echo 1. 激活或创建conda环境
echo ========================================

REM 检查环境是否存在
conda env list | findstr "project_rating" >nul
if errorlevel 1 (
    echo 创建 project_rating 环境...
    conda create -n project_rating python=3.9 -y
    if errorlevel 1 (
        echo ❌ 创建conda环境失败
        pause
        exit /b 1
    )
    echo ✅ 环境创建成功
) else (
    echo ✅ project_rating 环境已存在
)

echo.
echo 激活 project_rating 环境...
call conda activate project_rating
if errorlevel 1 (
    echo ⚠️ 尝试使用完整路径激活
    REM 尝试其他激活方式
    call activate project_rating
)

echo.
echo 2. 安装依赖
echo ========================================

REM 检查是否在正确环境中
python --version

echo.
echo 安装核心依赖 (conda-forge)...

REM 使用conda安装主要包
conda install -c conda-forge -y ^
    fastapi ^
    uvicorn ^
    sqlalchemy ^
    numpy ^
    scikit-learn ^
    nltk ^
    pandas ^
    pydantic

if errorlevel 1 (
    echo ⚠️ conda安装部分失败，尝试pip安装
)

echo.
echo 安装其他依赖 (pip)...
pip install -r requirements.txt

if errorlevel 1 (
    echo ⚠️ 部分依赖安装失败，尝试安装核心包
    pip install fastapi uvicorn sqlalchemy numpy scikit-learn nltk pydantic
)

echo.
echo 3. 验证安装
echo ========================================

python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import sklearn; print('✅ scikit-learn:', sklearn.__version__)"
python -c "import nltk; print('✅ NLTK:', nltk.__version__)"

echo.
echo 4. 运行快速测试
echo ========================================

echo 运行项目结构验证...
python verify_setup.py

if errorlevel 1 (
    echo ⚠️ 验证脚本运行失败
    echo 但环境应该已设置完成
)

echo.
echo ========================================
echo Conda环境设置完成！
echo ========================================
echo.
echo 下一步命令：
echo.
echo 1. 初始化数据库：
echo    python -m scripts.init_database
echo.
echo 2. 训练模型：
echo    python -m scripts.train_models
echo.
echo 3. 运行快速测试：
echo    python -m scripts.integration_test --quick
echo.
echo 4. 运行完整测试：
echo    python -m scripts.integration_test --full
echo.
echo 5. 启动服务：
echo    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
echo.
echo 完成后访问：
echo   API文档： http://localhost:8000/docs
echo   健康检查： http://localhost:8000/health
echo.
pause