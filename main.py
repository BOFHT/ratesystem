# main.py - 应用的入口点（用于Render部署）
import os
import sys

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

if __name__ == "__main__":
    try:
        # 导入并启动应用
        from backend.app_simple import app
        import uvicorn
        
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        print("=" * 60)
        print("项目识别智能评分系统 v1.0.0")
        print("=" * 60)
        print(f"服务器地址: http://{host}:{port}")
        print(f"API文档: http://{host}:{port}/docs")
        print(f"健康检查: http://{host}:{port}/health")
        print(f"演示数据: http://{host}:{port}/api/demo")
        print("=" * 60)
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已经安装了所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动错误: {e}")
        sys.exit(1)