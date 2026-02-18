@echo off
echo ========================================
echo GitHub仓库更新脚本
echo ========================================
echo.

echo 步骤1：检查当前目录
echo.
echo 当前目录：%cd%
echo.
echo 请确保你在正确的目录：
echo 应该是：C:\Users\ASUS\.openclaw\workspace\upload_to_github
echo.
pause

echo.
echo ========================================
echo 步骤2：列出所有修复文件
echo ========================================
echo.
echo 以下是需要上传到GitHub的关键文件：
echo.
echo A. 核心修复文件（必须上传）：
echo   1. Dockerfile
echo   2. requirements.txt
echo   3. main.py
echo   4. start.sh
echo   5. QUICK_DEPLOY.bat
echo.
echo B. Backend目录文件：
echo   6. backend\app_simple.py
echo   7. backend\database_sqlite.py
echo   8. backend\config_cloud.py
echo   9. backend\app_cloud.py
echo.
echo C. 部署指南：
echo   10. README_DEPLOY.md
echo   11. GITHUB_UPLOAD_GUIDE.md
echo   12. verify_deployment.py
echo   13. test_app.py
echo.
pause

echo.
echo ========================================
echo 步骤3：GitHub上传指南
echo ========================================
echo.
echo 方法一：使用GitHub网页界面
echo.
echo 1. 访问 https://github.com/BOFHT/ratesystem
echo 2. 点击 "Add file" → "Upload files"
echo 3. 将上述文件拖拽到上传区域
echo 4. 填写提交信息："修复部署问题"
echo 5. 点击 "Commit changes"
echo.
echo 方法二：使用Git命令
echo.
echo 如果你的本地有仓库副本：
echo git add .
echo git commit -m "修复部署问题"
echo git push origin main
echo.
echo 方法三：直接替换文件
echo.
echo 1. 在GitHub仓库中删除有问题的文件
echo 2. 上传修复后的文件
echo.
pause

echo.
echo ========================================
echo 步骤4：文件内容预览
echo ========================================
echo.
echo 1. Dockerfile 内容：
type Dockerfile
echo.
echo 2. requirements.txt 内容：
type requirements.txt
echo.
echo 3. main.py 入口点：
type main.py | head -10
echo.
pause

echo.
echo ========================================
echo 步骤5：验证文件完整性
echo ========================================
echo.
echo 运行验证脚本：
python verify_deployment.py
echo.
if errorlevel 1 (
    echo ❌ 验证失败，请检查文件
) else (
    echo ✅ 验证成功，可以上传
)
echo.
pause

echo.
echo ========================================
echo 步骤6：上传后操作
echo ========================================
echo.
echo 1. 上传完成后，访问你的Render应用
echo 2. 点击 "Manual Deploy" → "Deploy latest commit"
echo 3. 等待5-10分钟部署完成
echo 4. 测试应用：
echo    - https://你的应用.onrender.com/health
echo    - https://你的应用.onrender.com/docs
echo.
echo ========================================
echo 重要提示：
echo 1. 确保上传所有必需文件
echo 2. 检查文件路径是否正确
echo 3. 部署可能需要几分钟
echo 4. 首次访问可能有延迟
echo ========================================
echo.
pause