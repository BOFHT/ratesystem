"""
评分路由
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from ..database import get_db, Project, ScoringHistory
from ..schemas import (
    ScoringRequest, ScoringResponse, BatchScoringRequest,
    BatchScoringResponse, ScoringResult
)
from ..ml_models import analyze_project
from ..scoring import calculate_project_score, update_project_scores

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ScoringResponse)
async def score_project(
    scoring_request: ScoringRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    对项目进行评分
    
    Args:
        scoring_request: 评分请求
        
    Returns:
        评分结果
    """
    try:
        # 检查项目是否存在
        query = select(Project).where(Project.id == scoring_request.project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 检查项目状态
        if project.status not in ["analyzed", "scored"]:
            # 如果未分析，先分析项目
            logger.info(f"项目 {project.id} 未分析，先进行分析")
            analysis_result = await analyze_project({
                "name": project.name,
                "description": project.description,
                "category": project.category,
                "tech_stack": project.tech_stack,
                "metadata": project.metadata
            })
            
            # 更新分析结果
            await db.execute(
                update(Project)
                .where(Project.id == project.id)
                .values(
                    analysis_result=analysis_result,
                    status="analyzed",
                    analyzed_at=datetime.utcnow()
                )
            )
            
            await db.commit()
            
            # 重新获取项目
            result = await db.execute(query)
            project = result.scalar_one_or_none()
        
        # 计算评分
        scoring_result = await calculate_project_score(
            project=project,
            algorithm=scoring_request.algorithm,
            weights=scoring_request.weights,
            options=scoring_request.options
        )
        
        # 更新项目评分
        await update_project_scores(
            db=db,
            project_id=project.id,
            scoring_result=scoring_result
        )
        
        # 创建评分历史记录
        scoring_history = ScoringHistory(
            project_id=project.id,
            quality_score=scoring_result.quality_score,
            innovation_score=scoring_result.innovation_score,
            feasibility_score=scoring_result.feasibility_score,
            business_value_score=scoring_result.business_value_score,
            overall_score=scoring_result.overall_score,
            scoring_details=scoring_result.scoring_details,
            algorithm_version=scoring_result.algorithm_version
        )
        
        db.add(scoring_history)
        await db.commit()
        
        logger.info(f"项目 {project.id} 评分完成，综合评分: {scoring_result.overall_score}")
        
        return ScoringResponse(
            project_id=project.id,
            project_name=project.name,
            scoring_result=scoring_result,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"项目评分失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"评分失败: {str(e)}")


@router.post("/batch", response_model=BatchScoringResponse)
async def batch_score_projects(
    batch_request: BatchScoringRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批量评分项目
    
    Args:
        batch_request: 批量评分请求
        
    Returns:
        批量评分结果
    """
    try:
        results = []
        failed_projects = []
        
        for project_id in batch_request.project_ids:
            try:
                # 构建单个评分请求
                scoring_request = ScoringRequest(
                    project_id=project_id,
                    algorithm=batch_request.algorithm,
                    weights=batch_request.weights,
                    options=batch_request.options
                )
                
                # 调用单个评分
                scoring_response = await score_project(scoring_request, db)
                results.append(scoring_response)
                
            except Exception as e:
                logger.error(f"项目 {project_id} 评分失败: {e}")
                failed_projects.append(project_id)
        
        return BatchScoringResponse(
            results=results,
            failed_projects=failed_projects,
            total=len(batch_request.project_ids),
            success=len(results)
        )
        
    except Exception as e:
        logger.error(f"批量评分失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量评分失败: {str(e)}")


@router.get("/history")
async def get_scoring_history(
    db: AsyncSession = Depends(get_db),
    project_id: Optional[int] = Query(None, description="项目ID"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="最低评分"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="最高评分"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
):
    """
    获取评分历史
    
    Args:
        project_id: 项目ID
        start_date: 开始日期
        end_date: 结束日期
        min_score: 最低评分
        max_score: 最高评分
        skip: 跳过的记录数
        limit: 返回的记录数
        
    Returns:
        评分历史列表
    """
    try:
        # 构建查询
        from sqlalchemy import and_
        from sqlalchemy.sql import func
        
        query = select(ScoringHistory)
        
        # 应用过滤器
        if project_id:
            query = query.where(ScoringHistory.project_id == project_id)
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
                query = query.where(ScoringHistory.created_at >= start_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式错误")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                query = query.where(ScoringHistory.created_at <= end_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式错误")
        
        if min_score is not None:
            query = query.where(ScoringHistory.overall_score >= min_score)
        
        if max_score is not None:
            query = query.where(ScoringHistory.overall_score <= max_score)
        
        # 排序
        query = query.order_by(ScoringHistory.created_at.desc())
        
        # 分页
        query = query.offset(skip).limit(limit)
        
        # 执行查询
        result = await db.execute(query)
        history_records = result.scalars().all()
        
        # 获取项目信息
        project_names = {}
        if history_records:
            project_ids = list(set([h.project_id for h in history_records]))
            project_query = select(Project.id, Project.name).where(Project.id.in_(project_ids))
            project_result = await db.execute(project_query)
            for project in project_result:
                project_names[project.id] = project.name
        
        # 构建响应
        history_list = []
        for record in history_records:
            history_list.append({
                "id": record.id,
                "project_id": record.project_id,
                "project_name": project_names.get(record.project_id, "未知项目"),
                "quality_score": record.quality_score,
                "innovation_score": record.innovation_score,
                "feasibility_score": record.feasibility_score,
                "business_value_score": record.business_value_score,
                "overall_score": record.overall_score,
                "algorithm_version": record.algorithm_version,
                "created_at": record.created_at.isoformat()
            })
        
        # 获取总数
        count_query = select(func.count()).select_from(ScoringHistory)
        if project_id:
            count_query = count_query.where(ScoringHistory.project_id == project_id)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return {
            "history": history_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评分历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取评分历史失败")


@router.get("/statistics")
async def get_scoring_statistics(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None, description="项目分类"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """
    获取评分统计
    
    Args:
        category: 项目分类
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        评分统计
    """
    try:
        from sqlalchemy import func, case
        
        # 构建基础查询
        query = select(
            func.count(ScoringHistory.id).label("total_scorings"),
            func.avg(ScoringHistory.overall_score).label("avg_overall_score"),
            func.avg(ScoringHistory.quality_score).label("avg_quality_score"),
            func.avg(ScoringHistory.innovation_score).label("avg_innovation_score"),
            func.avg(ScoringHistory.feasibility_score).label("avg_feasibility_score"),
            func.avg(ScoringHistory.business_value_score).label("avg_business_value_score"),
            func.stddev(ScoringHistory.overall_score).label("std_overall_score"),
            func.min(ScoringHistory.overall_score).label("min_overall_score"),
            func.max(ScoringHistory.overall_score).label("max_overall_score")
        ).select_from(ScoringHistory)
        
        # 如果有项目过滤，需要联表查询
        if category:
            query = query.join(Project, ScoringHistory.project_id == Project.id)
            query = query.where(Project.category == category)
        
        # 时间过滤
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
                query = query.where(ScoringHistory.created_at >= start_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式错误")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                query = query.where(ScoringHistory.created_at <= end_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式错误")
        
        # 执行查询
        result = await db.execute(query)
        stats = result.first()
        
        # 评分分布
        distribution_query = select(
            case(
                (ScoringHistory.overall_score < 20, "0-19"),
                (ScoringHistory.overall_score < 40, "20-39"),
                (ScoringHistory.overall_score < 60, "40-59"),
                (ScoringHistory.overall_score < 80, "60-79"),
                (ScoringHistory.overall_score <= 100, "80-100"),
                else_="unknown"
            ).label("score_range"),
            func.count().label("count")
        ).group_by("score_range")
        
        if start_date or end_date:
            if start_date:
                start_datetime = datetime.fromisoformat(start_date)
                distribution_query = distribution_query.where(ScoringHistory.created_at >= start_datetime)
            if end_date:
                end_datetime = datetime.fromisoformat(end_date)
                distribution_query = distribution_query.where(ScoringHistory.created_at <= end_datetime)
        
        distribution_result = await db.execute(distribution_query)
        score_distribution = {
            row.score_range: row.count 
            for row in distribution_result
            if row.score_range != "unknown"
        }
        
        # 按分类统计（如果有分类）
        category_stats = {}
        if not category:  # 只在没有特定分类过滤时统计
            category_query = select(
                Project.category,
                func.count(ScoringHistory.id).label("count"),
                func.avg(ScoringHistory.overall_score).label("avg_score")
            ).join(Project, ScoringHistory.project_id == Project.id) \
             .group_by(Project.category) \
             .order_by(func.count(ScoringHistory.id).desc())
            
            category_result = await db.execute(category_query)
            for row in category_result:
                if row.category:
                    category_stats[row.category] = {
                        "count": row.count,
                        "avg_score": float(row.avg_score) if row.avg_score else 0.0
                    }
        
        # 最近评分趋势（最近7天）
        trend_query = select(
            func.date(ScoringHistory.created_at).label("date"),
            func.count().label("count"),
            func.avg(ScoringHistory.overall_score).label("avg_score")
        ).group_by(func.date(ScoringHistory.created_at)) \
         .order_by(func.date(ScoringHistory.created_at).desc()) \
         .limit(7)
        
        trend_result = await db.execute(trend_query)
        recent_trend = [
            {
                "date": row.date.isoformat() if row.date else "",
                "count": row.count,
                "avg_score": float(row.avg_score) if row.avg_score else 0.0
            }
            for row in trend_result
        ]
        recent_trend.reverse()  # 按时间顺序
        
        return {
            "summary": {
                "total_scorings": stats.total_scorings or 0,
                "avg_overall_score": float(stats.avg_overall_score) if stats.avg_overall_score else 0.0,
                "avg_quality_score": float(stats.avg_quality_score) if stats.avg_quality_score else 0.0,
                "avg_innovation_score": float(stats.avg_innovation_score) if stats.avg_innovation_score else 0.0,
                "avg_feasibility_score": float(stats.avg_feasibility_score) if stats.avg_feasibility_score else 0.0,
                "avg_business_value_score": float(stats.avg_business_value_score) if stats.avg_business_value_score else 0.0,
                "std_overall_score": float(stats.std_overall_score) if stats.std_overall_score else 0.0,
                "min_overall_score": float(stats.min_overall_score) if stats.min_overall_score else 0.0,
                "max_overall_score": float(stats.max_overall_score) if stats.max_overall_score else 0.0
            },
            "score_distribution": score_distribution,
            "category_stats": category_stats,
            "recent_trend": recent_trend,
            "filters": {
                "category": category,
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评分统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取评分统计失败")


@router.get("/algorithms")
async def get_scoring_algorithms():
    """
    获取可用的评分算法
    
    Returns:
        评分算法列表
    """
    from ..schemas import ScoringAlgorithm
    
    algorithms = []
    
    for algorithm in ScoringAlgorithm:
        algorithm_info = {
            "name": algorithm.value,
            "description": get_algorithm_description(algorithm),
            "parameters": get_algorithm_parameters(algorithm),
            "suitable_for": get_algorithm_suitability(algorithm)
        }
        algorithms.append(algorithm_info)
    
    return {
        "algorithms": algorithms,
        "count": len(algorithms),
        "default_algorithm": ScoringAlgorithm.BASIC.value
    }


@router.get("/weights")
async def get_scoring_weights():
    """
    获取评分权重配置
    
    Returns:
        评分权重配置
    """
    from config import settings
    
    return {
        "quality_weights": settings.SCORE_WEIGHTS["quality"],
        "innovation_weights": settings.SCORE_WEIGHTS["innovation"],
        "feasibility_weights": settings.SCORE_WEIGHTS["feasibility"],
        "business_value_weights": settings.SCORE_WEIGHTS["business_value"],
        "note": "权重总和应为1.0，可在评分请求中自定义权重"
    }


# 辅助函数
def get_algorithm_description(algorithm):
    """获取算法描述"""
    descriptions = {
        "basic": "基础评分算法，基于规则和加权平均",
        "advanced": "高级评分算法，结合机器学习和规则引擎",
        "ml_based": "基于机器学习的评分算法，使用训练好的模型"
    }
    return descriptions.get(algorithm.value, "未知算法")


def get_algorithm_parameters(algorithm):
    """获取算法参数"""
    parameters = {
        "basic": {
            "weights": "可自定义",
            "thresholds": "固定",
            "complexity": "低"
        },
        "advanced": {
            "weights": "可自定义",
            "thresholds": "动态调整",
            "complexity": "中",
            "ml_components": "部分"
        },
        "ml_based": {
            "weights": "模型学习",
            "thresholds": "模型决定",
            "complexity": "高",
            "ml_components": "全部"
        }
    }
    return parameters.get(algorithm.value, {})


def get_algorithm_suitability(algorithm):
    """获取算法适用性"""
    suitability = {
        "basic": ["简单项目", "快速评估", "资源有限"],
        "advanced": ["复杂项目", "需要详细分析", "有历史数据"],
        "ml_based": ["大规模评估", "需要预测", "有训练数据"]
    }
    return suitability.get(algorithm.value, [])