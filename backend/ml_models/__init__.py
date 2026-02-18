"""
机器学习模型模块
"""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
from config import settings

logger = logging.getLogger(__name__)

# 导入各子模块
from .project_classifier import ProjectClassifier
from .tech_stack_analyzer import TechStackAnalyzer
from .feature_extractor import FeatureExtractor
from .nlp_processor import NLPProcessor

# 全局模型实例
_project_classifier = None
_tech_stack_analyzer = None
_feature_extractor = None
_nlp_processor = None


async def load_models():
    """加载所有机器学习模型"""
    global _project_classifier, _tech_stack_analyzer, _feature_extractor, _nlp_processor
    
    try:
        logger.info("开始加载机器学习模型...")
        
        # 加载NLP处理器
        _nlp_processor = NLPProcessor()
        await _nlp_processor.load_model()
        logger.info("NLP处理器加载完成")
        
        # 加载特征提取器
        _feature_extractor = FeatureExtractor()
        await _feature_extractor.load_model()
        logger.info("特征提取器加载完成")
        
        # 加载项目分类器
        _project_classifier = ProjectClassifier()
        await _project_classifier.load_model()
        logger.info("项目分类器加载完成")
        
        # 加载技术栈分析器
        _tech_stack_analyzer = TechStackAnalyzer()
        await _tech_stack_analyzer.load_model()
        logger.info("技术栈分析器加载完成")
        
        logger.info("所有机器学习模型加载完成")
        
    except Exception as e:
        logger.error(f"加载模型失败: {e}")
        raise


async def analyze_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析项目
    
    Args:
        project_data: 项目数据
        
    Returns:
        分析结果
    """
    try:
        # 确保模型已加载
        if not all([_project_classifier, _tech_stack_analyzer, _feature_extractor, _nlp_processor]):
            await load_models()
        
        # 提取项目特征
        features = await _feature_extractor.extract_features(project_data)
        
        # 项目分类
        category_result = await _project_classifier.predict(project_data)
        
        # 技术栈分析
        tech_analysis = await _tech_stack_analyzer.analyze_tech_stack(project_data)
        
        # NLP分析（如果有描述）
        nlp_analysis = {}
        if project_data.get("description"):
            nlp_analysis = await _nlp_processor.analyze_text(project_data["description"])
        
        # 组合分析结果
        analysis_result = {
            "category": category_result,
            "tech_stack_analysis": tech_analysis,
            "features": features,
            "nlp_analysis": nlp_analysis,
            "complexity_score": calculate_complexity_score(features, tech_analysis),
            "maturity_score": calculate_maturity_score(features, tech_analysis),
            "risk_assessment": assess_risks(features, tech_analysis),
            "recommendations": generate_recommendations(features, tech_analysis, category_result),
            "model_versions": {
                "classifier": _project_classifier.version if _project_classifier else "unknown",
                "tech_analyzer": _tech_stack_analyzer.version if _tech_stack_analyzer else "unknown",
                "feature_extractor": _feature_extractor.version if _feature_extractor else "unknown",
                "nlp_processor": _nlp_processor.version if _nlp_processor else "unknown"
            }
        }
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"项目分析失败: {e}")
        # 返回基础分析结果
        return {
            "category": {"name": "unknown", "confidence": 0.0},
            "tech_stack_analysis": {"detected_tech": [], "confidence": 0.0},
            "features": {},
            "nlp_analysis": {},
            "complexity_score": 50.0,
            "maturity_score": 50.0,
            "risk_assessment": {"level": "medium", "factors": []},
            "recommendations": ["分析过程中出现错误"],
            "model_versions": {"classifier": "error", "tech_analyzer": "error"},
            "error": str(e)
        }


async def classify_project(project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    分类项目
    
    Args:
        project_data: 项目数据
        
    Returns:
        分类结果
    """
    try:
        if not _project_classifier:
            await load_models()
        
        return await _project_classifier.predict(project_data)
        
    except Exception as e:
        logger.error(f"项目分类失败: {e}")
        return None


