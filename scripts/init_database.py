"""
数据库初始化脚本
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, ProjectCategory, TechStackDefinition
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """创建数据库表"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建成功")
            
            # 创建索引（如果不存在）
            await create_indexes(conn)
            
    except Exception as e:
        logger.error(f"创建表失败: {e}")
        raise


async def create_indexes(conn):
    """创建索引"""
    try:
        # 为projects表创建索引
        indexes = [
            # 主键和外键索引会自动创建
            "CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)",
            "CREATE INDEX IF NOT EXISTS idx_projects_category ON projects(category)",
            "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)",
            "CREATE INDEX IF NOT EXISTS idx_projects_overall_score ON projects(overall_score)",
            "CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at)",
            
            # scoring_history表索引
            "CREATE INDEX IF NOT EXISTS idx_scoring_history_project_id ON scoring_history(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_scoring_history_created_at ON scoring_history(created_at)",
            
            # project_categories表索引
            "CREATE INDEX IF NOT EXISTS idx_project_categories_name ON project_categories(name)",
            
            # tech_stack_definitions表索引
            "CREATE INDEX IF NOT EXISTS idx_tech_stack_definitions_name ON tech_stack_definitions(name)",
            "CREATE INDEX IF NOT EXISTS idx_tech_stack_definitions_category ON tech_stack_definitions(category)",
        ]
        
        for sql in indexes:
            await conn.execute(text(sql))
        
        logger.info("索引创建成功")
        
    except Exception as e:
        logger.error(f"创建索引失败: {e}")
        raise


