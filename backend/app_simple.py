# backend/app_simple.py - 超简化的FastAPI应用（专门用于Render部署）
import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="项目识别智能评分系统",
    description="基于AI的项目识别与智能评分系统（云端部署版）",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单的内存数据库（用于演示）
projects_db = {}
analyses_db = {}
scores_db = {}

# 简化的评分算法
class SimpleScoringAlgorithm:
    """简化的评分算法"""
    
    @staticmethod
    def calculate_score(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算项目评分"""
        
        # 基础评分逻辑
        score = 50.0  # 基础分
        
        # 根据项目特征调整分数
        if project_data.get("has_documentation", False):
            score += 10
        if project_data.get("has_tests", False):
            score += 15
        if project_data.get("has_ci_cd", False):
            score += 10
            
        # 根据团队规模调整
        team_size = project_data.get("team_size", 1)
        if team_size > 5:
            score += 5
        elif team_size > 10:
            score += 10
            
        # 根据复杂度调整
        complexity = project_data.get("estimated_complexity", "低")
        if complexity == "中等":
            score += 5
        elif complexity == "高":
            score += 10
            
        # 确保分数在0-100之间
        score = max(0, min(100, score))
        
        # 生成详细评分
        breakdown = {
            "基础分": 50.0,
            "文档完整性": 10 if project_data.get("has_documentation") else 0,
            "测试覆盖": 15 if project_data.get("has_tests") else 0,
            "CI/CD": 10 if project_data.get("has_ci_cd") else 0,
            "团队规模": min(10, (team_size - 1) * 2),
            "项目复杂度": {
                "低": 0,
                "中等": 5,
                "高": 10
            }.get(complexity, 0)
        }
        
        # 生成建议
        recommendations = []
        if not project_data.get("has_documentation", False):
            recommendations.append("建议添加项目文档")
        if not project_data.get("has_tests", False):
            recommendations.append("建议添加单元测试")
        if not project_data.get("has_ci_cd", False):
            recommendations.append("建议配置CI/CD流水线")
            
        return {
            "final_score": round(score, 1),
            "breakdown": breakdown,
            "recommendations": recommendations[:3]  # 最多3条建议
        }

# 项目模型
class ProjectCreate:
    def __init__(self, name: str, description: str = "", repo_url: str = "", tags: List[str] = None):
        self.name = name
        self.description = description
        self.repo_url = repo_url
        self.tags = tags or []

# API路由
@app.get("/")
async def root():
    """根目录"""
    return {
        "message": "欢迎使用项目识别智能评分系统",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api": "/api",
        "endpoints": [
            "/projects",
            "/analyze/score",
            "/projects/{id}/rating"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "database": "in-memory",
        "message": "系统运行正常"
    }

@app.get("/api/projects")
async def get_projects():
    """获取所有项目"""
    return {
        "projects": list(projects_db.values()),
        "count": len(projects_db)
    }

@app.post("/api/projects")
async def create_project(data: Dict[str, Any]):
    """创建新项目"""
    project_id = f"proj_{int(datetime.now().timestamp())}"
    
    project = {
        "id": project_id,
        "name": data.get("name", "未命名项目"),
        "description": data.get("description", ""),
        "repo_url": data.get("repo_url", ""),
        "tags": data.get("tags", []),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    projects_db[project_id] = project
    return {"project": project, "message": "项目创建成功"}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """获取特定项目"""
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return {"project": project}

@app.post("/api/analyze/score")
async def analyze_and_score_project(data: Dict[str, Any]):
    """分析并评分项目"""
    project_data = data.get("project_data", {})
    
    # 使用简化算法计算分数
    algorithm = SimpleScoringAlgorithm()
    score_result = algorithm.calculate_score(project_data)
    
    # 存储评分结果
    score_id = f"score_{int(datetime.now().timestamp())}"
    scores_db[score_id] = {
        "id": score_id,
        "project_data": project_data,
        "score_result": score_result,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "analysis_result": {
            "project_data": project_data,
            "scoring_result": score_result
        },
        "message": "项目分析和评分完成"
    }

@app.get("/api/projects/{project_id}/rating")
async def get_project_rating(project_id: str):
    """获取项目评分"""
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 查找该项目的评分
    project_scores = []
    for score_id, score_data in scores_db.items():
        if score_data.get("project_data", {}).get("name") == project["name"]:
            project_scores.append(score_data["score_result"])
    
    if not project_scores:
        # 如果没有评分，创建一个演示评分
        algorithm = SimpleScoringAlgorithm()
        demo_data = {
            "name": project["name"],
            "has_documentation": True,
            "has_tests": len(project.get("tags", [])) > 0,
            "has_ci_cd": bool(project.get("repo_url")),
            "team_size": 3,
            "estimated_complexity": "中等"
        }
        project_scores.append(algorithm.calculate_score(demo_data))
    
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "ratings": project_scores,
        "average_score": round(sum(s["final_score"] for s in project_scores) / len(project_scores), 1) if project_scores else 0
    }

@app.get("/api/demo")
async def demo():
    """演示端点"""
    # 创建演示项目
    demo_project = {
        "id": "demo_001",
        "name": "示例项目 - AI智能助手",
        "description": "这是一个演示项目，展示AI智能助手的功能",
        "repo_url": "https://github.com/example/ai-assistant",
        "tags": ["AI", "Python", "FastAPI", "机器学习"],
        "created_at": datetime.now().isoformat()
    }
    
    projects_db["demo_001"] = demo_project
    
    # 创建演示评分
    demo_data = {
        "name": demo_project["name"],
        "has_documentation": True,
        "has_tests": True,
        "has_ci_cd": True,
        "team_size": 5,
        "estimated_complexity": "高"
    }
    
    algorithm = SimpleScoringAlgorithm()
    score_result = algorithm.calculate_score(demo_data)
    
    scores_db["demo_score"] = {
        "id": "demo_score",
        "project_data": demo_data,
        "score_result": score_result,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "演示数据已创建",
        "project": demo_project,
        "score": score_result,
        "endpoints": {
            "root": "/",
            "health": "/health",
            "projects": "/api/projects",
            "analyze": "/api/analyze/score",
            "rating": "/api/projects/demo_001/rating"
        }
    }

# 主函数
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"启动项目识别智能评分系统 v1.0.0")
    print(f"服务器地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"健康检查: http://{host}:{port}/health")
    print(f"演示数据: http://{host}:{port}/api/demo")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )