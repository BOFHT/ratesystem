"""
评分算法模块
智能评分计算逻辑
"""

import logging
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..schemas import ScoringAlgorithm, ScoringResult, ScoringWeightConfig
from ..ml_models import analyze_project
from config import settings

logger = logging.getLogger(__name__)


class ScoringDimension(str, Enum):
    """评分维度"""
    QUALITY = "quality"
    INNOVATION = "innovation" 
    FEASIBILITY = "feasibility"
    BUSINESS_VALUE = "business_value"


class BaseScoringAlgorithm:
    """基础评分算法"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.name = "base"
        
    async def calculate_score(self, project_data: Dict[str, Any], 
                            analysis_result: Dict[str, Any]) -> ScoringResult:
        """计算评分"""
        try:
            # 提取特征
            features = analysis_result.get("features", {})
            
            # 计算各维度分数
            quality_score = self._calculate_quality_score(features, analysis_result)
            innovation_score = self._calculate_innovation_score(features, analysis_result)
            feasibility_score = self._calculate_feasibility_score(features, analysis_result)
            business_value_score = self._calculate_business_value_score(features, analysis_result)
            
            # 计算综合评分（默认权重）
            overall_score = self._calculate_overall_score(
                quality_score, innovation_score, feasibility_score, business_value_score
            )
            
            return ScoringResult(
                quality_score=quality_score,
                innovation_score=innovation_score,
                feasibility_score=feasibility_score,
                business_value_score=business_value_score,
                overall_score=overall_score,
                scoring_details={
                    "algorithm": self.name,
                    "version": self.version,
                    "features_used": list(features.keys()),
                    "category": analysis_result.get("category", {}),
                    "timestamp": datetime.utcnow().isoformat()
                },
                algorithm_version=self.version
            )
            
        except Exception as e:
            logger.error(f"基础评分算法计算失败: {e}")
            # 返回默认评分
            return self._get_default_score()
    
    def _calculate_quality_score(self, features: Dict[str, Any], 
                               analysis_result: Dict[str, Any]) -> float:
        """计算质量评分"""
        try:
            score = 50.0  # 基础分
            
            # 1. 代码质量
            if "quality_score_code" in features:
                code_score = features["quality_score_code"] * 20  # 最多20分
                score += code_score
            
            # 2. 架构质量
            if "quality_score_architecture" in features:
                arch_score = features["quality_score_architecture"] * 15  # 最多15分
                score += arch_score
            
            # 3. 文档完整性
            if "quality_score_documentation" in features:
                doc_score = features["quality_score_documentation"] * 10  # 最多10分
                score += doc_score
            
            # 4. 测试覆盖率
            if "quality_score_testing" in features:
                test_score = features["quality_score_testing"] * 10  # 最多10分
                score += test_score
            
            # 5. 安全性
            if "quality_score_security" in features:
                security_score = features["quality_score_security"] * 5  # 最多5分
                score += security_score
            
            # 6. 技术栈成熟度
            tech_maturity = analysis_result.get("tech_stack_analysis", {}).get("analysis", {}).get("maturity", 0.5)
            score += (tech_maturity - 0.5) * 20  # 调整范围
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.error(f"计算质量评分失败: {e}")
            return 50.0
    
    def _calculate_innovation_score(self, features: Dict[str, Any],
                                  analysis_result: Dict[str, Any]) -> float:
        """计算创新性评分"""
        try:
            score = 50.0  # 基础分
            
            # 1. 创新关键词
            if "innovation_score_novelty" in features:
                novelty_score = features["innovation_score_novelty"] * 25  # 最多25分
                score += novelty_score
            
            # 2. 技术先进性
            if "innovation_score_complexity" in features:
                complexity_score = features["innovation_score_complexity"] * 20  # 最多20分
                score += complexity_score
            
            # 3. 自动化程度
            if "innovation_score_automation" in features:
                automation_score = features["innovation_score_automation"] * 15  # 最多15分
                score += automation_score
            
            # 4. 项目分类创新性权重
            category = analysis_result.get("category", {}).get("name", "")
            innovation_categories = ["machine_learning", "iot", "blockchain", "game_development"]
            if category in innovation_categories:
                score += 10  # 创新领域加分
            
            # 5. 技术栈新颖度
            outdated_tech = analysis_result.get("tech_stack_analysis", {}).get("analysis", {}).get("outdated_technologies", [])
            if not outdated_tech:
                score += 5  # 没有过时技术加分
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.error(f"计算创新性评分失败: {e}")
            return 50.0
    
    def _calculate_feasibility_score(self, features: Dict[str, Any],
                                   analysis_result: Dict[str, Any]) -> float:
        """计算可行性评分"""
        try:
            score = 50.0  # 基础分
            
            # 1. 项目复杂度（越低越好）
            complexity = features.get("overall_complexity", 0.5)
            score -= (complexity - 0.5) * 30  # 复杂度越高，可行性越低
            
            # 2. 技术可行性
            tech_feasibility = analysis_result.get("tech_stack_analysis", {}).get("analysis", {}).get("maturity", 0.5)
            score += (tech_feasibility - 0.5) * 25  # 技术越成熟，可行性越高
            
            # 3. 资源需求（越低越好）
            if "project_size" in features:
                size = features["project_size"]
                if size == 3:  # 大型项目
                    score -= 15
                elif size == 2:  # 中型项目
                    score -= 5
            
            # 4. 风险评估
            risk_level = analysis_result.get("risk_assessment", {}).get("level", "medium")
            if risk_level == "high":
                score -= 20
            elif risk_level == "medium":
                score -= 10
            elif risk_level == "low":
                score += 5
            
            # 5. 维护性
            if "maintainability_score" in features:
                maintain_score = features["maintainability_score"] * 15  # 最多15分
                score += maintain_score
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.error(f"计算可行性评分失败: {e}")
            return 50.0
    
    def _calculate_business_value_score(self, features: Dict[str, Any],
                                      analysis_result: Dict[str, Any]) -> float:
        """计算商业价值评分"""
        try:
            score = 50.0  # 基础分
            
            # 1. 商业关键词
            if "business_score_market" in features:
                market_score = features["business_score_market"] * 25  # 最多25分
                score += market_score
            
            # 2. 用户需求
            if "business_score_user" in features:
                user_score = features["business_score_user"] * 20  # 最多20分
                score += user_score
            
            # 3. 可扩展性
            if "business_score_scale" in features:
                scale_score = features["business_score_scale"] * 15  # 最多15分
                score += scale_score
            
            # 4. 项目分类的商业价值权重
            category = analysis_result.get("category", {}).get("name", "")
            business_categories = ["web_development", "mobile_app", "data_science", "cloud_infrastructure"]
            if category in business_categories:
                score += 10  # 商业价值高的领域加分
            
            # 5. 创新潜力
            if "innovation_potential" in features:
                innovation_potential = features["innovation_potential"] * 10  # 最多10分
                score += innovation_potential
            
            # 6. 文本情感分析
            sentiment = analysis_result.get("nlp_analysis", {}).get("sentiment", {}).get("score", 0)
            score += sentiment * 10  # 情感分数影响商业价值
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.error(f"计算商业价值评分失败: {e}")
            return 50.0
    
    def _calculate_overall_score(self, quality: float, innovation: float,
                               feasibility: float, business_value: float,
                               weights: Optional[Dict[str, float]] = None) -> float:
        """计算综合评分"""
        try:
            # 使用默认权重或自定义权重
            if weights:
                weight_quality = weights.get("quality", 0.25)
                weight_innovation = weights.get("innovation", 0.25)
                weight_feasibility = weights.get("feasibility", 0.25)
                weight_business = weights.get("business_value", 0.25)
            else:
                # 默认权重
                weight_quality = 0.25
                weight_innovation = 0.25
                weight_feasibility = 0.25
                weight_business = 0.25
            
            # 加权平均
            overall = (
                quality * weight_quality +
                innovation * weight_innovation +
                feasibility * weight_feasibility +
                business_value * weight_business
            )
            
            return round(overall, 2)
            
        except Exception as e:
            logger.error(f"计算综合评分失败: {e}")
            # 简单平均作为后备
            return round((quality + innovation + feasibility + business_value) / 4, 2)
    
    def _get_default_score(self) -> ScoringResult:
        """获取默认评分"""
        return ScoringResult(
            quality_score=50.0,
            innovation_score=50.0,
            feasibility_score=50.0,
            business_value_score=50.0,
            overall_score=50.0,
            scoring_details={
                "algorithm": self.name,
                "version": self.version,
                "error": "评分计算失败，使用默认值",
                "timestamp": datetime.utcnow().isoformat()
            },
            algorithm_version=self.version
        )


class AdvancedScoringAlgorithm(BaseScoringAlgorithm):
    """高级评分算法"""
    
    def __init__(self):
        super().__init__()
        self.version = "2.0.0"
        self.name = "advanced"
    
    async def calculate_score(self, project_data: Dict[str, Any],
                            analysis_result: Dict[str, Any]) -> ScoringResult:
        """高级评分计算"""
        try:
            # 先获取基础评分
            base_result = await super().calculate_score(project_data, analysis_result)
            
            # 应用高级调整
            adjusted_result = self._apply_advanced_adjustments(base_result, analysis_result)
            
            return adjusted_result
            
        except Exception as e:
            logger.error(f"高级评分算法计算失败: {e}")
            return await super().calculate_score(project_data, analysis_result)
    
    def _apply_advanced_adjustments(self, base_result: ScoringResult,
                                  analysis_result: Dict[str, Any]) -> ScoringResult:
        """应用高级调整"""
        try:
            adjustments = {}
            
            # 1. 基于技术栈多样性的调整
            tech_diversity = analysis_result.get("tech_stack_analysis", {}).get("analysis", {}).get("diversity", 0.5)
            if tech_diversity > 0.7:
                # 技术栈过于多样，可能增加复杂度
                adjustments["feasibility"] = -5
            elif tech_diversity < 0.3:
                # 技术栈过于单一，可能限制扩展性
                adjustments["innovation"] = -3
                adjustments["business_value"] = -2
            
            # 2. 基于风险评估的调整
            risk_level = analysis_result.get("risk_assessment", {}).get("level", "medium")
            if risk_level == "high":
                adjustments["feasibility"] = adjustments.get("feasibility", 0) - 15
                adjustments["quality"] = adjustments.get("quality", 0) - 10
            elif risk_level == "low":
                adjustments["feasibility"] = adjustments.get("feasibility", 0) + 5
            
            # 3. 基于项目规模的调整
            features = analysis_result.get("features", {})
            project_size = features.get("project_size", 0)
            if project_size == 3:  # 大型项目
                adjustments["feasibility"] = adjustments.get("feasibility", 0) - 10
                adjustments["business_value"] = adjustments.get("business_value", 0) + 5
            elif project_size == 1:  # 小型项目
                adjustments["feasibility"] = adjustments.get("feasibility", 0) + 5
                adjustments["innovation"] = adjustments.get("innovation", 0) - 3
            
            # 4. 基于文本情感的调整
            sentiment_score = analysis_result.get("nlp_analysis", {}).get("sentiment", {}).get("score", 0)
            if sentiment_score > 0.2:
                adjustments["business_value"] = adjustments.get("business_value", 0) + 3
            elif sentiment_score < -0.2:
                adjustments["quality"] = adjustments.get("quality", 0) - 5
            
            # 应用调整
            quality = max(0, min(100, base_result.quality_score + adjustments.get("quality", 0)))
            innovation = max(0, min(100, base_result.innovation_score + adjustments.get("innovation", 0)))
            feasibility = max(0, min(100, base_result.feasibility_score + adjustments.get("feasibility", 0)))
            business_value = max(0, min(100, base_result.business_value_score + adjustments.get("business_value", 0)))
            
            # 重新计算综合评分
            overall = self._calculate_overall_score(quality, innovation, feasibility, business_value)
            
            # 更新评分详情
            scoring_details = base_result.scoring_details.copy()
            scoring_details.update({
                "advanced_adjustments": adjustments,
                "adjusted_scores": {
                    "quality": quality,
                    "innovation": innovation,
                    "feasibility": feasibility,
                    "business_value": business_value
                }
            })
            
            return ScoringResult(
                quality_score=quality,
                innovation_score=innovation,
                feasibility_score=feasibility,
                business_value_score=business_value,
                overall_score=overall,
                scoring_details=scoring_details,
                algorithm_version=self.version
            )
            
        except Exception as e:
            logger.error(f"应用高级调整失败: {e}")
            return base_result


class MLBasedScoringAlgorithm(BaseScoringAlgorithm):
    """基于机器学习的评分算法"""
    
    def __init__(self):
        super().__init__()
        self.version = "3.0.0"
        self.name = "ml_based"
        self.ml_model = None
    
    async def load_model(self):
        """加载机器学习模型"""
        try:
            # 这里可以加载训练好的ML模型
            # 实际实现中应该从文件加载
            logger.info("ML评分模型加载完成")
            self.ml_model = {"loaded": True}
            
        except Exception as e:
            logger.error(f"加载ML模型失败: {e}")
            self.ml_model = None
    
    async def calculate_score(self, project_data: Dict[str, Any],
                            analysis_result: Dict[str, Any]) -> ScoringResult:
        """ML评分计算"""
        try:
            if self.ml_model is None:
                await self.load_model()
            
            # 提取ML特征
            ml_features = self._extract_ml_features(project_data, analysis_result)
            
            # 模拟ML预测（实际实现中应该调用模型）
            # 这里使用规则引擎作为后备
            if self.ml_model:
                # 模拟ML预测结果
                ml_scores = self._simulate_ml_prediction(ml_features)
            else:
                # 回退到高级算法
                advanced_algo = AdvancedScoringAlgorithm()
                base_result = await advanced_algo.calculate_score(project_data, analysis_result)
                ml_scores = {
                    "quality": base_result.quality_score,
                    "innovation": base_result.innovation_score,
                    "feasibility": base_result.feasibility_score,
                    "business_value": base_result.business_value_score
                }
            
            # 计算综合评分
            overall = self._calculate_overall_score(
                ml_scores["quality"],
                ml_scores["innovation"],
                ml_scores["feasibility"],
                ml_scores["business_value"]
            )
            
            return ScoringResult(
                quality_score=ml_scores["quality"],
                innovation_score=ml_scores["innovation"],
                feasibility_score=ml_scores["feasibility"],
                business_value_score=ml_scores["business_value"],
                overall_score=overall,
                scoring_details={
                    "algorithm": self.name,
                    "version": self.version,
                    "ml_features": ml_features,
                    "model_used": "simulated_ml_model",
                    "timestamp": datetime.utcnow().isoformat()
                },
                algorithm_version=self.version
            )
            
        except Exception as e:
            logger.error(f"ML评分算法计算失败: {e}")
            # 回退到高级算法
            advanced_algo = AdvancedScoringAlgorithm()
            return await advanced_algo.calculate_score(project_data, analysis_result)
    
    def _extract_ml_features(self, project_data: Dict[str, Any],
                           analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取ML特征"""
        features = analysis_result.get("features", {})
        
        ml_features = {
            # 文本特征
            "text_length": features.get("text_length", 0),
            "vocabulary_size": features.get("vocabulary_size", 0),
            "readability_score": features.get("readability_score", 0),
            
            # 技术特征
            "tech_count": features.get("tech_count", 0),
            "tech_diversity": features.get("tech_diversity", 0),
            "popular_tech_ratio": features.get("popular_tech_ratio", 0),
            
            # 质量特征
            "overall_quality_score": features.get("overall_quality_score", 0),
            "code_quality": features.get("quality_score_code", 0),
            "architecture_quality": features.get("quality_score_architecture", 0),
            
            # 创新特征
            "overall_innovation_score": features.get("overall_innovation_score", 0),
            "novelty_score": features.get("innovation_score_novelty", 0),
            
            # 复杂度特征
            "overall_complexity": features.get("overall_complexity", 0),
            "project_size": features.get("project_size", 0),
            
            # 风险评估
            "risk_level": analysis_result.get("risk_assessment", {}).get("level", "medium"),
            
            # 情感特征
            "sentiment_score": analysis_result.get("nlp_analysis", {}).get("sentiment", {}).get("score", 0),
            
            # 分类特征
            "category": analysis_result.get("category", {}).get("name", "unknown"),
            "category_confidence": analysis_result.get("category", {}).get("confidence", 0)
        }
        
        return ml_features
    
    def _simulate_ml_prediction(self, features: Dict[str, Any]) -> Dict[str, float]:
        """模拟ML预测"""
        try:
            # 模拟ML模型的预测逻辑
            # 实际实现中应该调用真实的ML模型
            
            base_scores = {
                "quality": 50.0,
                "innovation": 50.0,
                "feasibility": 50.0,
                "business_value": 50.0
            }
            
            # 基于特征调整分数
            adjustments = {}
            
            # 文本质量影响
            if features.get("readability_score", 0) > 60:
                adjustments["quality"] = 10
            elif features.get("readability_score", 0) < 30:
                adjustments["quality"] = -5
            
            # 技术栈影响
            if features.get("tech_count", 0) > 5:
                adjustments["feasibility"] = -5
                adjustments["quality"] = -3
            
            # 创新性影响
            if features.get("novelty_score", 0) > 0.5:
                adjustments["innovation"] = 15
            
            # 风险评估影响
            if features.get("risk_level") == "high":
                adjustments["feasibility"] = adjustments.get("feasibility", 0) - 10
            elif features.get("risk_level") == "low":
                adjustments["feasibility"] = adjustments.get("feasibility", 0) + 5
            
            # 应用调整
            for key in base_scores:
                base_scores[key] += adjustments.get(key, 0)
                base_scores[key] = max(0, min(100, base_scores[key]))
            
            return base_scores
            
        except Exception as e:
            logger.error(f"模拟ML预测失败: {e}")
            return {"quality": 50.0, "innovation": 50.0, "feasibility": 50.0, "business_value": 50.0}


