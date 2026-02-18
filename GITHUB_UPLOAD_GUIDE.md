# GitHub上传指南

## 方法一：使用GitHub网页界面（最简单）

### 步骤1：创建GitHub仓库
1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `project-rating-system`
   - **Description**: `AI项目识别与智能评分系统`
   - 选择 **Public** (公开)
   - 不要勾选 "Add README" (我们已经有)
   - 点击 "Create repository"

### 步骤2：上传文件
1. 创建仓库后，你会看到上传文件的选项
2. 点击 "uploading an existing file"
3. 将 `upload_to_github` 文件夹中的所有文件和文件夹拖拽到上传区域
4. 填写提交信息: `初始提交: 项目识别智能评分系统`
5. 点击 "Commit changes"

## 方法二：使用Git命令行（推荐）

### 准备工作
1. 安装Git: https://git-scm.com/downloads
2. 配置Git:
   ```bash
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱"
   ```

### 上传步骤
```bash
# 1. 进入项目文件夹
cd C:\Users\ASUS\.openclaw\workspace\upload_to_github

# 2. 初始化Git仓库
git init

# 3. 添加所有文件
git add .

# 4. 提交更改
git commit -m "初始提交: 项目识别智能评分系统"

# 5. 连接到GitHub仓库
git remote add origin https://github.com/你的用户名/project-rating-system.git

# 6. 推送到GitHub
git push -u origin main
```

## 方法三：使用GitHub Desktop

1. 下载安装 GitHub Desktop: https://desktop.github.com/
2. 登录你的GitHub账号
3. 点击 "File" → "Add local repository"
4. 选择 `C:\Users\ASUS\.openclaw\workspace\upload_to_github` 文件夹
5. 填写提交信息
6. 点击 "Publish repository"

## 验证上传

上传完成后，访问你的GitHub仓库：
```
https://github.com/你的用户名/project-rating-system
```

你应该能看到以下文件：
- `Dockerfile`
- `requirements.txt`
- `main.py`
- `backend/` 文件夹
- `README_DEPLOY.md`

## 下一步：Render部署

GitHub仓库创建后，按以下步骤在Render部署：

1. 访问 https://render.com
2. 点击 "New +" → "Web Service"
3. 点击 "Connect GitHub"
4. 授权Render访问你的GitHub账号
5. 选择 `project-rating-system` 仓库
6. 配置部署选项：
   - **Name**: `project-rating-system`
   - **Environment**: `Docker`
   - **Region**: 选择最近的（如 `Singapore`）
   - **Branch**: `main`
7. 点击 "Create Web Service"

## 常见问题

### Q1: 文件太大无法上传？
A: 确保没有上传 `.gitignore` 中忽略的文件，如 `__pycache__/`, `.env`, 大文件等。

### Q2: 权限错误？
A: 确保你有GitHub仓库的写入权限。

### Q3: Dockerfile不工作？
A: 检查文件路径，确保所有文件都在正确位置。

### Q4: 如何更新代码？
A: 修改代码后，重新提交并推送到GitHub：
```bash
git add .
git commit -m "更新描述"
git push
```

## 快速检查清单

✅ 已完成:
- [ ] 创建GitHub仓库
- [ ] 上传所有文件
- [ ] 验证文件结构
- [ ] 准备Render部署

📋 部署前确认:
- [ ] `Dockerfile` 存在且正确
- [ ] `requirements.txt` 包含所有依赖
- [ ] `main.py` 可以正常导入
- [ ] 没有语法错误
- [ ] 文件大小合适（不超过100MB）

🚀 部署后验证:
- [ ] 访问根URL返回成功
- [ ] `/health` 端点正常工作
- [ ] `/docs` 可以访问API文档
- [ ] `/api/demo` 创建演示数据

## 技术支持

如果遇到问题：
1. 检查GitHub仓库是否包含所有必需文件
2. 查看Render的构建日志
3. 确保Python版本兼容（3.9+）
4. 验证环境变量设置

## 备用方案

如果Render部署失败，还可以考虑：
1. **Railway.app** - 类似Render的部署平台
2. **PythonAnywhere** - 专门用于Python应用的托管
3. **Heroku** - 经典部署平台（需要信用卡验证）
4. **Vercel** - 适合前端，但也可以部署Python

---

**提示**: 最简单的路径是使用GitHub网页界面上传，然后在Render连接GitHub仓库自动部署。