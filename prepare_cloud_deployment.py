#!/usr/bin/env python3
# prepare_cloud_deployment.py - 云端部署准备脚本
import os
import shutil
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("=" * 60)
    print(text)
    print("=" * 60)

def check_prerequisites():
    """检查前提条件"""
    print_header("检查部署前提条件")
    
    requirements = [
        ("requirements.txt", "Python依赖文件"),
        ("backend/", "后端代码目录"),
        ("Dockerfile.render", "Docker配置文件"),
        ("render.yaml", "Render部署配置"),
        ("start_server.py", "启动脚本"),
    ]
    
    all_ok = True
    for file_path, description in requirements:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} - 缺失")
            all_ok = False
    
    return all_ok

def prepare_dockerfile():
    """准备Dockerfile"""
    print_header("准备Dockerfile")
    
    # 复制Dockerfile.render到Dockerfile
    dockerfile_render = Path("Dockerfile.render")
    dockerfile = Path("Dockerfile")
    
    if dockerfile_render.exists():
        shutil.copy2(dockerfile_render, dockerfile)
        print(f"✅ 复制 {dockerfile_render} -> {dockerfile}")
        
        # 读取并显示Dockerfile内容
        with open(dockerfile, 'r') as f:
            lines = f.readlines()
            print(f"📦 Dockerfile包含 {len(lines)} 行")
            
        return True
    else:
        print(f"❌ {dockerfile_render} 不存在")
        return False

def prepare_requirements():
    """准备requirements.txt"""
    print_header("检查requirements.txt")
    
    req_file = Path("requirements.txt")
    if req_file.exists():
        with open(req_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"📦 检测到 {len(packages)} 个Python包:")
        for i, package in enumerate(packages[:10], 1):  # 显示前10个
            print(f"  {i}. {package}")
        
        if len(packages) > 10:
            print(f"  ... 还有 {len(packages)-10} 个包")
        
        return True
    else:
        print(f"❌ {req_file} 不存在")
        return False

def create_cloud_readme():
    """创建云端部署README"""
    print_header("创建部署文档")
    
    readme_content = """# 项目评分系统 - 云端部署指南

## 🚀 一键部署到Render

本项目已配置好所有文件，可以直接部署到Render免费平台。

### 部署步骤

1. **注册Render账户**
   - 访问 https://render.com
   - 使用GitHub或邮箱注册
   - 完成邮箱验证

2. **准备GitHub仓库**
   - 将此项目推送到GitHub仓库
   - 确保包含所有文件

3. **在Render部署**
   - 登录Render控制台
   - 点击 "New +" → "Web Service"
   - 连接你的GitHub仓库
   - 选择 "project-rating-system" 仓库
   - 保持默认配置，点击 "Create Web Service"

4. **等待部署完成**
   - 首次部署需要5-10分钟
   - 自动配置HTTPS证书
   - 获取免费域名: `project-rating-system.onrender.com`

### 访问地址

部署成功后，可以访问：

- 🌐 **主应用**: https://project-rating-system.onrender.com
- 📚 **API文档**: https://project-rating-system.onrender.com/docs
- 💪 **健康检查**: https://project-rating-system.onrender.com/health

### API使用示例

#### 创建项目
```bash
curl -X POST https://project-rating-system.onrender.com/projects/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "我的测试项目",
    "description": "这是一个测试项目",
    "code_language": "Python",
    "has_documentation": true,
    "has_tests": true
  }'
```

#### 项目评分
```bash
curl -X POST https://project-rating-system.onrender.com/analyze/score \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": 1,
    "algorithm": "advanced"
  }'
```

#### 获取项目列表
```bash
curl https://project-rating-system.onrender.com/projects/
```

### 免费计划限制

Render免费计划提供：
- ✅ 750小时/月（约31天连续运行）
- ✅ 512MB RAM
- ✅ 共享CPU
- ✅ 免费HTTPS
- ✅ 自动部署
- ❌ 15分钟无流量后休眠

### 保持应用活跃

防止应用休眠：
1. 定期访问应用
2. 使用监控服务（如UptimeRobot）
3. 设置定时任务访问健康检查

### 项目结构

```
project-rating-system/
├── Dockerfile          # 容器配置
├── render.yaml         # Render部署配置
├── requirements.txt    # Python依赖
├── start_server.py     # 启动脚本
├── backend/           # 后端代码
│   ├── app_cloud.py   # 主应用
│   └── database_sqlite.py # SQLite数据库
└── data/              # 数据存储目录
```

### 技术支持

如有问题：
1. 查看Render部署日志
2. 检查应用健康状态
3. 访问API文档测试接口

### 更新部署

推送代码到GitHub后，Render会自动重新部署。

---
🎉 **祝您部署顺利！**
"""
    
    readme_path = Path("README_CLOUD_DEPLOYMENT.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 创建云端部署指南: {readme_path}")
    print(f"📖 文件大小: {readme_path.stat().st_size:,} 字节")
    
    return True