# 算法工厂
class ScoringAlgorithmFactory:
    """评分算法工厂"""
    
    @staticmethod
    def create_algorithm(algorithm: ScoringAlgorithm) -> BaseScoringAlgorithm:
        """创建评分算法实例"""
        if algorithm == ScoringAlgorithm.BASIC:
            return BaseScoringAlgorithm()
        elif algorithm == ScoringAlgorithm.ADVANCED:
            return AdvancedScoringAlgorithm()
        elif algorithm == ScoringAlgorithm.ML_BASED:
            return MLBasedScoringAlgorithm()
        else:
            logger.warning(f"未知算法类型: {algorithm}, 使用基础算法")
            return BaseScoringAlgorithm()


# 主评分函数
async def calculate_project_score(project, algorithm: ScoringAlgorithm = ScoringAlgorithm.BASIC,
                                weights: Optional[Dict[str, float]] = None,
                                options: Optional[Dict[str, Any]] = None) -> ScoringResult:
    """
    计算项目评分
    
    Args:
        project: 项目对象或数据
        algorithm: 评分算法
        weights: 自定义权重
        options: 评分选项
        
    Returns:
        评分结果
    """
    try:
        # 准备项目数据
        if hasattr(project, '__dict__'):
            # 如果是ORM对象
            project_data = {
                "name": project.name,
                "description": project.description,
                "category": project.category,
                "tech_stack": project.tech_stack,
                "metadata": project.metadata
            }
        else:
            # 如果是字典
            project_data = project
        
        # 分析项目
        analysis_result = await analyze_project(project_data)
        
        # 创建算法实例
        scoring_algo = ScoringAlgorithmFactory.create_algorithm(algorithm)
        
        # 计算评分
        result = await scoring_algo.calculate_score(project_data, analysis_result)
        
        # 应用自定义权重（如果有）
        if weights:
            result.overall_score = scoring_algo._calculate_overall_score(
                result.quality_score,
                result.innovation_score,
                result.feasibility_score,
                result.business_value_score,
                weights
            )
            result.scoring_details["custom_weights"] = weights
        
        # 应用选项（如果有）
        if options:
            result.scoring_details["options"] = options
        
        return result
        
    except Exception as e:
        logger.error(f"计算项目评分失败: {e}")
        # 返回默认评分
        return ScoringResult(
            quality_score=50.0,
            innovation_score=50.0,
            feasibility_score=50.0,
            business_value_score=50.0,
            overall_score=50.0,
            scoring_details={
                "error": str(e),
                "algorithm": "error_fallback",
                "timestamp": datetime.utcnow().isoformat()
            },
            algorithm_version="0.0.0"
        )


