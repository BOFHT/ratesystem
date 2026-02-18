#!/usr/bin/env python
# verify_deployment.py - 验证部署文件完整性
import os
import sys

def check_file_exists(filepath, description=""):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath} {description}")
    return exists

def main():
    print("=" * 60)
    print("部署文件完整性检查")
    print("=" * 60)
    
    # 必需文件列表
    required_files = [
        ("Dockerfile", "Docker配置文件"),
        ("requirements.txt", "Python依赖文件"),
        ("main.py", "应用入口点"),
        ("start.sh", "启动脚本"),
        ("backend/app_simple.py", "简化版应用"),
        ("backend/config_cloud.py", "云端配置"),
        ("backend/database_sqlite.py", "SQLite数据库"),
        ("README_DEPLOY.md", "部署指南")
    ]
    
    # 可选文件列表
    optional_files = [
        ("render.yaml", "Render配置"),
        (".gitignore", "Git忽略文件"),
        ("config.py", "原始配置"),
        ("backend/app.py", "原始应用"),
        ("backend/app_cloud.py", "完整云端应用")
    ]
    
    print("\n必需文件检查:")
    print("-" * 40)
    
    all_required_exist = True
    for filename, description in required_files:
        if not check_file_exists(filename, description):
            all_required_exist = False
    
    print("\n可选文件检查:")
    print("-" * 40)
    
    for filename, description in optional_files:
        check_file_exists(filename, description)
    
    print("\n" + "=" * 60)
    print("检查结果:")
    print("=" * 60)
    
    if all_required_exist:
        print("🎉 所有必需文件都存在！可以部署到Render。")
        print("\n部署步骤:")
        print("1. 将本文件夹上传到GitHub仓库")
        print("2. 登录Render.com")
        print("3. 创建新的Web Service")
        print("4. 连接你的GitHub仓库")
        print("5. 配置部署选项")
        print("6. 点击'Create Web Service'")
        print("\n部署完成后访问:")
        print("- 应用根目录: https://your-app-name.onrender.com/")
        print("- API文档: https://your-app-name.onrender.com/docs")
        print("- 健康检查: https://your-app-name.onrender.com/health")
        print("- 演示数据: https://your-app-name.onrender.com/api/demo")
    else:
        print("⚠️  缺少必需文件，请先创建缺失的文件再部署。")
    
    print("\n文件结构:")
    print("upload_to_github/")
    for filename, _ in required_files:
        if "/" in filename:
            dir_name, file_name = filename.split("/")
            print(f"  ├── {dir_name}/")
            print(f"  │   └── {file_name}")
        else:
            print(f"  ├── {filename}")
    
    return all_required_exist

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)