def create_deployment_checklist():
    """创建部署检查清单"""
    print_header("部署检查清单")
    
    checklist = """# 部署检查清单

## 部署前检查
- [ ] GitHub仓库已准备好
- [ ] 所有必需文件已提交
- [ ] Render账户已注册验证

## 文件检查
- [ ] Dockerfile (从Dockerfile.render复制)
- [ ] render.yaml (部署配置)
- [ ] requirements.txt (Python依赖)
- [ ] backend/ 目录完整
- [ ] start_server.py 存在

## 部署步骤
- [ ] 登录Render控制台
- [ ] 创建新的Web Service
- [ ] 连接GitHub仓库
- [ ] 选择免费计划 (Free)
- [ ] 确认自动部署设置
- [ ] 点击创建并等待部署

## 部署后验证
- [ ] 访问健康检查: /health
- [ ] 访问API文档: /docs
- [ ] 测试创建项目
- [ ] 测试项目评分
- [ ] 验证HTTPS工作正常

## 维护任务
- [ ] 设置监控服务
- [ ] 定期备份数据
- [ ] 查看部署日志
- [ ] 更新依赖包

## 故障排除
- [ ] 检查Render部署日志
- [ ] 验证数据库连接
- [ ] 检查端口配置
- [ ] 验证环境变量
"""
    
    checklist_path = Path("DEPLOYMENT_CHECKLIST.md")
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print(f"✅ 创建部署检查清单: {checklist_path}")
    
    return True

def create_github_workflow():
    """创建GitHub Actions工作流"""
    print_header("创建GitHub Actions工作流（可选）")
    
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = """name: Deploy to Render

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Render
      run: |
        echo "项目已推送到GitHub，Render将自动部署"
        echo "访问 https://dashboard.render.com 查看部署状态"
        
    - name: Send deployment notification
      run: |
        echo "部署流程完成"
        echo "应用将在几分钟内上线"
"""
    
    workflow_path = workflow_dir / "deploy.yml"
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    
    print(f"✅ 创建GitHub Actions工作流: {workflow_path}")
    
    return True

def main():
    """主函数"""
    print_header("项目评分系统 - 云端部署准备")
    
    print("🏗️  开始准备云端部署...")
    print()
    
    # 检查前提条件
    if not check_prerequisites():
        print("❌ 前提条件检查失败，请修复缺失的文件")
        return False
    
    print()
    
    # 准备部署文件
    steps = [
        ("准备Dockerfile", prepare_dockerfile),
        ("检查依赖文件", prepare_requirements),
        ("创建部署文档", create_cloud_readme),
        ("创建检查清单", create_deployment_checklist),
        ("创建工作流", create_github_workflow),
    ]
    
    all_success = True
    for step_name, step_func in steps:
        print(f"正在执行: {step_name}...")
        if not step_func():
            print(f"❌ {step_name} 失败")
            all_success = False
        print()
    
    if all_success:
        print_header("✅ 云端部署准备完成！")
        
        print("下一步操作:")
        print("1. 将项目推送到GitHub仓库")
        print("2. 访问 https://render.com 注册账户")
        print("3. 创建新的Web Service")
        print("4. 连接GitHub仓库并部署")
        print()
        print("📚 详细步骤请参考: README_CLOUD_DEPLOYMENT.md")
        print("📋 检查清单: DEPLOYMENT_CHECKLIST.md")
        print()
        print("🎉 准备好免费上线您的项目评分系统了！")
    else:
        print_header("⚠️  部署准备遇到问题")
        print("请检查以上错误信息并修复后重试")
    
    return all_success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 准备过程出错: {e}")
        exit(1)