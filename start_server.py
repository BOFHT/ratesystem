#!/usr/bin/env python3
# start_server.py - Render平台启动脚本
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_environment():
    """检查环境配置"""
    print("🔍 环境检查...")
    
    # 检查必要目录
    required_dirs = ["backend", "data"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"⚠️  创建目录: {dir_name}")
            dir_path.mkdir(exist_ok=True)
    
    # 检查数据目录权限
    data_dir = project_root / "data"
    if data_dir.exists():
        print(f"✅ 数据目录: {data_dir}")
    
    # 显示环境变量
    env_vars = {
        "PORT": os.getenv("PORT", "8000"),
        "DEBUG": os.getenv("DEBUG", "False"),
        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///./data/projects.db")
    }
    
    print("📋 环境变量:")
    for key, value in env_vars.items():
        print(f"   {key}: {value}")

def create_sqlite_db():
    """创建SQLite数据库（如果不存在）"""
    try:
        from backend.database_sqlite import Base, engine
        print("🗄️  初始化数据库...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库表创建完成")
        
        # 插入测试数据（可选）
        if os.getenv("DEBUG", "False").lower() == "true":
            insert_test_data()
            
    except Exception as e:
        print(f"⚠️  数据库初始化警告: {e}")
        # 继续启动，可能数据库已存在

def insert_test_data():
    """插入测试数据（仅开发环境）"""
    try:
        from backend.database_sqlite import SessionLocal
        from backend import models
        
        db = SessionLocal()
        
        # 检查是否已有数据
        existing = db.query(models.Project).first()
        if existing:
            print("📊 数据库中已有数据，跳过测试数据插入")
            db.close()
            return
        
        # 创建测试项目
        test_project = models.Project(
            name="OpenClaw智能助手",
            description="基于OpenClaw的AI个人助手系统",
            code_language="Python",
            framework="FastAPI",
            git_url="https://github.com/openclaw/openclaw",
            estimated_complexity="中等"
        )
        
        db.add(test_project)
        db.commit()
        
        print("✅ 测试项目已插入")
        db.close()
        
    except Exception as e:
        print(f"⚠️  测试数据插入失败: {e}")

def main():
    """主启动函数"""
    print("=" * 60)
    print("项目评分系统 - 云端部署版")
    print("=" * 60)
    
    # 环境检查
    check_environment()
    
    # 数据库初始化
    create_sqlite_db()
    
    # 导入并启动FastAPI应用
    try:
        from backend.app_cloud import app
        
        # 获取端口（Render使用环境变量PORT）
        port = int(os.getenv("PORT", 8000))
        
        print(f"🌐 启动Web服务...")
        print(f"📍 监听地址: 0.0.0.0:{port}")
        print(f"🔗 外部访问: https://your-app.onrender.com")
        print(f"📚 API文档: /docs")
        print(f"💪 健康检查: /health")
        print("=" * 60)
        
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,  # 生产环境关闭热重载
            access_log=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 无法导入应用模块: {e}")
        print("请检查backend/app.py文件是否存在")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()