async def seed_initial_data():
    """初始化数据"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.begin() as conn:
            # 清空现有数据（如果需要）
            if settings.DEBUG:
                await conn.execute(text("DELETE FROM project_categories"))
                await conn.execute(text("DELETE FROM tech_stack_definitions"))
            
            # 插入项目分类数据
            categories = [
                {
                    "name": "web_development",
                    "description": "Web应用开发项目",
                    "keywords": ["web", "website", "application", "frontend", "backend"],
                    "priority": 10
                },
                {
                    "name": "mobile_app",
                    "description": "移动应用开发项目",
                    "keywords": ["mobile", "app", "ios", "android", "flutter", "react native"],
                    "priority": 9
                },
                {
                    "name": "data_science",
                    "description": "数据科学和数据分析项目",
                    "keywords": ["data", "analysis", "science", "visualization", "big data"],
                    "priority": 8
                },
                {
                    "name": "machine_learning",
                    "description": "机器学习和人工智能项目",
                    "keywords": ["ai", "ml", "machine learning", "deep learning", "neural network"],
                    "priority": 8
                },
                {
                    "name": "iot",
                    "description": "物联网项目",
                    "keywords": ["iot", "internet of things", "sensor", "smart device", "embedded"],
                    "priority": 7
                },
                {
                    "name": "blockchain",
                    "description": "区块链和加密货币项目",
                    "keywords": ["blockchain", "crypto", "smart contract", "distributed ledger"],
                    "priority": 6
                },
                {
                    "name": "game_development",
                    "description": "游戏开发项目",
                    "keywords": ["game", "gaming", "unity", "unreal engine", "graphics"],
                    "priority": 7
                },
                {
                    "name": "desktop_application",
                    "description": "桌面应用程序",
                    "keywords": ["desktop", "application", "windows", "mac", "linux"],
                    "priority": 6
                },
                {
                    "name": "embedded_systems",
                    "description": "嵌入式系统项目",
                    "keywords": ["embedded", "firmware", "hardware", "microcontroller"],
                    "priority": 5
                },
                {
                    "name": "cloud_infrastructure",
                    "description": "云基础设施项目",
                    "keywords": ["cloud", "infrastructure", "devops", "kubernetes", "docker"],
                    "priority": 8
                }
            ]
            
            for cat in categories:
                await conn.execute(
                    text("""
                    INSERT INTO project_categories (name, description, keywords, priority, is_active, created_at)
                    VALUES (:name, :description, :keywords, :priority, true, NOW())
                    ON CONFLICT (name) DO NOTHING
                    """),
                    cat
                )
            
            logger.info(f"插入了 {len(categories)} 个分类")
            
            # 插入技术栈数据
            tech_stacks = [
                # 编程语言
                {"name": "python", "category": "language", "aliases": ["py"], "popularity_score": 0.9},
                {"name": "javascript", "category": "language", "aliases": ["js", "ecmascript"], "popularity_score": 0.95},
                {"name": "java", "category": "language", "aliases": [], "popularity_score": 0.8},
                {"name": "c++", "category": "language", "aliases": ["cpp"], "popularity_score": 0.7},
                {"name": "c#", "category": "language", "aliases": ["csharp"], "popularity_score": 0.75},
                {"name": "go", "category": "language", "aliases": ["golang"], "popularity_score": 0.7},
                {"name": "rust", "category": "language", "aliases": [], "popularity_score": 0.6},
                {"name": "ruby", "category": "language", "aliases": [], "popularity_score": 0.5},
                {"name": "php", "category": "language", "aliases": [], "popularity_score": 0.6},
                {"name": "swift", "category": "language", "aliases": [], "popularity_score": 0.6},
                
                # Web框架
                {"name": "django", "category": "framework", "aliases": [], "popularity_score": 0.8},
                {"name": "flask", "category": "framework", "aliases": [], "popularity_score": 0.7},
                {"name": "fastapi", "category": "framework", "aliases": [], "popularity_score": 0.6},
                {"name": "express", "category": "framework", "aliases": ["expressjs"], "popularity_score": 0.85},
                {"name": "react", "category": "framework", "aliases": ["reactjs"], "popularity_score": 0.9},
                {"name": "vue", "category": "framework", "aliases": ["vuejs"], "popularity_score": 0.8},
                {"name": "angular", "category": "framework", "aliases": ["angularjs"], "popularity_score": 0.7},
                {"name": "spring", "category": "framework", "aliases": ["spring boot"], "popularity_score": 0.7},
                {"name": "laravel", "category": "framework", "aliases": [], "popularity_score": 0.6},
                
                # 数据库
                {"name": "postgresql", "category": "database", "aliases": ["postgres"], "popularity_score": 0.8},
                {"name": "mysql", "category": "database", "aliases": [], "popularity_score": 0.7},
                {"name": "mongodb", "category": "database", "aliases": ["mongo"], "popularity_score": 0.7},
                {"name": "redis", "category": "database", "aliases": [], "popularity_score": 0.8},
                {"name": "elasticsearch", "category": "database", "aliases": ["es"], "popularity_score": 0.6},
                {"name": "cassandra", "category": "database", "aliases": [], "popularity_score": 0.5},
                
                # 云平台
                {"name": "aws", "category": "cloud", "aliases": ["amazon web services"], "popularity_score": 0.9},
                {"name": "azure", "category": "cloud", "aliases": ["microsoft azure"], "popularity_score": 0.7},
                {"name": "google_cloud", "category": "cloud", "aliases": ["gcp"], "popularity_score": 0.7},
                {"name": "aliyun", "category": "cloud", "aliases": ["alibaba cloud"], "popularity_score": 0.6},
                {"name": "heroku", "category": "cloud", "aliases": [], "popularity_score": 0.5},
                
                # 工具和平台
                {"name": "docker", "category": "tool", "aliases": [], "popularity_score": 0.85},
                {"name": "kubernetes", "category": "tool", "aliases": ["k8s"], "popularity_score": 0.7},
                {"name": "git", "category": "tool", "aliases": ["github", "gitlab"], "popularity_score": 0.95},
                {"name": "jenkins", "category": "tool", "aliases": [], "popularity_score": 0.6},
                {"name": "terraform", "category": "tool", "aliases": [], "popularity_score": 0.6},
            ]
            
            for tech in tech_stacks:
                await conn.execute(
                    text("""
                    INSERT INTO tech_stack_definitions (name, category, aliases, popularity_score, is_active, created_at)
                    VALUES (:name, :category, :aliases, :popularity_score, true, NOW())
                    ON CONFLICT (name) DO NOTHING
                    """),
                    tech
                )
            
            logger.info(f"插入了 {len(tech_stacks)} 个技术栈定义")
            
            await conn.commit()
            
    except Exception as e:
        logger.error(f"初始化数据失败: {e}")
        raise


async def verify_database():
    """验证数据库连接和结构"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.connect() as conn:
            # 测试连接
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("数据库连接正常")
            
            # 检查表是否存在
            tables = ["projects", "scoring_history", "project_categories", "tech_stack_definitions"]
            
            for table in tables:
                result = await conn.execute(
                    text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table)"),
                    {"table": table}
                )
                exists = result.scalar()
                if exists:
                    logger.info(f"表 {table} 存在")
                else:
                    logger.warning(f"表 {table} 不存在")
            
            # 检查数据
            result = await conn.execute(text("SELECT COUNT(*) FROM project_categories"))
            category_count = result.scalar()
            logger.info(f"项目分类数量: {category_count}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM tech_stack_definitions"))
            tech_count = result.scalar()
            logger.info(f"技术栈定义数量: {tech_count}")
            
    except Exception as e:
        logger.error(f"数据库验证失败: {e}")
        raise


async def main():
    """主函数"""
    try:
        logger.info("开始数据库初始化...")
        
        # 创建表
        await create_tables()
        
        # 初始化数据
        await seed_initial_data()
        
        # 验证数据库
        await verify_database()
        
        logger.info("数据库初始化完成!")
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())