"""
数据库模块
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy基类
Base = declarative_base()

# 数据库引擎
async_engine = None
AsyncSessionLocal = None

# Redis连接
redis_client = None

# MongoDB连接
mongo_client = None
mongo_db = None


async def init_db():
    """初始化数据库连接"""
    global async_engine, AsyncSessionLocal, redis_client, mongo_client, mongo_db
    
    try:
        # PostgreSQL初始化
        async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("PostgreSQL连接已建立")
        
        # Redis初始化
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
        
        logger.info("Redis连接已建立")
        
        # MongoDB初始化
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        mongo_db = mongo_client.get_database("project_rating")
        
        logger.info("MongoDB连接已建立")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    if AsyncSessionLocal is None:
        raise RuntimeError("数据库未初始化")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """获取Redis连接"""
    if redis_client is None:
        raise RuntimeError("Redis未初始化")
    return redis_client


async def get_mongo():
    """获取MongoDB连接"""
    if mongo_db is None:
        raise RuntimeError("MongoDB未初始化")
    return mongo_db


async def close_db():
    """关闭数据库连接"""
    global async_engine, redis_client, mongo_client
    
    try:
        if async_engine:
            await async_engine.dispose()
            logger.info("PostgreSQL连接已关闭")
        
        if redis_client:
            await redis_client.close()
            logger.info("Redis连接已关闭")
        
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB连接已关闭")
            
    except Exception as e:
        logger.error(f"关闭数据库连接时出错: {e}")


# 数据库模型
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func


class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    tech_stack = Column(JSON, nullable=True)  # 技术栈列表
    metadata = Column(JSON, nullable=True)    # 额外元数据
    
    # 评分相关字段
    quality_score = Column(Float, nullable=True)
    innovation_score = Column(Float, nullable=True)
    feasibility_score = Column(Float, nullable=True)
    business_value_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True, index=True)
    
    # 状态和时间
    status = Column(String(50), default="pending", index=True)  # pending, analyzing, scored, archived
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 索引
    __table_args__ = (
        {"postgresql_include": ["name", "category"]},
    )


class ScoringHistory(Base):
    """评分历史表"""
    __tablename__ = "scoring_history"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # 各项评分
    quality_score = Column(Float, nullable=False)
    innovation_score = Column(Float, nullable=False)
    feasibility_score = Column(Float, nullable=False)
    business_value_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    # 评分详情
    scoring_details = Column(JSON, nullable=True)
    algorithm_version = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 索引
    __table_args__ = (
        {"postgresql_include": ["project_id", "overall_score"]},
    )


class ProjectCategory(Base):
    """项目分类定义表"""
    __tablename__ = "project_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # 分类关键词
    priority = Column(Integer, default=0)  # 分类优先级
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechStackDefinition(Base):
    """技术栈定义表"""
    __tablename__ = "tech_stack_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # language, framework, database, etc.
    aliases = Column(JSON, nullable=True)  # 别名列表
    popularity_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# MongoDB集合定义（用于存储非结构化数据）
class MongoCollections:
    """MongoDB集合名称"""
    PROJECT_RAW_DATA = "project_raw_data"           # 原始项目数据
    ANALYSIS_RESULTS = "analysis_results"           # 详细分析结果
    SCORING_CACHE = "scoring_cache"                 # 评分缓存
    ML_MODEL_METRICS = "ml_model_metrics"          # 模型指标
    USER_FEEDBACK = "user_feedback"                # 用户反馈