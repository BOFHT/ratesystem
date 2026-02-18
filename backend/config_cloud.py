# backend/config_cloud.py - 云端部署配置
import os
from typing import List, Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基础设置
    APP_NAME: str = "项目识别智能评分系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于AI的项目识别与智能评分系统"
    
    # API设置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Project Rating System"
    
    # 服务器设置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False  # 生产环境关闭热重载
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 数据库设置
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'projects.db')}")
    
    # ML模型设置（云端简化版）
    ML_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "ml_models", "models")
    USE_SIMPLE_ALGORITHM: bool = True  # 云端使用简化算法
    
    # 日志设置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = os.path.join(os.path.dirname(__file__), "logs", "app.log")
    
    # 安全设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 全局设置实例
settings = Settings()

# 导出常量
API_PREFIX = settings.API_V1_STR
PROJECT_NAME = settings.PROJECT_NAME
VERSION = settings.APP_VERSION

# CORS配置
ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://project-rating-system.onrender.com",
    "https://*.onrender.com",
]

# 数据库表名常量
PROJECTS_TABLE = "projects"
PROJECT_ANALYSIS_TABLE = "project_analysis"
SCORING_LOGS_TABLE = "scoring_logs"

# 算法类型常量
ALGORITHM_BASE = "base"
ALGORITHM_ADVANCED = "advanced"
ALGORITHM_ML = "ml"
ALGORITHM_SIMPLE = "simple"  # 云端简化算法

# 项目分类常量
PROJECT_CATEGORIES = [
    "web应用",
    "移动应用",
    "数据分析",
    "机器学习",
    "区块链",
    "物联网",
    "桌面应用",
    "游戏",
    "工具库",
    "其他"
]

# 技术栈常量
TECH_STACKS = {
    "web": ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust"],
    "frontend": ["React", "Vue", "Angular", "Svelte", "Next.js"],
    "backend": ["Django", "Flask", "FastAPI", "Spring", "Express", "NestJS"],
    "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"],
    "cloud": ["AWS", "Azure", "GCP", "阿里云", "腾讯云"],
    "devops": ["Docker", "Kubernetes", "GitHub Actions", "Jenkins", "GitLab CI"]
}

# 评分权重常量（云端简化版）
SCORING_WEIGHTS = {
    "documentation": 0.15,
    "tests": 0.20,
    "ci_cd": 0.15,
    "team_size": 0.10,
    "complexity": 0.15,
    "tech_stack": 0.25
}

# 项目复杂度映射
COMPLEXITY_MAPPING = {
    "低": 1,
    "中等": 2,
    "高": 3,
    "非常高": 4
}

# 导出配置函数
def get_settings() -> Settings:
    """获取设置实例"""
    return settings

def get_database_url() -> str:
    """获取数据库URL"""
    return settings.DATABASE_URL

def get_cors_origins() -> List[str]:
    """获取CORS允许的来源"""
    return settings.BACKEND_CORS_ORIGINS + ORIGINS

def get_algorithm_types() -> List[str]:
    """获取支持的算法类型"""
    return [ALGORITHM_BASE, ALGORITHM_ADVANCED, ALGORITHM_ML, ALGORITHM_SIMPLE]