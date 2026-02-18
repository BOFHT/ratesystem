@echo off
echo ========================================
echo 最简单更新指南
echo ========================================
echo.
echo 只需做两件事：
echo.
echo 1. 复制我的文件到你的GitHub仓库
echo 2. 在Render重新部署
echo.
echo ========================================
echo 第一步：复制这些文件
echo ========================================
echo.
echo 复制以下文件到你的GitHub仓库：
echo.
echo A. 根目录文件：
echo   - Dockerfile
echo   - requirements.txt
echo   - main.py
echo   - start.sh
echo.
echo B. Backend目录文件：
echo   - backend/app_simple.py     (最重要！)
echo   - backend/database_sqlite.py (最重要！)
echo   - backend/config_cloud.py
echo.
echo C. 指南文件：
echo   - README_DEPLOY.md
echo   - GITHUB_UPLOAD_GUIDE.md
echo.
echo 文件位置：
echo C:\Users\ASUS\.openclaw\workspace\upload_to_github\
echo.
pause

echo.
echo ========================================
echo 第二步：GitHub操作
echo ========================================
echo.
echo 打开浏览器，访问：
echo https://github.com/BOFHT/ratesystem
echo.
echo 然后：
echo 1. 点击 "Add file" → "Upload files"
echo 2. 选择上述文件
echo 3. 提交信息："修复部署"
echo 4. 点击 "Commit changes"
echo.
pause

echo.
echo ========================================
echo 第三步：Render操作
echo ========================================
echo.
echo 打开浏览器，访问：
echo https://render.com
echo.
echo 然后：
echo 1. 找到你的应用
echo 2. 点击 "Manual Deploy"
echo 3. 选择 "Deploy latest commit"
echo 4. 等待5分钟
echo.
pause

echo.
echo ========================================
echo 第四步：测试
echo ========================================
echo.
echo 部署完成后，访问：
echo.
echo 1. 健康检查：
echo    https://你的应用.onrender.com/health
echo    应该看到：{"status": "healthy"}
echo.
echo 2. API文档：
echo    https://你的应用.onrender.com/docs
echo    应该看到：交互式文档
echo.
echo 3. 演示数据：
echo    https://你的应用.onrender.com/api/demo
echo    应该看到：演示数据创建成功
echo.
pause

echo.
echo ========================================
echo 如果遇到问题：
echo ========================================
echo.
echo 1. 检查GitHub仓库文件是否完整
echo 2. 查看Render构建日志
echo 3. 确保所有必需文件都上传了
echo.
echo 必需文件清单：
echo   ✅ backend/app_simple.py
echo   ✅ backend/database_sqlite.py
echo   ✅ Dockerfile
echo   ✅ requirements.txt
echo   ✅ main.py
echo.
echo ========================================
echo 完成！
echo ========================================
echo.
pause