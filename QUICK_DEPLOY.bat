@echo off
echo ========================================
echo 项目识别智能评分系统 - 快速部署指南
echo ========================================
echo.

echo 第一步：上传到GitHub
echo.
echo 1. 访问 https://github.com
echo 2. 点击右上角 "+" → "New repository"
echo 3. 填写信息：
echo    - Repository name: project-rating-system
echo    - Description: AI项目识别与智能评分系统
echo    - 选择 Public
echo 4. 点击 "Create repository"
echo 5. 上传本文件夹所有文件到GitHub
echo.

echo 第二步：部署到Render
echo.
echo 1. 访问 https://render.com
echo 2. 点击 "New +" → "Web Service"
echo 3. 点击 "Connect GitHub"
echo 4. 授权访问GitHub
echo 5. 选择 project-rating-system 仓库
echo 6. 配置：
echo    - Name: project-rating-system
echo    - Environment: Docker
echo    - Region: 选择最近的
echo 7. 点击 "Create Web Service"
echo.

echo 第三步：等待部署完成
echo.
echo 1. 等待5-10分钟构建完成
echo 2. 获取你的应用URL（如：https://project-rating-system.onrender.com）
echo 3. 测试应用：
echo    - 访问 /health 端点
echo    - 访问 /docs 查看API文档
echo    - 访问 /api/demo 创建演示数据
echo.

echo 第四步：验证部署
echo.
echo 打开浏览器访问：
echo 1. https://你的应用.onrender.com/health
echo   应该看到：{"status": "healthy"}
echo.
echo 2. https://你的应用.onrender.com/docs
echo   应该看到：API交互式文档
echo.
echo 3. https://你的应用.onrender.com/api/demo
echo   应该看到：演示数据创建成功
echo.

echo ========================================
echo 重要提示：
echo 1. 所有必需文件都在本文件夹中
echo 2. 部署可能需要5-10分钟
echo 3. 免费服务在闲置时会休眠
echo 4. 首次访问可能需要30秒唤醒
echo ========================================
echo.

echo 详细指南请查看 README_DEPLOY.md
echo GitHub上传指南请查看 GITHUB_UPLOAD_GUIDE.md
echo.

pause