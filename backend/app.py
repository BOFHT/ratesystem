"""
项目识别智能评分系统 - 主应用
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from config import settings
from .database import init_db, close_db
from .routers import projects, scoring, analysis
from .middleware import LoggingMiddleware, RateLimitMiddleware

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 初始化数据库连接
    await init_db()
    logger.info("数据库连接已初始化")
    
    # 加载机器学习模型
    try:
        from .ml_models import load_models
        await load_models()
        logger.info("机器学习模型已加载")
    except Exception as e:
        logger.warning(f"模型加载失败: {e}")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭应用...")
    await close_db()
    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="项目识别智能评分系统API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)


# 异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.exception(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "内部错误"
        }
    )


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": "connected",  # 实际应检查数据库连接
            "redis": "connected",     # 实际应检查Redis连接
            "models": "loaded"        # 实际应检查模型状态
        }
    }


@app.get("/api/info")
async def api_info():
    """API信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs" if settings.DEBUG else None,
        "endpoints": [
            {"path": "/api/v1/projects", "methods": ["GET", "POST"]},
            {"path": "/api/v1/projects/{id}", "methods": ["GET", "PUT", "DELETE"]},
            {"path": "/api/v1/scoring", "methods": ["POST"]},
            {"path": "/api/v1/analysis", "methods": ["POST"]}
        ]
    }


# 注册路由
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目"])
app.include_router(scoring.router, prefix="/api/v1/scoring", tags=["评分"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["分析"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1
    )