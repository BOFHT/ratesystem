# backend/app_cloud.py - 云端部署版FastAPI应用
import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# 导入配置和数据库
from config_cloud import settings
try:
    from backend.database_sqlite import get_db, Project, ProjectAnalysis, ScoringLog
except ImportError:
    # 创建简单的替代类
    class Project:
        pass
    class ProjectAnalysis:
        pass
    class ScoringLog:
        pass
    # 创建简单的get_db函数
    def get_db():
        return None

# 导入Pydantic模型
try:
    from pydantic import BaseModel
except ImportError:
    # 如果pydantic不可用，使用简单字典
    BaseModel = dict

# 定义请求/响应模型
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    code_language: Optional[str] = None
    framework: Optional[str] = None
    git_url: Optional[str] = None
    estimated_complexity: Optional[str] = None
    estimated_development_time: Optional[str] = None
    team_size: Optional[int] = None
    has_documentation: bool = False
    has_tests: bool = False
    has_ci_cd: bool = False

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    code_language: Optional[str] = None
    framework: Optional[str] = None
    git_url: Optional[str] = None
    estimated_complexity: Optional[str] = None
    estimated_development_time: Optional[str] = None
    team_size: Optional[int] = None
    has_documentation: bool
    has_tests: bool
    has_ci_cd: bool
    created_at: str
    updated_at: str

class ScoreRequest(BaseModel):
    project_id: int
    algorithm: str = "advanced"

class ScoreResponse(BaseModel):
    status: str
    project_id: int
    algorithm: str
    final_score: float
    breakdown: Dict[str, float]
    recommendations: List[str]
    calculated_at: str

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    features: Dict[str, bool]

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="项目评分系统 - 云端部署版",
    version=settings.VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（如果存在）
static_dir = project_root / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 简单的评分算法（云端简化版）
class SimpleScoringAlgorithm:
    """简化的评分算法 - 适合云端部署"""
    
    @staticmethod
    def calculate_score(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算项目评分"""
        
        # 基础评分逻辑
        score = 50.0  # 基础分
        
        # 根据项目特征调整分数
        if project_data.get("has_documentation"):
            score += 10
        if project_data.get("has_tests"):
            score += 15
        if project_data.get("has_ci_cd"):
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
        if not project_data.get("has_documentation"):
            recommendations.append("建议添加项目文档")
        if not project_data.get("has_tests"):
            recommendations.append("建议添加单元测试")
        if not project_data.get("has_ci_cd"):
            recommendations.append("建议配置CI/CD流水线")
            
        return {
            "final_score": round(score, 1),
            "breakdown": breakdown,
            "recommendations": recommendations[:3]  # 最多3条建议
        }

# API路由
@app.get("/")
async def root():
    """根目录"""
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1",
        "endpoints": ["/projects", "/analyze", "/scoring"]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "database": "sqlite",
        "message": f"{settings.APP_NAME}运行正常"
    }

@app.post("/projects/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """创建新项目"""
    try:
        db_project = Project(**project.dict())
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

@app.get("/projects/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """列出所有项目"""
    try:
        projects = db.query(Project).offset(skip).limit(limit).all()
        return [p.to_dict() for p in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project.to_dict()

@app.post("/analyze/score", response_model=ScoreResponse)
async def score_project(
    request: ScoreRequest,
    db: Session = Depends(get_db)
):
    """项目评分"""
    try:
        # 获取项目信息
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 转换为字典格式
        project_data = project.to_dict()
        
        # 使用简化算法评分
        algorithm = SimpleScoringAlgorithm()
        score_result = algorithm.calculate_score(project_data)
        
        # 更新项目评分信息
        import json
        from datetime import datetime
        
        project.rating_score = score_result["final_score"]
        project.rating_algorithm = request.algorithm
        project.rating_breakdown = json.dumps(score_result["breakdown"])
        project.rating_recommendations = json.dumps(score_result["recommendations"])
        project.rating_calculated_at = datetime.utcnow()
        
        db.commit()
        
        # 创建评分日志
        scoring_log = ScoringLog(
            project_id=request.project_id,
            algorithm=request.algorithm,
            score=score_result["final_score"],
            breakdown=json.dumps(score_result["breakdown"]),
            recommendations=json.dumps(score_result["recommendations"])
        )
        db.add(scoring_log)
        db.commit()
        
        # 返回评分结果
        return {
            "status": "success",
            "project_id": request.project_id,
            "algorithm": request.algorithm,
            "final_score": score_result["final_score"],
            "breakdown": score_result["breakdown"],
            "recommendations": score_result["recommendations"],
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评分失败: {str(e)}")

@app.get("/projects/{project_id}/rating")
async def get_project_rating(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取项目评分"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if not project.rating_score:
        raise HTTPException(status_code=404, detail="项目尚未评分")
    
    import json
    rating_data = {
        "score": project.rating_score,
        "algorithm": project.rating_algorithm,
        "calculated_at": project.rating_calculated_at.isoformat() if project.rating_calculated_at else None,
    }
    
    # 解析详细评分
    try:
        if project.rating_breakdown:
            rating_data["breakdown"] = json.loads(project.rating_breakdown)
        if project.rating_recommendations:
            rating_data["recommendations"] = json.loads(project.rating_recommendations)
    except json.JSONDecodeError:
        pass
    
    return rating_data

# 示例数据端点
@app.get("/examples")
async def get_examples():
    """获取示例项目数据"""
    examples = [
        {
            "name": "OpenClaw智能助手",
            "description": "基于OpenClaw的AI个人助手系统",
            "code_language": "Python",
            "framework": "FastAPI",
            "estimated_complexity": "中等",
            "has_documentation": True,
            "has_tests": True,
            "has_ci_cd": True,
            "team_size": 5
        },
        {
            "name": "电商数据分析平台",
            "description": "大数据分析平台，支持用户行为分析和销售预测",
            "code_language": "Java",
            "framework": "Spring Boot",
            "estimated_complexity": "高",
            "has_documentation": True,
            "has_tests": True,
            "has_ci_cd": True,
            "team_size": 10
        },
        {
            "name": "个人博客系统",
            "description": "简单的个人博客系统",
            "code_language": "JavaScript",
            "framework": "React + Node.js",
            "estimated_complexity": "低",
            "has_documentation": False,
            "has_tests": False,
            "has_ci_cd": False,
            "team_size": 1
        }
    ]
    return {"examples": examples}

if __name__ == "__main__":
    # 直接运行时启动服务器
    print(f"启动 {settings.APP_NAME}...")
    uvicorn.run(
        "app_cloud:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG
    )