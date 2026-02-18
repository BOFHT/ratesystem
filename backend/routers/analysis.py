"""
分析路由
项目分析相关API
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..database import get_db, Project
from ..schemas import AnalysisRequest, AnalysisResult
from ..ml_models import analyze_project, classify_project, analyze_tech_stack, extract_features

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=AnalysisResult)
async def analyze_project_endpoint(
    analysis_request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    分析项目
    
    Args:
        analysis_request: 分析请求
        
    Returns:
        分析结果
    """
    try:
        project_data = analysis_request.project_data
        
        # 生成分析ID（如果未提供项目ID）
        analysis_id = str(uuid.uuid4())[:8]
        
        # 执行分析
        analysis_result = await analyze_project(project_data)
        
        # 构建响应
        result = AnalysisResult(
            project_id=None,  # 可以后续关联
            project_name=project_data.get("name", f"未命名项目-{analysis_id}"),
            category=analysis_result.get("category", {}).get("name"),
            tech_stack_analysis=analysis_result.get("tech_stack_analysis", {}),
            complexity_score=analysis_result.get("complexity_score", 50.0),
            maturity_score=analysis_result.get("maturity_score", 50.0),
            risk_assessment=analysis_result.get("risk_assessment", {}),
            recommendations=analysis_result.get("recommendations", []),
            analysis_timestamp=analysis_result.get("model_versions", {}).get("timestamp") or "now"
        )
        
        logger.info(f"项目分析完成: {result.project_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"项目分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/classify", response_model=Dict[str, Any])
async def classify_project_endpoint(
    project_data: Dict[str, Any] = Body(..., description="项目数据")
):
    """
    分类项目
    
    Args:
        project_data: 项目数据
        
    Returns:
        分类结果
    """
    try:
        classification_result = await classify_project(project_data)
        
        return {
            "success": True,
            "classification": classification_result,
            "project_name": project_data.get("name", "未命名项目")
        }
        
    except Exception as e:
        logger.error(f"项目分类失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "classification": {"name": "unknown", "confidence": 0.0}
        }


@router.post("/tech-stack", response_model=Dict[str, Any])
async def analyze_tech_stack_endpoint(
    project_data: Dict[str, Any] = Body(..., description="项目数据")
):
    """
    分析技术栈
    
    Args:
        project_data: 项目数据
        
    Returns:
        技术栈分析结果
    """
    try:
        tech_analysis = await analyze_tech_stack(project_data)
        
        return {
            "success": True,
            "tech_stack_analysis": tech_analysis,
            "detected_count": len(tech_analysis.get("detected_tech", [])),
            "confidence": tech_analysis.get("confidence", 0.0)
        }
        
    except Exception as e:
        logger.error(f"技术栈分析失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "tech_stack_analysis": {"detected_tech": [], "confidence": 0.0}
        }


@router.post("/extract-features", response_model=Dict[str, Any])
async def extract_features_endpoint(
    project_data: Dict[str, Any] = Body(..., description="项目数据")
):
    """
    提取项目特征
    
    Args:
        project_data: 项目数据
        
    Returns:
        特征提取结果
    """
    try:
        features = await extract_features(project_data)
        
        return {
            "success": True,
            "features": features,
            "feature_count": len(features),
            "categories": {
                "text_features": len([k for k in features.keys() if "text" in k or "word" in k]),
                "tech_features": len([k for k in features.keys() if "tech" in k]),
                "quality_features": len([k for k in features.keys() if "quality" in k]),
                "complexity_features": len([k for k in features.keys() if "complexity" in k])
            }
        }
        
    except Exception as e:
        logger.error(f"特征提取失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "features": {},
            "feature_count": 0
        }


@router.post("/compare")
async def compare_projects(
    project1: Dict[str, Any] = Body(..., description="项目1数据"),
    project2: Dict[str, Any] = Body(..., description="项目2数据"),
    compare_type: str = Query("full", description="比较类型: full/tech/features")
):
    """
    比较两个项目
    
    Args:
        project1: 项目1数据
        project2: 项目2数据
        compare_type: 比较类型
        
    Returns:
        比较结果
    """
    try:
        from ..ml_models.nlp_processor import NLPProcessor
        
        # 分析两个项目
        analysis1 = await analyze_project(project1)
        analysis2 = await analyze_project(project2)
        
        # 创建NLP处理器比较文本
        nlp_processor = NLPProcessor()
        await nlp_processor.load_model()
        
        text1 = f"{project1.get('name', '')} {project1.get('description', '')}"
        text2 = f"{project2.get('name', '')} {project2.get('description', '')}"
        
        text_comparison = await nlp_processor.compare_texts(text1, text2)
        
        # 构建比较结果
        comparison = {
            "project1": {
                "name": project1.get("name", "项目1"),
                "category": analysis1.get("category", {}),
                "tech_stack": analysis1.get("tech_stack_analysis", {}).get("detected_tech", []),
                "complexity": analysis1.get("complexity_score", 50.0),
                "risk": analysis1.get("risk_assessment", {}).get("level", "medium")
            },
            "project2": {
                "name": project2.get("name", "项目2"),
                "category": analysis2.get("category", {}),
                "tech_stack": analysis2.get("tech_stack_analysis", {}).get("detected_tech", []),
                "complexity": analysis2.get("complexity_score", 50.0),
                "risk": analysis2.get("risk_assessment", {}).get("level", "medium")
            },
            "comparisons": {
                "category_similarity": analysis1.get("category", {}).get("name") == analysis2.get("category", {}).get("name"),
                "tech_overlap": list(set(analysis1.get("tech_stack_analysis", {}).get("detected_tech", [])) &
                                   set(analysis2.get("tech_stack_analysis", {}).get("detected_tech", []))),
                "complexity_difference": abs(analysis1.get("complexity_score", 50.0) - analysis2.get("complexity_score", 50.0)),
                "text_similarity": text_comparison.get("similarity_score", 0.0)
            },
            "recommendations": []
        }
        
        # 生成比较建议
        if comparison["comparisons"]["category_similarity"]:
            comparison["recommendations"].append("两个项目属于相同领域，可考虑技术共享")
        
        tech_overlap = len(comparison["comparisons"]["tech_overlap"])
        if tech_overlap > 3:
            comparison["recommendations"].append(f"技术栈高度重叠({tech_overlap}项)，团队可互相支持")
        elif tech_overlap == 0:
            comparison["recommendations"].append("技术栈完全不同，需要不同技能团队")
        
        complexity_diff = comparison["comparisons"]["complexity_difference"]
        if complexity_diff > 20:
            comparison["recommendations"].append("项目复杂度差异较大，需要不同的管理策略")
        
        return {
            "success": True,
            "comparison": comparison,
            "text_comparison": text_comparison
        }
        
    except Exception as e:
        logger.error(f"项目比较失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "comparison": {}
        }


@router.get("/models/info")
async def get_models_info():
    """
    获取模型信息
    
    Returns:
        模型信息
    """
    try:
        from ..ml_models import (
            ProjectClassifier, TechStackAnalyzer, 
            FeatureExtractor, NLPProcessor
        )
        
        # 创建实例并获取信息
        classifier = ProjectClassifier()
        await classifier.load_model()
        
        tech_analyzer = TechStackAnalyzer()
        await tech_analyzer.load_model()
        
        feature_extractor = FeatureExtractor()
        await feature_extractor.load_model()
        
        nlp_processor = NLPProcessor()
        await nlp_processor.load_model()
        
        return {
            "models": {
                "project_classifier": classifier.get_model_info(),
                "tech_stack_analyzer": tech_analyzer.get_model_info(),
                "feature_extractor": feature_extractor.get_model_info(),
                "nlp_processor": nlp_processor.get_model_info()
            },
            "status": "loaded",
            "total_models": 4
        }
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        return {
            "models": {},
            "status": "error",
            "error": str(e)
        }


@router.post("/models/train")
async def train_models(
    training_data: Optional[List[Dict[str, Any]]] = Body(None, description="训练数据"),
    model_type: str = Query("all", description="训练模型类型: all/classifier/tech/features")
):
    """
    训练模型
    
    Args:
        training_data: 训练数据
        model_type: 训练模型类型
        
    Returns:
        训练结果
    """
    try:
        results = {}
        
        if model_type in ["all", "classifier"]:
            from ..ml_models.project_classifier import ProjectClassifier
            classifier = ProjectClassifier()
            train_result = await classifier.train_model(training_data)
            results["classifier"] = train_result
        
        if model_type in ["all", "features"]:
            from ..ml_models.feature_extractor import FeatureExtractor
            feature_extractor = FeatureExtractor()
            await feature_extractor.load_model()
            if training_data:
                train_result = await feature_extractor.train_model(training_data)
                results["feature_extractor"] = train_result
        
        return {
            "success": True,
            "training_results": results,
            "model_type": model_type,
            "training_samples": len(training_data) if training_data else 0
        }
        
    except Exception as e:
        logger.error(f"训练模型失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "training_results": {}
        }


@router.get("/recommendations")
async def get_recommendations(
    project_id: Optional[int] = Query(None, description="项目ID"),
    project_data: Optional[Dict[str, Any]] = Body(None, description="项目数据"),
    recommendation_type: str = Query("all", description="建议类型: all/tech/architecture/business")
):
    """
    获取项目建议
    
    Args:
        project_id: 项目ID
        project_data: 项目数据
        recommendation_type: 建议类型
        
    Returns:
        建议列表
    """
    try:
        # 获取项目数据
        if project_id:
            query = select(Project).where(Project.id == project_id)
            result = await db.execute(query)
            project = result.scalar_one_or_none()
            
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
            
            project_data = {
                "name": project.name,
                "description": project.description,
                "category": project.category,
                "tech_stack": project.tech_stack,
                "metadata": project.metadata
            }
        elif not project_data:
            raise HTTPException(status_code=400, detail="需要提供项目ID或项目数据")
        
        # 分析项目
        analysis_result = await analyze_project(project_data)
        
        # 提取建议
        all_recommendations = analysis_result.get("recommendations", [])
        
        # 按类型过滤
        filtered_recommendations = []
        if recommendation_type == "all":
            filtered_recommendations = all_recommendations
        else:
            # 简单的关键词过滤
            type_keywords = {
                "tech": ["技术", "框架", "语言", "数据库", "升级", "替换", "兼容"],
                "architecture": ["架构", "设计", "微服务", "模块", "解耦", "扩展"],
                "business": ["商业", "市场", "用户", "需求", "价值", "收入", "增长"]
            }
            
            keywords = type_keywords.get(recommendation_type, [])
            for rec in all_recommendations:
                if any(keyword in rec for keyword in keywords):
                    filtered_recommendations.append(rec)
            
            # 如果过滤后为空，返回通用建议
            if not filtered_recommendations:
                filtered_recommendations = all_recommendations[:3]
        
        return {
            "success": True,
            "project_name": project_data.get("name", "未命名项目"),
            "recommendations": filtered_recommendations,
            "total_count": len(filtered_recommendations),
            "recommendation_type": recommendation_type,
            "analysis_summary": {
                "category": analysis_result.get("category", {}).get("name", "unknown"),
                "complexity": analysis_result.get("complexity_score", 50.0),
                "risk_level": analysis_result.get("risk_assessment", {}).get("level", "medium")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取建议失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "recommendations": ["分析过程中出现错误，请稍后重试"]
        }


@router.get("/health")
async def analysis_health_check():
    """
    分析模块健康检查
    
    Returns:
        健康状态
    """
    try:
        # 测试模型加载
        from ..ml_models import analyze_project
        
        test_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "tech_stack": ["python", "fastapi"]
        }
        
        # 快速分析测试
        result = await analyze_project(test_data)
        
        return {
            "status": "healthy",
            "models_loaded": True,
            "analysis_capable": True,
            "test_result": {
                "category": result.get("category", {}).get("name", "unknown"),
                "success": result.get("category", {}).get("confidence", 0) > 0
            },
            "timestamp": "now"
        }
        
    except Exception as e:
        logger.error(f"分析健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "models_loaded": False,
            "analysis_capable": False,
            "error": str(e),
            "timestamp": "now"
        }