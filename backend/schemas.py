"""
数据模型（Pydantic schemas）
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# 枚举类型
class ProjectStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    SCORED = "scored"
    ARCHIVED = "archived"


class ScoringAlgorithm(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    ML_BASED = "ml_based"


# 请求模型
class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, max_length=5000, description="项目描述")
    category: Optional[str] = Field(None, max_length=100, description="项目分类")
    tech_stack: Optional[List[str]] = Field(default_factory=list, description="技术栈")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    @validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("项目名称不能为空")
        return v.strip()


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, max_length=5000, description="项目描述")
    category: Optional[str] = Field(None, max_length=100, description="项目分类")
    tech_stack: Optional[List[str]] = Field(None, description="技术栈")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")
    
    @validator("name")
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("项目名称不能为空")
        return v.strip() if v else v


class ScoringRequest(BaseModel):
    """评分请求"""
    project_id: int = Field(..., description="项目ID")
    algorithm: ScoringAlgorithm = Field(ScoringAlgorithm.BASIC, description="评分算法")
    weights: Optional[Dict[str, float]] = Field(None, description="评分权重")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="评分选项")
    
    @validator("weights")
    def validate_weights(cls, v):
        if v:
            total = sum(v.values())
            if abs(total - 1.0) > 0.01:  # 允许1%的误差
                raise ValueError("权重总和必须为1")
        return v


class BatchScoringRequest(BaseModel):
    """批量评分请求"""
    project_ids: List[int] = Field(..., min_items=1, max_items=100, description="项目ID列表")
    algorithm: ScoringAlgorithm = Field(ScoringAlgorithm.BASIC, description="评分算法")
    weights: Optional[Dict[str, float]] = Field(None, description="评分权重")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="评分选项")


class AnalysisRequest(BaseModel):
    """分析请求"""
    project_data: Dict[str, Any] = Field(..., description="项目数据")
    analysis_type: str = Field("full", description="分析类型")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="分析选项")


# 响应模型
class ScoringResult(BaseModel):
    """评分结果"""
    quality_score: float = Field(..., ge=0, le=100, description="质量评分")
    innovation_score: float = Field(..., ge=0, le=100, description="创新性评分")
    feasibility_score: float = Field(..., ge=0, le=100, description="可行性评分")
    business_value_score: float = Field(..., ge=0, le=100, description="商业价值评分")
    overall_score: float = Field(..., ge=0, le=100, description="综合评分")
    scoring_details: Dict[str, Any] = Field(default_factory=dict, description="评分详情")
    algorithm_version: str = Field(..., description="算法版本")


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int = Field(..., description="项目ID")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    category: Optional[str] = Field(None, description="项目分类")
    tech_stack: Optional[List[str]] = Field(default_factory=list, description="技术栈")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    # 评分字段
    quality_score: Optional[float] = Field(None, description="质量评分")
    innovation_score: Optional[float] = Field(None, description="创新性评分")
    feasibility_score: Optional[float] = Field(None, description="可行性评分")
    business_value_score: Optional[float] = Field(None, description="商业价值评分")
    overall_score: Optional[float] = Field(None, description="综合评分")
    
    # 状态和时间
    status: ProjectStatus = Field(..., description="项目状态")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="分析结果")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    analyzed_at: Optional[datetime] = Field(None, description="分析时间")
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    projects: List[ProjectResponse] = Field(..., description="项目列表")
    total: int = Field(..., description="总数")
    skip: int = Field(0, description="跳过的记录数")
    limit: int = Field(100, description="返回的记录数")


class ScoringResponse(BaseModel):
    """评分响应"""
    project_id: int = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    scoring_result: ScoringResult = Field(..., description="评分结果")
    created_at: datetime = Field(..., description="评分时间")


class BatchScoringResponse(BaseModel):
    """批量评分响应"""
    results: List[ScoringResponse] = Field(..., description="评分结果列表")
    failed_projects: List[int] = Field(default_factory=list, description="失败的项目ID")
    total: int = Field(..., description="总项目数")
    success: int = Field(..., description="成功数")


class AnalysisResult(BaseModel):
    """分析结果"""
    project_id: Optional[int] = Field(None, description="项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    category: Optional[str] = Field(None, description="分类结果")
    tech_stack_analysis: Dict[str, Any] = Field(default_factory=dict, description="技术栈分析")
    complexity_score: float = Field(..., ge=0, le=100, description="复杂度评分")
    maturity_score: float = Field(..., ge=0, le=100, description="成熟度评分")
    risk_assessment: Dict[str, Any] = Field(default_factory=dict, description="风险评估")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    analysis_timestamp: datetime = Field(..., description="分析时间")


class CategoryInfo(BaseModel):
    """分类信息"""
    name: str = Field(..., description="分类名称")
    description: str = Field(..., description="分类描述")
    example_projects: List[str] = Field(default_factory=list, description="示例项目")
    average_score: Optional[float] = Field(None, description="平均评分")
    project_count: int = Field(0, description="项目数量")


class TechStackInfo(BaseModel):
    """技术栈信息"""
    name: str = Field(..., description="技术名称")
    category: str = Field(..., description="技术类别")
    popularity_score: float = Field(..., description="流行度评分")
    project_count: int = Field(0, description="使用项目数量")
    average_project_score: Optional[float] = Field(None, description="项目平均评分")


class StatisticsResponse(BaseModel):
    """统计响应"""
    total_projects: int = Field(..., description="总项目数")
    projects_by_category: Dict[str, int] = Field(..., description="按分类统计")
    projects_by_status: Dict[str, int] = Field(..., description="按状态统计")
    average_score: Optional[float] = Field(None, description="平均评分")
    score_distribution: Dict[str, int] = Field(default_factory=dict, description="评分分布")
    top_technologies: List[TechStackInfo] = Field(default_factory=list, description="热门技术")
    top_categories: List[CategoryInfo] = Field(default_factory=list, description="热门分类")
    scoring_history_trend: List[Dict[str, Any]] = Field(default_factory=list, description="评分趋势")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: bool = Field(True, description="是否错误")
    code: int = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="错误详情")
    path: Optional[str] = Field(None, description="请求路径")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = Field(True, description="是否成功")
    message: str = Field(..., description="成功消息")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


# 内部使用模型
class ProjectAnalysisData(BaseModel):
    """项目分析数据"""
    name: str
    description: Optional[str]
    category: Optional[str]
    tech_stack: List[str]
    metadata: Dict[str, Any]
    source: Optional[str] = "user_input"


class MLFeatureVector(BaseModel):
    """机器学习特征向量"""
    features: Dict[str, float]
    feature_names: List[str]
    normalized: bool = False


class ScoringFeatures(BaseModel):
    """评分特征"""
    project_size: float  # 项目规模
    tech_stack_diversity: float  # 技术栈多样性
    code_complexity: float  # 代码复杂度
    documentation_completeness: float  # 文档完整性
    test_coverage: float  # 测试覆盖率
    architecture_quality: float  # 架构质量
    innovation_level: float  # 创新水平
    market_demand: float  # 市场需求
    implementation_difficulty: float  # 实施难度
    resource_requirements: float  # 资源需求
    
    class Config:
        validate_assignment = True


class ModelPrediction(BaseModel):
    """模型预测结果"""
    category: str
    confidence: float
    category_probabilities: Dict[str, float]
    features_used: List[str]


# 配置相关模型
class ScoringWeightConfig(BaseModel):
    """评分权重配置"""
    quality: float = Field(0.25, ge=0, le=1, description="质量权重")
    innovation: float = Field(0.25, ge=0, le=1, description="创新性权重")
    feasibility: float = Field(0.25, ge=0, le=1, description="可行性权重")
    business_value: float = Field(0.25, ge=0, le=1, description="商业价值权重")
    
    @validator("*")
    def validate_weights(cls, v, field):
        if v < 0 or v > 1:
            raise ValueError(f"{field.name}必须在0到1之间")
        return v


class AlgorithmConfig(BaseModel):
    """算法配置"""
    name: str
    version: str
    parameters: Dict[str, Any]
    enabled: bool = True
    description: Optional[str] = None