async def update_project_scores(db, project_id: int, scoring_result: ScoringResult):
    """
    更新项目评分
    
    Args:
        db: 数据库会话
        project_id: 项目ID
        scoring_result: 评分结果
    """
    try:
        from sqlalchemy import update
        from ..database import Project
        
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(
                quality_score=scoring_result.quality_score,
                innovation_score=scoring_result.innovation_score,
                feasibility_score=scoring_result.feasibility_score,
                business_value_score=scoring_result.business_value_score,
                overall_score=scoring_result.overall_score,
                status="scored",
                analysis_result=scoring_result.scoring_details
            )
        )
        
        logger.info(f"项目 {project_id} 评分已更新: {scoring_result.overall_score}")
        
    except Exception as e:
        logger.error(f"更新项目评分失败: {e}")
        raise


async def batch_score_projects(projects, algorithm: ScoringAlgorithm = ScoringAlgorithm.BASIC,
                             weights: Optional[Dict[str, float]] = None) -> List[ScoringResult]:
    """
    批量评分项目
    
    Args:
        projects: 项目列表
        algorithm: 评分算法
        weights: 自定义权重
        
    Returns:
        评分结果列表
    """
    results = []
    
    for project in projects:
        try:
            result = await calculate_project_score(project, algorithm, weights)
            results.append(result)
        except Exception as e:
            logger.error(f"批量评分项目失败: {e}")
            # 添加错误结果
            results.append(ScoringResult(
                quality_score=0.0,
                innovation_score=0.0,
                feasibility_score=0.0,
                business_value_score=0.0,
                overall_score=0.0,
                scoring_details={
                    "error": str(e),
                    "algorithm": algorithm.value,
                    "timestamp": datetime.utcnow().isoformat()
                },
                algorithm_version="0.0.0"
            ))
    
    return results