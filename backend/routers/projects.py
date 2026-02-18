"""
项目路由
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import uuid

from ..database import get_db, Project, ScoringHistory, ProjectCategory
from ..schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectListResponse, ScoringRequest
)
from ..ml_models import analyze_project, classify_project
from ..scoring import calculate_project_score

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    category: Optional[str] = Query(None, description="项目分类"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="最低评分"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="最高评分"),
    status: Optional[str] = Query(None, description="项目状态"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序")
):
    """
    获取项目列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        category: 项目分类
        min_score: 最低评分
        max_score: 最高评分
        status: 项目状态
        sort_by: 排序字段
        sort_order: 排序顺序
    
    Returns:
        项目列表
    """
    try:
        # 构建查询
        query = select(Project)
        
        # 应用过滤器
        if category:
            query = query.where(Project.category == category)
        
        if min_score is not None:
            query = query.where(Project.overall_score >= min_score)
        
        if max_score is not None:
            query = query.where(Project.overall_score <= max_score)
        
        if status:
            query = query.where(Project.status == status)
        
        # 应用排序
        if hasattr(Project, sort_by):
            order_column = getattr(Project, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            # 默认按创建时间降序
            query = query.order_by(Project.created_at.desc())
        
        # 获取总数
        count_query = select(func.count()).select_from(Project)
        if category:
            count_query = count_query.where(Project.category == category)
        if status:
            count_query = count_query.where(Project.status == status)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        projects = result.scalars().all()
        
        # 转换为响应模型
        project_responses = [
            ProjectResponse.from_orm(project) for project in projects
        ]
        
        return ProjectListResponse(
            projects=project_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取项目列表失败")


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    include_scoring_history: bool = Query(False, description="是否包含评分历史")
):
    """
    获取单个项目详情
    
    Args:
        project_id: 项目ID
        include_scoring_history: 是否包含评分历史
    
    Returns:
        项目详情
    """
    try:
        # 构建查询
        query = select(Project).where(Project.id == project_id)
        
        if include_scoring_history:
            query = query.options(selectinload(Project.scoring_history))
        
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return ProjectResponse.from_orm(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取项目详情失败")


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新项目
    
    Args:
        project_data: 项目数据
    
    Returns:
        创建的项目
    """
    try:
        # 检查项目名称是否已存在
        existing_query = select(Project).where(Project.name == project_data.name)
        existing_result = await db.execute(existing_query)
        existing_project = existing_result.scalar_one_or_none()
        
        if existing_project:
            raise HTTPException(status_code=400, detail="项目名称已存在")
        
        # 创建项目记录
        project = Project(
            name=project_data.name,
            description=project_data.description,
            category=project_data.category,
            tech_stack=project_data.tech_stack,
            metadata=project_data.metadata,
            status="pending"
        )
        
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"创建项目成功: {project.id} - {project.name}")
        
        return ProjectResponse.from_orm(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="创建项目失败")


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新项目信息
    
    Args:
        project_id: 项目ID
        project_data: 更新数据
    
    Returns:
        更新后的项目
    """
    try:
        # 检查项目是否存在
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 更新字段
        update_data = project_data.dict(exclude_unset=True)
        
        # 如果是pending状态，重置评分
        if project_data.status == "pending":
            update_data.update({
                "quality_score": None,
                "innovation_score": None,
                "feasibility_score": None,
                "business_value_score": None,
                "overall_score": None,
                "analysis_result": None,
                "analyzed_at": None
            })
        
        # 执行更新
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(**update_data)
        )
        
        await db.commit()
        
        # 重新获取项目
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        logger.info(f"更新项目成功: {project_id}")
        
        return ProjectResponse.from_orm(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新项目失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="更新项目失败")


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除项目
    
    Args:
        project_id: 项目ID
    """
    try:
        # 检查项目是否存在
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 删除项目
        await db.execute(
            delete(Project).where(Project.id == project_id)
        )
        
        await db.commit()
        
        logger.info(f"删除项目成功: {project_id}")
        
        return {"message": "项目删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除项目失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="删除项目失败")


@router.post("/{project_id}/analyze", response_model=ProjectResponse)
async def analyze_project_endpoint(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    分析项目
    
    Args:
        project_id: 项目ID
    
    Returns:
        分析后的项目
    """
    try:
        # 检查项目是否存在
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 检查是否已分析
        if project.status == "scored":
            return ProjectResponse.from_orm(project)
        
        # 更新状态为分析中
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(status="analyzing")
        )
        
        await db.commit()
        
        # 分析项目
        analysis_result = await analyze_project(project)
        
        # 如果未分类，尝试分类
        if not project.category:
            category = await classify_project(project)
            if category:
                analysis_result["category"] = category
        
        # 更新分析结果
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(
                analysis_result=analysis_result,
                status="analyzed",
                analyzed_at=func.now()
            )
        )
        
        await db.commit()
        
        # 重新获取项目
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        logger.info(f"分析项目成功: {project_id}")
        
        return ProjectResponse.from_orm(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析项目失败: {e}")
        await db.rollback()
        
        # 重置状态
        try:
            await db.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(status="pending")
            )
            await db.commit()
        except:
            pass
        
        raise HTTPException(status_code=500, detail="分析项目失败")


@router.get("/{project_id}/scoring-history")
async def get_scoring_history(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数")
):
    """
    获取项目评分历史
    
    Args:
        project_id: 项目ID
        skip: 跳过的记录数
        limit: 返回的记录数
    
    Returns:
        评分历史列表
    """
    try:
        # 检查项目是否存在
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 获取评分历史
        history_query = (
            select(ScoringHistory)
            .where(ScoringHistory.project_id == project_id)
            .order_by(ScoringHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(history_query)
        history = result.scalars().all()
        
        # 获取总数
        count_query = (
            select(func.count())
            .select_from(ScoringHistory)
            .where(ScoringHistory.project_id == project_id)
        )
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "history": [
                {
                    "id": h.id,
                    "quality_score": h.quality_score,
                    "innovation_score": h.innovation_score,
                    "feasibility_score": h.feasibility_score,
                    "business_value_score": h.business_value_score,
                    "overall_score": h.overall_score,
                    "algorithm_version": h.algorithm_version,
                    "created_at": h.created_at.isoformat()
                }
                for h in history
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评分历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取评分历史失败")