# config_cloud.py - 云端部署配置
import os
from pathlib import Path

class CloudSettings:
    """云端部署配置"""
    
    # 应用配置
    APP_NAME = "项目评分系统 - 云端版"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    VERSION = "1.0.0-cloud"
    
    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/projects.db")
    
    # 文件存储配置
    DATA_DIR = Path("./data")
    LOGS_DIR = Path("./logs")
    
    # API配置
    API_PREFIX = "/api"
    DOCS_URL = "/docs" if DEBUG else None
    REDOC_URL = "/redoc" if DEBUG else None
    
    # CORS配置
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://project-rating-system.onrender.com",
        "https://*.onrender.com",
        "*"  # 开发环境允许所有
    ]
    
    # 安全配置
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    
    # 性能配置
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT = 30  # 秒
    
    # 功能开关
    FEATURES = {
        "ml_analysis": True,
        "scoring": True,
        "batch_processing": True,
        "export_reports": True,
    }
    
    def __init__(self):
        """初始化配置"""
        # 确保目录存在
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
        
        # 打印配置信息（仅调试模式）
        if self.DEBUG:
            print(f"🔧 云端配置加载完成:")
            print(f"   应用名称: {self.APP_NAME}")
            print(f"   数据库: {self.DATABASE_URL}")
            print(f"   数据目录: {self.DATA_DIR.absolute()}")
            print(f"   调试模式: {self.DEBUG}")

# 创建配置实例
settings = CloudSettings()

# 导出配置
__all__ = ["settings"]