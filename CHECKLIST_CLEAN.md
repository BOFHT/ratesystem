# 部署检查清单

## 必需的核心文件 ✅

### 1. 主入口文件
- `main.py` - 应用入口点
- `backend/app_simple.py` - 简化版FastAPI应用

### 2. 依赖配置
- `requirements.txt` - Python依赖包
- `Dockerfile` - Docker容器配置
- `render.yaml` - Render部署配置

### 3. 部署脚本
- `start.sh` - 启动脚本（Linux）
- `scripts/` - 初始化脚本

### 4. 文档和指南
- `README_DEPLOY.md` - 部署指南
- `GITHUB_UPLOAD_GUIDE.md` - GitHub上传指南
- `README.md` - 项目说明

## 验证步骤

### 1. 文件完整性检查
```bash
# 检查核心文件是否存在
ls -la main.py backend/app_simple.py requirements.txt Dockerfile render.yaml start.sh
```

### 2. 依赖验证
```bash
# 检查依赖是否有效
pip install -r requirements.txt --dry-run
```

### 3. 本地测试
```bash
# 本地运行测试
python verify_deployment.py
```

### 4. Docker构建测试
```bash
# 测试Docker构建
docker build -t project-rating-system .
```

## GitHub上传步骤

### 1. 初始化Git
```bash
git init
git add .
git commit -m "项目识别智能评分系统"
```

### 2. 连接到GitHub
```bash
git remote add origin https://github.com/你的用户名/ratesystem.git
git branch -M main
```

### 3. 推送代码
```bash
git push -u origin main
```

## Render部署步骤

### 1. 连接GitHub
- 访问 https://render.com
- 连接GitHub账号

### 2. 创建Web服务
- 选择"New Web Service"
- 选择GitHub仓库
- 使用自动检测配置

### 3. 部署设置
- 名称：project-rating-system
- 环境：Python
- 启动命令：python main.py

### 4. 等待部署完成
- 预计时间：3-5分钟
- 访问URL：https://project-rating-system.onrender.com

## 系统功能验证

### API端点测试：
1. `GET /` - 根目录
2. `GET /health` - 健康检查
3. `GET /docs` - API文档
4. `POST /api/analyze` - 项目分析
5. `GET /api/projects/{id}/rating` - 获取评分

### 测试数据：
```json
{
  "name": "测试项目",
  "description": "这是一个测试项目",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
}
```

## 注意事项

### 1. Render免费版限制
- 自动休眠（15分钟无访问）
- 内存限制（512MB）
- 磁盘限制（1GB）
- 首次访问较慢（冷启动）

### 2. GitHub配置
- 不要提交敏感信息
- 使用.gitignore忽略不需要的文件
- 定期更新依赖

### 3. 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload
```

## 故障排除

### 1. 部署失败
- 检查requirements.txt格式
- 验证Dockerfile语法
- 查看Render日志

### 2. 应用启动失败
- 检查端口设置（PORT环境变量）
- 验证依赖是否完整
- 查看错误日志

### 3. API访问失败
- 检查应用是否运行
- 验证CORS设置
- 检查网络连接

## 后续维护

### 1. 更新代码
```bash
git add .
git commit -m "更新描述"
git push
# Render会自动重新部署
```

### 2. 监控状态
- 访问Render Dashboard
- 查看应用日志
- 监控API响应时间

### 3. 扩展功能
- 添加数据库支持
- 实现用户认证
- 集成更多AI模型