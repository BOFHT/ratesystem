#!/usr/bin/env python3
# deploy_prepare.py - 纯ASCII部署准备脚本

import os
import shutil
from pathlib import Path

def check_files():
    """检查必需文件"""
    print("=" * 60)
    print("项目评分系统 - 云端部署文件检查")
    print("=" * 60)
    
    required_files = [
        ("requirements.txt", "Python依赖文件"),
        ("backend/", "后端代码目录"),
        ("Dockerfile.render", "Docker配置模板"),
        ("render.yaml", "Render部署配置"),
        ("start_server.py", "启动脚本"),
        ("backend/app_cloud.py", "云端API应用"),
        ("backend/database_sqlite.py", "SQLite数据库"),
        ("config_cloud.py", "云端配置"),
    ]
    
    all_ok = True
    for file_path, description in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[OK] {description}: {file_path}")
        else:
            print(f"[FAIL] {description}: {file_path} - 缺失")
            all_ok = False
    
    return all_ok

def prepare_deployment():
    """准备部署文件"""
    print()
    print("=" * 60)
    print("准备部署文件")
    print("=" * 60)
    
    # 1. 复制Dockerfile
    if Path("Dockerfile.render").exists():
        shutil.copy2("Dockerfile.render", "Dockerfile")
        print("[OK] 创建 Dockerfile")
    else:
        print("[FAIL] Dockerfile.render 不存在")
        return False
    
    # 2. 检查requirements.txt
    if Path("requirements.txt").exists():
        with open("requirements.txt", 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"[OK] requirements.txt 包含 {len(packages)} 个包")
    else:
        print("[FAIL] requirements.txt 不存在")
        return False
    
    # 3. 创建部署说明
    deploy_guide = """# 部署说明

## 1. 将代码推送到GitHub
git init
git add .
git commit -m "初始提交"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main

## 2. 在Render部署
1. 访问 https://render.com
2. 注册账户（推荐GitHub登录）
3. 点击 New + -> Web Service
4. 连接GitHub仓库
5. 选择项目仓库
6. 点击 Create Web Service

## 3. 等待部署完成
- 首次部署: 5-10分钟
- 访问地址: https://YOUR_APP.onrender.com
- API文档: /docs
- 健康检查: /health

## 4. 测试API
创建项目:
curl -X POST https://YOUR_APP.onrender.com/projects/ \\
  -H "Content-Type: application/json" \\
  -d '{"name":"测试项目","code_language":"Python"}'

项目评分:
curl -X POST https://YOUR_APP.onrender.com/analyze/score \\
  -H "Content-Type: application/json" \\
  -d '{"project_id":1,"algorithm":"advanced"}'
"""
    
    with open("DEPLOY_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(deploy_guide)
    print("[OK] 创建部署指南: DEPLOY_GUIDE.md")
    
    # 4. 创建快速测试脚本
    test_script = """#!/usr/bin/env python3
# quick_test.py - 快速测试脚本
import requests
import json

def test_api():
    # 请替换为您的实际URL
    base_url = "https://YOUR_APP.onrender.com"
    
    print("测试项目评分系统API...")
    
    try:
        # 1. 健康检查
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"健康检查: {response.status_code} - {response.json()}")
        
        # 2. 创建项目
        project_data = {
            "name": "测试项目-" + str(hash("test")),
            "description": "API测试项目",
            "code_language": "Python",
            "has_documentation": True,
            "has_tests": True
        }
        
        response = requests.post(
            f"{base_url}/projects/",
            json=project_data,
            timeout=10
        )
        
        if response.status_code == 200:
            project = response.json()
            project_id = project['id']
            print(f"项目创建成功: ID={project_id}")
            
            # 3. 项目评分
            score_data = {
                "project_id": project_id,
                "algorithm": "advanced"
            }
            
            response = requests.post(
                f"{base_url}/analyze/score",
                json=score_data,
                timeout=10
            )
            
            if response.status_code == 200:
                score_result = response.json()
                print(f"评分成功: {score_result['final_score']}/100")
                print("测试完成!")
            else:
                print(f"评分失败: {response.status_code}")
        else:
            print(f"项目创建失败: {response.status_code}")
            
    except Exception as e:
        print(f"测试出错: {e}")

if __name__ == "__main__":
    test_api()
"""
    
    with open("quick_test.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    print("[OK] 创建快速测试脚本: quick_test.py")
    
    return True

def create_file_list():
    """创建文件清单"""
    print()
    print("=" * 60)
    print("项目文件清单")
    print("=" * 60)
    
    files_to_deploy = [
        "Dockerfile",
        "render.yaml",
        "requirements.txt",
        "start_server.py",
        "config_cloud.py",
        "backend/app_cloud.py",
        "backend/database_sqlite.py",
        "backend/__init__.py",
        "data/",
        "DEPLOY_GUIDE.md",
        "quick_test.py"
    ]
    
    total_size = 0
    for file_path in files_to_deploy:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                total_size += size
                print(f"{file_path:30s} {size:8,} 字节")
            else:
                print(f"{file_path:30s} [目录]")
        else:
            print(f"{file_path:30s} [警告: 不存在]")
    
    print("-" * 60)
    print(f"总计文件大小: {total_size:,} 字节 ({total_size/1024:.1f} KB)")
    print()
    print("部署大小: 非常适合免费平台!")
    
    return True

def main():
    """主函数"""
    print("开始准备云端部署...")
    print()
    
    # 检查文件
    if not check_files():
        print()
        print("错误: 必需文件缺失，请检查项目结构")
        return False
    
    # 准备部署
    if not prepare_deployment():
        print()
        print("错误: 部署文件准备失败")
        return False
    
    # 创建文件清单
    create_file_list()
    
    print()
    print("=" * 60)
    print("部署准备完成!")
    print("=" * 60)
    
    print()
    print("下一步操作:")
    print("1. 将以上文件推送到GitHub")
    print("2. 访问 https://render.com 注册")
    print("3. 创建Web Service并连接GitHub")
    print("4. 等待部署完成")
    print("5. 访问您的免费网址!")
    print()
    print("详细步骤请参考: DEPLOY_GUIDE.md")
    print()
    print("祝您部署顺利!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"部署准备出错: {e}")
        exit(1)