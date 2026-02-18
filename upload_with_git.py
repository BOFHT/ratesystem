#!/usr/bin/env python
# upload_with_git.py - 使用Git命令上传修复文件
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """运行命令并返回结果"""
    print(f"执行: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode == 0:
            print(f"✅ 成功: {result.stdout[:200]}")
            return True, result.stdout
        else:
            print(f"❌ 失败: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"⚠️  错误: {e}")
        return False, str(e)

def clone_repository(repo_url, token, target_dir):
    """克隆仓库（使用Token认证）"""
    # 使用Token的认证URL
    auth_url = repo_url.replace('https://', f'https://{token}@')
    
    print(f"克隆仓库: {repo_url}")
    success, output = run_command(f'git clone {auth_url} "{target_dir}"')
    
    if success:
        print(f"✅ 仓库克隆到: {target_dir}")
        return True
    else:
        print(f"❌ 克隆失败")
        return False

def copy_fix_files(source_dir, target_dir):
    """复制修复文件到仓库目录"""
    print("复制修复文件...")
    
    # 要复制的文件列表
    essential_files = [
        # 根目录文件
        'Dockerfile',
        'requirements.txt',
        'main.py',
        'start.sh',
        'QUICK_DEPLOY.bat',
        'README_DEPLOY.md',
        'GITHUB_UPLOAD_GUIDE.md',
        'verify_deployment.py',
        'test_app.py',
        
        # Backend目录文件
        'backend/app_simple.py',
        'backend/database_sqlite.py',
        'backend/config_cloud.py',
        'backend/app_cloud.py',
    ]
    
    copied_count = 0
    for file_path in essential_files:
        source_path = os.path.join(source_dir, file_path)
        target_path = os.path.join(target_dir, file_path)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            print(f"  ✅ 复制: {file_path}")
            copied_count += 1
        else:
            print(f"  ❌ 缺失: {file_path}")
    
    print(f"总共复制: {copied_count}/{len(essential_files)} 个文件")
    return copied_count > 0

def commit_and_push(target_dir, commit_message):
    """提交并推送更改"""
    print("提交更改...")
    
    # 切换到仓库目录
    os.chdir(target_dir)
    
    # 添加所有文件
    success, _ = run_command('git add .')
    if not success:
        return False
    
    # 提交更改
    success, _ = run_command(f'git commit -m "{commit_message}"')
    if not success:
        return False
    
    # 推送到远程
    success, output = run_command('git push origin main')
    if success:
        print("✅ 更改已推送到GitHub")
        return True
    else:
        print("❌ 推送失败")
        return False

def verify_upload():
    """验证上传是否成功"""
    print("验证必需文件...")
    
    essential_files = [
        'backend/app_simple.py',
        'backend/database_sqlite.py',
        'Dockerfile',
        'requirements.txt',
        'main.py'
    ]
    
    all_exist = True
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("GitHub自动上传脚本")
    print("=" * 60)
    
    # 配置参数
    repo_url = "https://github.com/BOFHT/ratesystem.git"
    source_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(os.path.dirname(source_dir), "temp_ratesystem")
    
    # 获取GitHub Token
    token = input("请输入GitHub Token: ").strip()
    if not token:
        print("❌ 需要GitHub Token")
        return
    
    # 清理临时目录
    if os.path.exists(target_dir):
        print(f"清理现有目录: {target_dir}")
        shutil.rmtree(target_dir)
    
    # 步骤1：克隆仓库
    print("\n步骤1：克隆仓库")
    if not clone_repository(repo_url, token, target_dir):
        return
    
    # 步骤2：复制修复文件
    print("\n步骤2：复制修复文件")
    if not copy_fix_files(source_dir, target_dir):
        print("⚠️  有些文件可能缺失，但继续...")
    
    # 步骤3：验证文件
    print("\n步骤3：验证文件")
    os.chdir(target_dir)
    if not verify_upload():
        print("⚠️  必需文件可能不完整")
        continue_anyway = input("继续上传吗？(y/n): ").strip().lower()
        if continue_anyway != 'y':
            return
    
    # 步骤4：提交并推送
    print("\n步骤4：提交更改")
    commit_message = "修复部署问题：添加缺失模块和配置文件"
    if commit_and_push(target_dir, commit_message):
        print("\n🎉 上传完成！")
        print("\n下一步：")
        print("1. 访问 https://render.com")
        print("2. 找到你的应用")
        print("3. 点击 'Manual Deploy' → 'Deploy latest commit'")
        print("4. 等待5-10分钟部署完成")
    else:
        print("\n❌ 上传失败")
    
    # 清理临时目录
    print(f"\n清理临时目录: {target_dir}")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作取消")
    except Exception as e:
        print(f"错误: {e}")