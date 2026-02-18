# 快速开始指南

## 项目识别智能评分系统

### 系统要求
- Python 3.8+
- PostgreSQL 14+
- MongoDB 5+
- Redis 6+
- Docker (可选，用于容器化部署)

### 快速启动方式

#### 方式1: 使用Docker Compose (推荐)
```bash
# 克隆或进入项目目录
cd project_rating_system

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

服务启动后访问:
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 前端界面: http://localhost:3000 (需要前端构建)
- 数据库管理: http://localhost:5050 (pgAdmin)
- 监控面板: http://localhost:3001 (Grafana)

#### 方式2: 手动启动
```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 启动数据库服务(确保PostgreSQL、MongoDB、Redis已安装并运行)

# 3. 初始化数据库
python -m scripts.init_database

# 4. 启动后端服务
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

#### 方式3: Windows环境
双击运行 `start_development.bat` 脚本

### API快速测试

#### 1. 创建新项目
```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "智能电商系统",
    "description": "基于AI的个性化推荐电商平台",
    "category": "web_development",
    "tech_stack": ["python", "django", "react", "postgresql", "redis"]
  }'
```

#### 2. 获取项目列表
```bash
curl "http://localhost:8000/api/v1/projects/"
```

#### 3. 分析项目
```bash
curl -X POST "http://localhost:8000/api/v1/projects/1/analyze"
```

#### 4. 获取项目详情
```bash
curl "http://localhost:8000/api/v1/projects/1"
```

### 配置说明

#### 环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置数据库连接等信息
```

#### 配置文件
- `config.py`: 主要配置文件
- `requirements.txt`: Python依赖
- `docker-compose.yml`: Docker编排配置

### 开发指南

#### 项目结构
```
project_rating_system/
├── backend/          # 后端代码
│   ├── routers/      # API路由
│   ├── schemas.py    # 数据模型
│   ├── database.py   # 数据库
│   ├── middleware.py # 中间件
│   └── app.py        # 主应用
├── frontend/         # 前端代码(待开发)
├── models/           # 机器学习模型
├── scripts/          # 工具脚本
├── docs/             # 文档
└── tests/            # 测试代码(待添加)
```

#### 添加新功能
1. 在 `schemas.py` 中定义数据模型
2. 在 `backend/routers/` 中创建新的路由文件
3. 在 `app.py` 中注册路由
4. 添加相关业务逻辑

### 故障排除

#### 常见问题
1. **数据库连接失败**
   - 检查PostgreSQL、MongoDB、Redis是否运行
   - 验证连接字符串配置
   - 检查防火墙设置

2. **依赖安装失败**
   - 使用Python虚拟环境
   - 更新pip: `pip install --upgrade pip`
   - 使用国内镜像源

3. **Docker启动失败**
   - 检查Docker服务状态
   - 检查端口是否被占用
   - 清理Docker缓存: `docker system prune`

4. **API访问错误**
   - 检查后端服务是否运行
   - 查看应用日志: `logs/app.log`
   - 验证请求数据格式

#### 日志查看
```bash
# Docker环境
docker-compose logs -f backend

# 本地环境
tail -f logs/app.log
```

### 下一步开发

#### 阶段2: 项目识别模块
```bash
# 开发机器学习模型
cd models/

# 训练分类器
python train_classifier.py

# 测试识别功能
python test_recognition.py
```

#### 阶段3: 评分算法
- 质量评分算法
- 创新性评估模型
- 可行性分析模块
- 商业价值计算

#### 阶段4: 前端界面
- React/Vue.js应用
- 数据可视化图表
- 项目管理界面

### 贡献指南
1. Fork项目仓库
2. 创建特性分支
3. 提交代码变更
4. 创建Pull Request
5. 通过代码审查

### 技术支持
- API文档: http://localhost:8000/docs
- 错误报告: 创建Issue
- 功能建议: 提交Pull Request

---

**注意**: 此为开发版本，生产部署需要额外的安全配置和优化。