# 项目识别智能评分系统 - 部署指南

## 系统概述
这是一个基于AI的项目识别与智能评分系统，提供以下功能：
- 项目信息管理
- AI智能分析与识别
- 多算法评分系统
- RESTful API接口

## 部署到Render.com

### 准备工作
1. 将本文件夹 (`upload_to_github/`) 上传到GitHub仓库
2. 注册Render.com账号（免费）

### 部署步骤

#### 方法1：使用Docker部署（推荐）
1. 登录Render.com
2. 点击"New +" → "Web Service"
3. 连接你的GitHub仓库
4. 配置部署选项：
   - **Name**: `project-rating-system`
   - **Environment**: `Docker`
   - **Region**: 选择离你最近的地区
   - **Branch**: `main` 或你的分支
   - **Root Directory**: 留空（或设置为仓库根目录）
5. 点击"Create Web Service"
6. Render会自动使用 `Dockerfile` 构建和部署

#### 方法2：使用Python直接部署
1. 登录Render.com
2. 点击"New +" → "Web Service"
3. 连接你的GitHub仓库
4. 配置部署选项：
   - **Name**: `project-rating-system`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Python Version**: `3.9`
5. 点击"Create Web Service"

### 环境变量配置
在Render控制台的"Environment"标签页添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | `8000` | 应用端口 |
| `HOST` | `0.0.0.0` | 监听地址 |
| `DATABASE_URL` | `sqlite:///backend/database/projects.db` | 数据库URL |

### 部署文件说明

#### 必需文件
- `Dockerfile` - Docker配置
- `requirements.txt` - Python依赖包
- `main.py` - 应用入口点
- `backend/app_simple.py` - 简化版FastAPI应用
- `backend/config_cloud.py` - 云端配置
- `backend/database_sqlite.py` - SQLite数据库模块

#### 可选文件
- `start.sh` - 启动脚本（Linux/Mac）
- `render.yaml` - Render配置文件（可选）

## 验证部署

### 1. 部署成功后
Render会提供一个URL，例如：`https://project-rating-system.onrender.com`

### 2. 访问API端点

#### 根目录
```
GET https://project-rating-system.onrender.com/
```

#### 健康检查
```
GET https://project-rating-system.onrender.com/health
```

#### API文档
```
GET https://project-rating-system.onrender.com/docs
```

#### 创建演示数据
```
GET https://project-rating-system.onrender.com/api/demo
```

#### 创建项目
```
POST https://project-rating-system.onrender.com/api/projects
Content-Type: application/json

{
  "name": "我的测试项目",
  "description": "这是一个测试项目",
  "repo_url": "https://github.com/example/test",
  "tags": ["Python", "AI"]
}
```

#### 分析并评分项目
```
POST https://project-rating-system.onrender.com/api/analyze/score
Content-Type: application/json

{
  "project_data": {
    "name": "AI助手项目",
    "has_documentation": true,
    "has_tests": true,
    "has_ci_cd": false,
    "team_size": 3,
    "estimated_complexity": "中等"
  }
}
```

#### 获取项目评分
```
GET https://project-rating-system.onrender.com/api/projects/{project_id}/rating
```

## 故障排除

### 常见问题

#### 1. 构建失败：找不到模块
**问题**: `ModuleNotFoundError: No module named 'xxx'`
**解决**: 确保 `requirements.txt` 包含所有必需的包

#### 2. 应用启动失败
**问题**: `Failed to start application`
**解决**: 检查 `main.py` 或 `app_simple.py` 是否有语法错误

#### 3. 数据库连接问题
**问题**: `Database connection failed`
**解决**: 确保有写入权限，SQLite数据库文件可以正常创建

#### 4. Render免费层级限制
**注意**: Render免费服务有以下限制：
- 应用在闲置时会休眠（约15分钟无流量）
- 重启需要30-60秒
- 每月有免费小时数限制
- 网络带宽有限

### 调试步骤
1. 在Render控制台查看"Logs"标签页
2. 检查构建日志是否有错误
3. 验证环境变量是否正确设置
4. 使用curl或Postman测试API端点

## 本地开发

### 运行本地服务器
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
# 或
cd backend
python app_simple.py
```

### 访问本地应用
- 应用: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 系统架构

### 简化版架构（云端部署）
```
客户端 → Render服务器 → FastAPI应用 → SQLite数据库
```

### 核心模块
1. **app_simple.py** - 主应用，包含所有API端点
2. **SimpleScoringAlgorithm** - 简化评分算法
3. **内存数据库** - 用于演示的简单数据存储
4. **SQLite支持** - 可选持久化存储

### API端点
- `GET /` - 根目录
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /api/demo` - 创建演示数据
- `GET /api/projects` - 获取所有项目
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取特定项目
- `POST /api/analyze/score` - 分析并评分项目
- `GET /api/projects/{id}/rating` - 获取项目评分

## 性能优化建议

### 针对Render免费层
1. 启用缓存
2. 优化数据库查询
3. 减少启动时间
4. 实现健康检查保活

### 扩展建议
1. 添加Redis缓存
2. 使用PostgreSQL替代SQLite
3. 实现API限流
4. 添加监控和日志

## 联系支持
如有部署问题，请检查：
1. Render文档：https://render.com/docs
2. FastAPI文档：https://fastapi.tiangolo.com
3. 本项目GitHub仓库

---
**部署状态**: ✅ 已准备好部署  
**最后更新**: 2026-02-18  
**系统版本**: v1.0.0