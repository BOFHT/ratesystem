"""
中间件模块
"""

import time
import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import aioredis
from config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始
        start_time = time.time()
        
        # 获取客户端信息
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # 跳过健康检查的详细日志
        if request.url.path == "/health":
            response = await call_next(request)
            return response
        
        logger.info(f"请求开始: {request.method} {request.url.path} from {client_host}")
        logger.debug(f"请求头: {dict(request.headers)}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"请求完成: {request.method} {request.url.path} "
                f"status={response.status_code} time={process_time:.3f}s"
            )
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Server"] = settings.APP_NAME
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"请求异常: {request.method} {request.url.path} "
                f"error={exc} time={process_time:.3f}s"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.redis_client = None
    
    async def dispatch(self, request: Request, call_next):
        # 跳过某些路径的速率限制
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # 初始化Redis连接
        if self.redis_client is None:
            from .database import get_redis
            try:
                self.redis_client = await get_redis()
            except Exception:
                logger.warning("Redis不可用，跳过速率限制")
                return await call_next(request)
        
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 构建Redis键
        key = f"rate_limit:{client_ip}:{int(time.time() / 60)}"
        
        try:
            # 增加计数器
            current_count = await self.redis_client.incr(key)
            
            # 如果是新键，设置过期时间
            if current_count == 1:
                await self.redis_client.expire(key, 61)  # 61秒确保跨分钟
            
            # 检查是否超过限制
            if current_count > self.requests_per_minute:
                logger.warning(f"速率限制: IP {client_ip} 超过限制")
                raise HTTPException(
                    status_code=429,
                    detail="请求过于频繁，请稍后再试"
                )
            
            # 添加剩余请求数头部
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - current_count)
            response.headers["X-RateLimit-Reset"] = str(int(time.time() / 60 + 1) * 60)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"速率限制中间件错误: {e}")
            # Redis出错时跳过速率限制
            return await call_next(request)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """认证中间件（示例）"""
    
    async def dispatch(self, request: Request, call_next):
        # 跳过公开路径
        public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json", "/api/info"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # 检查API密钥
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            logger.warning("未提供API密钥")
            raise HTTPException(
                status_code=401,
                detail="未提供API密钥"
            )
        
        # 验证API密钥（这里应该从数据库或配置中验证）
        # 实际应用中应使用更安全的验证方式
        valid_keys = ["test-key-123", "dev-key-456"]  # 示例
        if api_key not in valid_keys:
            logger.warning(f"无效的API密钥: {api_key}")
            raise HTTPException(
                status_code=401,
                detail="无效的API密钥"
            )
        
        # 将用户信息添加到请求状态
        request.state.user = {"api_key": api_key, "role": "user"}
        
        return await call_next(request)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件"""
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        # 生成请求ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # 将请求ID添加到请求状态
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """压缩中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 检查客户端是否支持压缩
        accept_encoding = request.headers.get("Accept-Encoding", "")
        
        response = await call_next(request)
        
        # 只压缩特定类型的内容
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type or "text/plain" in content_type:
            # 检查响应大小
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > 1024:  # 大于1KB才压缩
                # 这里可以添加实际的压缩逻辑
                # 例如使用gzip或brotli
                pass
        
        return response


# 中间件配置
MIDDLEWARE_CONFIG = {
    "logging": {
        "enabled": True,
        "class": LoggingMiddleware,
        "exclude_paths": ["/health", "/metrics"]
    },
    "rate_limit": {
        "enabled": True,
        "class": RateLimitMiddleware,
        "requests_per_minute": 60,
        "exclude_paths": ["/health", "/docs", "/redoc"]
    },
    "authentication": {
        "enabled": False,  # 根据需求开启
        "class": AuthenticationMiddleware,
        "exclude_paths": ["/", "/health", "/docs", "/redoc", "/api/info"]
    },
    "request_id": {
        "enabled": True,
        "class": RequestIDMiddleware
    },
    "compression": {
        "enabled": False,  # 根据需求开启
        "class": CompressionMiddleware,
        "min_size": 1024  # 最小压缩大小
    }
}