async def analyze_tech_stack(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析技术栈
    
    Args:
        project_data: 项目数据
        
    Returns:
        技术栈分析结果
    """
    try:
        if not _tech_stack_analyzer:
            await load_models()
        
        return await _tech_stack_analyzer.analyze_tech_stack(project_data)
        
    except Exception as e:
        logger.error(f"技术栈分析失败: {e}")
        return {"detected_tech": [], "confidence": 0.0, "error": str(e)}


async def extract_features(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取项目特征
    
    Args:
        project_data: 项目数据
        
    Returns:
        特征字典
    """
    try:
        if not _feature_extractor:
            await load_models()
        
        return await _feature_extractor.extract_features(project_data)
        
    except Exception as e:
        logger.error(f"特征提取失败: {e}")
        return {}


def calculate_complexity_score(features: Dict[str, Any], tech_analysis: Dict[str, Any]) -> float:
    """计算复杂度评分"""
    try:
        score = 50.0  # 基础分
        
        # 基于技术栈多样性
        tech_count = len(tech_analysis.get("detected_tech", []))
        score += min(tech_count * 5, 25)  # 每项技术+5分，最多+25分
        
        # 基于项目规模（如果有）
        if "project_size" in features:
            size = features["project_size"]
            if size > 1000:
                score += 15
            elif size > 500:
                score += 10
            elif size > 100:
                score += 5
        
        # 基于架构复杂度
        if "architecture_complexity" in features:
            complexity = features["architecture_complexity"]
            score += complexity * 10
        
        return min(max(score, 0), 100)
        
    except Exception as e:
        logger.error(f"计算复杂度评分失败: {e}")
        return 50.0


def calculate_maturity_score(features: Dict[str, Any], tech_analysis: Dict[str, Any]) -> float:
    """计算成熟度评分"""
    try:
        score = 50.0  # 基础分
        
        # 基于技术栈成熟度
        tech_maturity = tech_analysis.get("tech_maturity", 0.5)
        score += (tech_maturity - 0.5) * 40  # 调整范围
        
        # 基于文档完整性
        if "documentation_score" in features:
            doc_score = features["documentation_score"]
            score += (doc_score - 0.5) * 20
        
        # 基于测试覆盖率
        if "test_coverage" in features:
            test_score = features["test_coverage"]
            score += (test_score - 0.5) * 20
        
        return min(max(score, 0), 100)
        
    except Exception as e:
        logger.error(f"计算成熟度评分失败: {e}")
        return 50.0


def assess_risks(features: Dict[str, Any], tech_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """风险评估"""
    try:
        risks = []
        risk_level = "low"
        
        # 技术栈风险
        outdated_tech = tech_analysis.get("outdated_technologies", [])
        if outdated_tech:
            risks.append(f"使用了过时技术: {', '.join(outdated_tech)}")
            risk_level = "medium"
        
        # 依赖风险
        dependency_count = len(tech_analysis.get("dependencies", []))
        if dependency_count > 50:
            risks.append(f"依赖过多 ({dependency_count}个)")
            risk_level = "medium"
        
        # 安全风险
        if "security_issues" in features:
            security_issues = features["security_issues"]
            if security_issues > 0:
                risks.append(f"存在安全漏洞: {security_issues}个")
                risk_level = "high"
        
        # 维护风险
        if "maintenance_score" in features:
            maintenance = features["maintenance_score"]
            if maintenance < 0.3:
                risks.append("维护困难")
                risk_level = "medium"
        
        return {
            "level": risk_level,
            "factors": risks,
            "outdated_technologies": outdated_tech,
            "dependency_count": dependency_count
        }
        
    except Exception as e:
        logger.error(f"风险评估失败: {e}")
        return {"level": "unknown", "factors": ["评估失败"], "error": str(e)}


def generate_recommendations(
    features: Dict[str, Any], 
    tech_analysis: Dict[str, Any], 
    category_result: Dict[str, Any]
) -> List[str]:
    """生成建议"""
    try:
        recommendations = []
        
        # 基于分类的建议
        category = category_result.get("name", "")
        if category == "web_development":
            recommendations.append("考虑使用现代前端框架如React或Vue.js")
            recommendations.append("实施响应式设计以支持移动设备")
        elif category == "machine_learning":
            recommendations.append("考虑使用PyTorch或TensorFlow进行模型开发")
            recommendations.append("添加模型评估和监控机制")
        
        # 基于技术栈的建议
        outdated_tech = tech_analysis.get("outdated_technologies", [])
        for tech in outdated_tech:
            recommendations.append(f"考虑升级或替换过时技术: {tech}")
        
        # 基于特征的通用建议
        if "documentation_score" in features and features["documentation_score"] < 0.5:
            recommendations.append("加强文档编写，特别是API文档和部署指南")
        
        if "test_coverage" in features and features["test_coverage"] < 0.3:
            recommendations.append("增加测试覆盖率，特别是单元测试和集成测试")
        
        if "security_issues" in features and features["security_issues"] > 0:
            recommendations.append("立即修复发现的安全漏洞")
        
        # 确保至少有3条建议
        if len(recommendations) < 3:
            generic_recommendations = [
                "实施持续集成/持续部署(CI/CD)流程",
                "添加性能监控和日志记录",
                "定期进行代码审查和重构",
                "考虑容器化部署以提高可移植性"
            ]
            recommendations.extend(generic_recommendations[:3 - len(recommendations)])
        
        return recommendations[:10]  # 最多返回10条建议
        
    except Exception as e:
        logger.error(f"生成建议失败: {e}")
        return ["系统分析中，请稍后查看详细建议"]


# 导出函数
__all__ = [
    "load_models",
    "analyze_project",
    "classify_project",
    "analyze_tech_stack",
    "extract_features",
    "ProjectClassifier",
    "TechStackAnalyzer",
    "FeatureExtractor",
    "NLPProcessor"
]